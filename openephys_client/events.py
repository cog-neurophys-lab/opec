import numpy as np


class OpenEphysEvent:

    event_types = {
        0: "TIMESTAMP",
        1: "BUFFER_SIZE",
        2: "PARAMETER_CHANGE",
        3: "TTL",
        4: "SPIKE",
        5: "MESSAGE",
        6: "BINARY_MSG",
    }

    def __init__(self, _d, _data=None):
        self.type = None
        self.stream = ""
        self.sample_num = 0
        self.source_node = 0
        self.event_state = 0
        self.event_line = 0
        self.event_word = 0
        self.numBytes = 0
        self.data = b""
        self.__dict__.update(_d)
        self.timestamp = None

        # noinspection PyTypeChecker
        self.type = OpenEphysEvent.event_types[self.type]
        if _data:
            self.data = _data
            self.numBytes = len(_data)

            dfb = np.frombuffer(self.data, dtype=np.uint8)
            self.event_line = dfb[0]

            dfb = np.frombuffer(self.data, dtype=np.uint8, offset=1)
            self.event_state = dfb[0]

            dfb = np.frombuffer(self.data, dtype=np.uint64, offset=2)
            self.event_word = dfb[0]
        if self.type == "TIMESTAMP":
            t = np.frombuffer(self.data, dtype=np.int64)
            self.timestamp = t[0]

    def set_data(self, _data):
        self.data = _data
        self.numBytes = len(_data)

    def __str__(self):
        ds = self.__dict__.copy()
        del ds["data"]
        return str(ds)

    @staticmethod
    def from_timestamp(timestamp, sample_num=0):
        """Debug code to auto-generate TTLs based on threshold level in case of file playback."""
        # {'event_channel': 0, 'event_id': 1, u'timestamp': 519170, 'base_timestamp': 518912, 'num_bytes': 8, 'type': 'TTL', 'sample_num': 258}
        e_template = {
            "type": 3,
            "timestamp": timestamp,
            "event_id": 1,
            "base_timestamp": timestamp - sample_num,
            "sample_num": sample_num,
            "num_bytes": 0,
        }
        return OpenEphysEvent(e_template)


class OpenEphysSpikeEvent:

    def __init__(self, _d, _data=None):
        self.stream = ""
        self.source_node = 0
        self.electrode = 0
        self.sample_num = 0
        self.num_channels = 0
        self.num_samples = 0
        self.sorted_id = 0
        self.threshold = []

        self.__dict__.update(_d)
        self.data = _data

    def __str__(self):
        ds = self.__dict__.copy()
        del ds["data"]
        return str(ds)
