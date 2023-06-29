
import json
import time 
import logging
import socket
from datetime import datetime
from numpy.random import uniform, choice, randn

from random import random as r

import numpy as np
from confluent_kafka import Producer


KAFKA_BROKER = 'broker:9092'
TRANSACTION_TOPIC = 'transactions'
LAG = 0.5
PROBABILITY_OUTLIER = 0.05

def create_producer():
    try:
        producer = Producer({
        "bootstrap.servers":KAFKA_BROKER,
        "client.id": socket.gethostname(),
        "enable.idempotence": True,
        "batch.size": 64000,
        "linger.ms":10,
        "acks": "all",
        "retries": 5,
        "delivery.timeout.ms":1000
        })
    except Exception as e:
        logging.exception("nie mogę utworzyć producenta")
        producer = None
    return producer


_id = 0 
producer = create_producer()

if producer is not None:
    while True:
        if r() <= PROBABILITY_OUTLIER:
            X_test = uniform(low=-4, high=4, size=(1,2))
        else:
            X = 0.3 * randn(1,2)
            X_test = (X + choice(a=[2,-2], size=1, p=[0.5, 0.5]))
        
        X_test = np.round(X_test, 3).tolist()
        
        current_time = datetime.utcnow().isoformat()
        
        record = {
        "id": _id,
        "data": X_test,
        "current_time" : current_time
        }
        
        record = json.dumps(record).encode("utf-8")
        
        producer.produce(topic= TRANSACTION_TOPIC, value=record)
        
        producer.flush()
        _id +=1 
        time.sleep(LAG)
        
