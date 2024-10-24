from arduino_iot_cloud import ArduinoCloudClient
from dotenv import load_dotenv

import os
import time
import logging

import sys
sys.path.append("lib")

def logging_func(_id, device_type):
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
        filename=f"{_id}_{device_type}.txt"
    )   

def on_moist_change(client, value):
    client["soilMoisture"] = value

load_dotenv()

DEVICE_ID = os.getenv('DEVICE_ID').encode('ascii')
DEVICE_KEY = os.getenv('DEVICE_KEY').encode('ascii')

logging_func()

class Device():
    def __init__(self, _id: int, device_key: str, device_id: str, device_type: int):

        # Parameters given from DB
        self.id = _id
        self.device_key = device_key.encode('ascii')
        self.device_id = device_id.encode('ascii')
        self.device_type = device_type

class Sensor(Device):
    def __init__(self, _id: int, device_key:  str, device_id: str, device_type: int, moisture: int, threshold: int):
        super.__init__(_id, device_key, device_id, device_type)
        self.threshold = threshold

        self.client = ArduinoCloudClient(device_id=self.device_id), username=self.device_id, password=self.device_key, sync_mode=True)
        logging_func(self.id, self.device_type)

        self.client.register('soilMoisture', on_write=on_moist_change)
        self.client['soilMoisture'] = moisture


class Hub(Device):
    def __init__(self, _id: int, device_key: str, device_id: str, device_type: int, avg_moisture: float, water_flow: int):
        super.__init__(_id, device_key, device_id, device_type)
        self.avg_moisture = avg_moisture
        self.water_flow = water_flow

        self.client = ArduinoCloudClient(device_id=self.device_id, username=self.device_id, password=self.device_key, sync_mode=True)
        logging_func(self.id, self.device_type)
