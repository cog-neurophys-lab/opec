import json
from uuid import UUID
from dataclasses import dataclass


class HeartBeatMessage:
    application: str  # name of the application
    uuid: str | UUID  # unique identifier for the application
    type: str  # type of message, always "heartbeat"

    def __init__(self, app_name: str, uuid: str | UUID):
        self.application = app_name
        self.uuid = uuid
        self.type = "heartbeat"

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_utf8(self) -> bytes:
        return self.to_json().encode("utf-8")

    def __str__(self):
        return self.to_json()


@dataclass
class ContinuousDataHeaderMessage:

    @dataclass
    class ContinuousDataHeaderMessageContent:
        stream: str  # stream name
        channel_num: str  # local channel index
        num_samples: int  # num of samples in this buffer
        sample_num: int  # index of first sample
        sample_rate: float  # sampling rate of this channel

    message_num: int  # message number
    type: str  # type of message, should always be "continuous"
    content: ContinuousDataHeaderMessageContent
    data_size: int  # size of the data buffer in bytes
    timestamp: int  # timestamp of the message in milliseconds

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def from_json(self, json_str: str):
        self.__dict__ = json.loads(json_str)


@dataclass
class EventDataHeaderMessage:

    @dataclass
    class EventDataHeaderMessageContent:
        stream: str  # stream name
        source_node: str  # processor ID that generated the event
        type: str  # specifies TTL vs. message,
        sample_num: int  # index of the event

    message_num: int  # message number
    type: str  # type of message, should always be "event"
    content = EventDataHeaderMessageContent
    data_size: int  # size of the data buffer in bytes
    timestamp: int  # timestamp of the message in milliseconds

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def from_json(self, json_str: str):
        self.__dict__ = json.loads(json_str)


@dataclass
class SpikeDataHeaderMessage:

    @dataclass
    class SpikeDataHeaderMessageContent:
        stream: str  # stream name
        source_node: str  # processor ID that generated the spike
        electrode: str  # name of the spike channel
        sample_num: int  # index of the peak sample
        num_channels: int  # total number of channels in this spike
        num_samples: int  # total number of samples in this spike
        sorted_id: int  # sorted ID (default = 0)
        threshold: list[float]

    message_num: int  # message number
    type: str  # type of message, should always be "spike"
    spike: SpikeDataHeaderMessageContent
    timestamp: int  # timestamp of the message in milliseconds

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def from_json(self, json_str: str):
        self.__dict__ = json.loads(json_str)


def header_message_from_string(
    message_type: str, message: str
) -> ContinuousDataHeaderMessage | EventDataHeaderMessage | SpikeDataHeaderMessage:

    supported_headers = ["continuous", "event", "spike"]
    if message_type not in supported_headers:
        raise ValueError(f"Unknown header type: {message_type}")

    try:
        if message_type == "continuous":
            return ContinuousDataHeaderMessage(message)
        elif message_type == "event":
            return EventDataHeaderMessage(message)
        elif message_type == "spike":
            return SpikeDataHeaderMessage(message)
    except Exception as e:
        raise ValueError(f"Error while parsing header message:\n\t{message}\n{e}")
