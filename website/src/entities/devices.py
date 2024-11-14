from arduino_iot_cloud import ArduinoCloudClient
from db import create_reading

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
    create_reading(client._sqlid, str(value))

class Device():
    def __init__(self, _id: int, device_id: str, threshold: int, soil_type: int):
        # Parameters given from DB
        self.id = _id
        self.device_id = device_id
        self.threshold = threshold
        self.soil_type = soil_type

class Sensor(Device):
    def __init__(self, _id: int, device_id: str, zone: int):
        self.id = _id
        self.device_id = device_id
        self.zone = zone 

class Hub(Device):
    def __init__(self, _id: int, device_id: str, soil_type_1: int, soil_type_2: int, threshold1: int, threshold2: int):
        self.id = _id
        self.device_id = device_id
        self.soil_types = [soil_type_1, soil_type_2]
        self.thresholds = [threshold1, threshold2]

    