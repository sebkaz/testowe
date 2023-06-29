
import json
import random
import sys
from datetime import datetime, timedelta
from time import sleep

from kafka import KafkaProducer

if __name__ == "__main__":
    SERVER = "broker:9092"

    producer = KafkaProducer(
        bootstrap_servers=[SERVER],
        value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        api_version=(2, 7, 0),
    )
    
    try:
        while True:
            ##### 
            #    YOUR CODE HERE
            message = {
                "time" : str(datetime.now() + timedelta(seconds=random.randint(-15, 0))),
                "id" : random.choice(["a", "b", "c", "d", "e"]),
                "value" : random.randint(0,100),
            }

            #####
            producer.send("streaming", value=message)
            sleep(1)
    except KeyboardInterrupt:
        producer.close()
