from arduino_iot_cloud import ArduinoCloudClient
from dotenv import load_dotenv

import os
import time
import logging

import sys
sys.path.append("lib")

def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )   

def on_moist_change(client, value):
    client["soilMoisture"] = value

load_dotenv()

DEVICE_ID = os.getenv('DEVICE_ID').encode('ascii')
DEVICE_KEY = os.getenv('DEVICE_KEY').encode('ascii')

logging_func()
# client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=DEVICE_KEY)

# client.register('solenoidControl')
# client.register('waterFlow')
# client.register('soilMoisture')

# client['waterFlow'] = 69.421

# client.start()

class Board():
    def __init__(self):
        self.client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=DEVICE_KEY, sync_mode=True)
        logging_func()

        self.client.register('solenoidControl')
        self.client.register('waterFlow')
        self.client.register('soilMoisture', on_write=on_moist_change)

    def start(self):
        self.client.start()

    def read(self, key):
        self.client.update()
        return self.client[key]
