import json


class HeartBeatMessage:
    def __init__(self, app_name: str, uuid: str):
        self.application = app_name
        self.uuid = uuid
        self.type = "heartbeat"

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_utf8(self) -> bytes:
        return self.to_json().encode("utf-8")

    def __str__(self):
        return self.to_json()
