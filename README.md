# Distributed Worker System

A distributed worker system to update data in Redis using Python with Pyspark

  - used spark dataframes to read the csv dataset (https://www.kaggle.com/datafiniti/womens-shoes-prices/), transform it and will insert data into redis parallely
  - used a Redis server to store each of the record
  - Implemented 3 APIs(Restful) to query and fetch data from redis
       - /api/getRecentItem/<date>- return the most recent item added on the given date 
       - /api/getBrandsCount/<date> - return the count of each brands added on the given date in descending order
       - /api/getItemsbyColor/<color> - return the top 10 latest items given input as color

### Steps to setup and run
Project Local Setup
```sh
$ git clone https://github.com/SugumarVenkatesan/DistributedWorkerSystem.git
$ cd DistributedWorkerSystem
```
Kaggle Dataset Extraction
```sh
$ tar -C kaggle_dataset -xzvf kaggle_dataset\kaggle_dataset.zip
```
Build and Run Application using Docker

```sh
$ docker pull redis:latest
$ docker build -t py-spark-redis .
$ docker network create distributed-worker-system
$ docker run -d --net distributed-worker-system --name redis redis
$ docker run -d -p 5000:5000 --net distributed-worker-system --name py-spark-redis -e REDIS_HOST=redis py-spark-redis
```
For RUN logs, use --follow to follow logs continuously
```sh
$ docker logs py-spark-redis
$ docker logs redis
```
Once the API is up and running
- to find the same, follow the py-spark-redis container RUN logs and it would have
    ```
    * Serving Flask app "distributed_worker.api" (lazy loading)
    * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
    * Debug mode: off
    * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
    ```
- Get the docker machine ip incase of windows - use docker-machine ip default or refer https://www.jhipster.tech/tips/020_tip_using_docker_containers_as_localhost_on_mac_and_windows.html to access the API server via localhost

- API endpoints are accessible via http://<docker-machine-ip|0.0.0.0>/api

#### API Endpoint Details
- #### getRecentItem
        Format: /api/getRecentItem/<date> - date format :: YYYY-MM-DD
        Sample 
            Request: api/getRecentItem/2017-02-03
            Response: {
                          colors: "Yellow",
                          date_of_addition: "2017-02-03T22:06:20Z",
                          id: "AVpfGgD5ilAPnD_xU-VH",
                          shoe_brand: "In-Sattva"
                      }

- #### getBrandsCount
        Format: /api/getBrandsCount/<date> - date format :: YYYY-MM-DD
        Sample 
            Request: api/getBrandsCount/2017-02-03
            Response: [
                        [
                            "In-Sattva",
                            9
                        ],
                        [
                            "Novica",
                            8
                        ],
                        [
                            "Birkenstock",
                            2
                        ],
                        [
                            "Journee Collection",
                            2
                        ],
                        [
                            "Moksha Imports",
                            1
                        ],
                        [
                            "Joules",
                            1
                        ],
                        [
                            "Nature Breeze",
                            1
                        ],
                        [
                            "Muk Luks",
                            1
                        ],
                        [
                            "Beston",
                            1
                        ],
                        [
                            "Qupid",
                            1
                        ],
                        [
                            "LILIANA",
                            1
                        ],
                        [
                            "UGG Australia",
                            1
                        ],
                        [
                            "VIA PINKY",
                            1
                        ],
                        [
                            "Sperry",
                            1
                        ],
                        [
                            "Alfani",
                            1
                        ],
                        [
                            "Naturalizer",
                            1
                        ],
                        [
                            "Asics",
                            1
                        ],
                        [
                            "1 World Sarongs",
                            1
                        ]
                    ]

- #### getItemsbyColor
        Format: /api/getItemsbyColor/<color> - color :: string
        Sample 
            Request: api/getRecentItem/2017-02-03
            Response: [
                        {
                            colors: "Blue",
                            date_of_addition: "2019-05-01T05:09:16Z",
                            id: "AWpx3RhnM263mwCq-0YV",
                            shoe_brand: "Unique Bargains"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-05-01T05:07:08Z",
                            id: "AWpx3kulM263mwCq-0ZR",
                            shoe_brand: "City Classified"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-05-01T05:06:07Z",
                            id: "AWpx52ShAGTnQPR7v_fC",
                            shoe_brand: "Unique Bargains"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-05-01T03:00:47Z",
                            id: "AWpxbrFnAGTnQPR7v3Tx",
                            shoe_brand: "UGG"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-30T08:06:26Z",
                            id: "AWptY-z20U_gzG0hjgm4",
                            shoe_brand: "Unique Bargains"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-30T08:02:11Z",
                            id: "AWptWecvM263mwCq-hkg",
                            shoe_brand: "Cape Robbin"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-29T07:11:52Z",
                            id: "AWpoBE120U_gzG0hjKnZ",
                            shoe_brand: "City Classified"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-29T06:24:26Z",
                            id: "AWpn3Tim0U_gzG0hjH3Q",
                            shoe_brand: "ellie"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-28T08:13:34Z",
                            id: "AWpjHPwSAGTnQPR7u6EB",
                            shoe_brand: "X2B"
                        },
                        {
                            colors: "Blue",
                            date_of_addition: "2019-04-28T08:09:02Z",
                            id: "AWpjDXnp0U_gzG0hisSc",
                            shoe_brand: "UGG"
                        }
                    ]
