import sys,os
sys.path.append(os.getcwd())

from collections import Counter
from datetime import datetime

from flask import request, Flask, jsonify, make_response, abort
from flask.views import MethodView
from distributed_worker.conf import REDIS_HOST
                                     
import redis
import functools
import time

app = Flask(__name__)
redis_conn = redis.StrictRedis(host=REDIS_HOST,decode_responses=True)
redis_pipe = redis_conn.pipeline()


def api_wrapper(f):
    @functools.wraps(f)
    def decorated_function(*args, **kws):
        if request.endpoint in ["RecentItemAPIView","BrandsCountAPIView"]:
            target_date = kws.get('date')
            if target_date is None:
                return make_response(jsonify({'message': 'date parameter is missing'}), 422)
            try:
                url_args = datetime.strptime(target_date, '%Y-%m-%d')
            except ValueError:
                return make_response(jsonify({'message': 'Provider Date in YYYY-MM-DD Format'}), 422)
            response = f(date=url_args)
        if request.endpoint == "ProductColorAPIView":
            try:
                url_args = kws.get('color').lower()
            except AttributeError:
                return make_response(jsonify({'message': 'Invalid parameters'}), 422)
            response = f(color=url_args)    
        json_response = jsonify(response)
        return make_response(json_response,200)
    return decorated_function


class RecentItemAPIView(MethodView):
    decorators = [api_wrapper]

    def get(self,date):
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        unix_start_timestamp = time.mktime(start_datetime.timetuple())
        unix_end_timestamp = time.mktime(end_datetime.timetuple())
        recent_item = redis_conn.zrangebyscore(
            'product_timestamp', int(unix_start_timestamp), int(unix_end_timestamp), withscores=True)[0]
        recent_itemid = recent_item[0]
        product = redis_conn.hgetall(recent_itemid)
        return product
        
class BrandsCountAPIView(MethodView):
    decorators = [api_wrapper]
    
    def get(self,date):
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        unix_start_timestamp = time.mktime(start_datetime.timetuple())
        unix_end_timestamp = time.mktime(end_datetime.timetuple())
        item_ids = redis_conn.zrangebyscore(
            'product_timestamp', int(unix_start_timestamp), int(unix_end_timestamp), withscores=False)
        for item_id in item_ids:
            redis_pipe.hget(item_id, 'shoe_brand')
        brands = redis_pipe.execute()
        return Counter(brands).most_common()

class ProductColorAPIView(MethodView):
    decorators = [api_wrapper]
        
    def get(self,color):
        item_ids = redis_conn.zrevrange(
            color, 0, 9)
        for item_id in item_ids:
            redis_pipe.hgetall(item_id)
        products = redis_pipe.execute()
        return products


def run():
    try:
        if(redis_conn.ping()):
            app.add_url_rule("/api/getRecentItem/<date>", view_func=RecentItemAPIView.as_view("RecentItemAPIView"))
            app.add_url_rule("/api/getBrandsCount/<date>", view_func=BrandsCountAPIView.as_view("BrandsCountAPIView"))
            app.add_url_rule("/api/getItemsbyColor/<color>", view_func=ProductColorAPIView.as_view("ProductColorAPIView"))
            app.run(host="0.0.0.0", debug=True)
    except redis.exceptions.ConnectionError:
        raise Exception("Please make sure redis server is configured and reachable")