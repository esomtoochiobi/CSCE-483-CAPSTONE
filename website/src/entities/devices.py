import os

class Sensor():
    def __init__(self, _id: int, device_id: str, zone: int):
        self.id = _id
        self.device_id = device_id
        self.zone = zone 

class Hub():
    def __init__(self, _id: int, device_id: str, soil_type_1: int, soil_type_2: int, threshold1: int, threshold2: int):
        self.id = _id
        self.device_id = device_id
        self.soil_types = [soil_type_1, soil_type_2]
        self.thresholds = [threshold1, threshold2]

    