import datetime

class Reading():
    def __init__(self, _id: int, device_id: int, reading: int, last_time: datetime.datetime):
        self.id = _id
        self.device_id = device_id
        self.value = reading
        self.last_time = last_time