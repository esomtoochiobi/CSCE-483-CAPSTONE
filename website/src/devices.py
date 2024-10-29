from arduino_iot_cloud import ArduinoCloudClient
from db import update_soil_moisture

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
        filename=f"logs/{_id}_{device_type}.txt"
    )   

def on_moist_change(client, value):
    client["moistureLevel"] = value
    update_soil_moisture(client._sqlid, str(value))

class Device():
    def __init__(self, _id: int, device_key: str, device_id: str, device_type: int):
        # Parameters given from DB
        self.id = _id
        self.device_key = device_key.encode('ascii')
        self.device_id = device_id.encode('ascii')
        self.device_type = device_type

class Sensor(Device):
    def __init__(self, _id: int, device_key: str, device_id: str, device_type: int, moisture: int, threshold: int, last_time: str):
        super().__init__(_id, device_key, device_id, device_type)
        self.threshold = threshold
        self.last_time = last_time

        self.client = ArduinoCloudClient(device_id=self.device_id, username=self.device_id, password=self.device_key, sync_mode=True)
        logging_func(self.id, self.device_type)

        self.client._sqlid = _id
        self.client.register('moistureLevel', on_write=on_moist_change, value=None)

    def start(self):
        self.client.start()

    def read(self, key):
        self.client.update()
        return self.client[key]


class Hub(Device):
    def __init__(self, _id: int, device_key: str, device_id: str, device_type: int, water_flow: int):
        super().__init__(_id, device_key, device_id, device_type)
        self.water_flow = water_flow

        self.client = ArduinoCloudClient(device_id=self.device_id, username=self.device_id, password=self.device_key, sync_mode=True)
        logging_func(self.id, self.device_type)

    def start(self):
        self.client.start()

    def read(self, key):
        self.client.update()
        return self.client.get(key)

    