import datetime

class Flow():
    def __init__(self, _id: int, hub_id: int, reading: int, zone: int, last_time: datetime.datetime):
        self.id = _id
        self.hub_id = hub_id
        self.value = reading
        self.zone = zone
        self.last_time = last_time
