
import json
import os
import time 
import numpy as np
import socket
import logging
from datetime import datetime
from joblib import load
from confluent_kafka import Producer, Consumer
from multiprocessing import Process

KAFKA_BROKER = 'broker:9092'
TRANSACTION_TOPIC = 'transactions'
TRANSACTOPM_CG = 'transactions'
ANOMALY_TOPIC = 'anomaly'
NUM_PARTITIONS = 3

MODEL_PATH = os.path.abspath('isolation_forest.joblib')

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

def create_consumer(topic, group_id):
    try:

        consumer = Consumer({
          "bootstrap.servers": KAFKA_BROKER,
          "group.id": group_id,
          "client.id": socket.gethostname(),
          "isolation.level":"read_committed",
          "default.topic.config":{
                    "auto.offset.reset":"latest",
                    "enable.auto.commit": False
            }
            
        })
        consumer.subscribe([topic])
    except Exception as e:
        logging.exception("nie mogę utworzyć konsumenta")
        consumer = None
    
    return consumer
    
def detekcja_anomalii():
    consumer = create_consumer(topic=TRANSACTION_TOPIC, group_id=TRANSACTOPM_CG)
    producer = create_producer()
    clf = load(MODEL_PATH)
    
    while True:
        message = consumer.poll()
        if message is None:
            continue
        if message.error():
            logging.error(f"CONSUMER error: {message.error()}")
            continue
        
        record = json.loads(message.value().decode('utf-8'))
        data = record['data']
        prediction = clf.predict(data)
        
        if prediction[0] == -1 :
            score = clf.score_samples(data)
            record["score"] = np.round(score, 3).tolist()
            
            _id = str(record["id"])
            record = json.dumps(record).encode("utf-8")
            
            producer.produce(topic=ANOMALY_TOPIC, value=record)
            
            producer.flush()
            
    consumer.close()
        

for _ in range(NUM_PARTITIONS):
    p = Process(target=detekcja_anomalii)
    p.start()
                        
                    
