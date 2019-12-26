FROM python:3.7-alpine
RUN apk add --no-cache --update \
    python3 python3-dev gcc bash \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev
RUN pip install --upgrade pip
RUN mkdir /DistributedWorkerSystem
COPY ./requirements.txt /DistributedWorkerSystem/requirements.txt
WORKDIR /DistributedWorkerSystem
RUN pip install -r /DistributedWorkerSystem/requirements.txt
COPY . /DistributedWorkerSystem/

ENV JAVA_HOME=/usr/lib/jvm/default-jvm
ENV PATH="${JAVA_HOME}/bin:${PATH}"
RUN apk add --no-cache openjdk8

CMD ["python", "/DistributedWorkerSystem/distributed_worker/run.py"]