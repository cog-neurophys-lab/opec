from abc import ABC, abstractmethod
from opez.events import OpenEphysEvent, OpenEphysSpikeEvent
from opez.continuous_data import OpenEphysContinuousData
from opez.messages import (
    ContinuousDataHeaderMessage,
    SpikeDataHeaderMessage,
    EventDataHeaderMessage,
)


class CollectorInterface(ABC):

    @abstractmethod
    def add_data(self, data: OpenEphysContinuousData):
        pass

    @abstractmethod
    def add_spike(self, spike: OpenEphysSpikeEvent):
        pass

    @abstractmethod
    def add_ttl(self, ttl: OpenEphysEvent):
        pass

    @abstractmethod
    def add_event(self, event: OpenEphysEvent):
        pass

    @abstractmethod
    def collect_from_bytes(
        self,
        header: (
            ContinuousDataHeaderMessage
            | EventDataHeaderMessage
            | SpikeDataHeaderMessage
        ),
        data: bytes,
    ):
        pass

    @abstractmethod
    def collect_from_data(self, data):
        pass

    @abstractmethod
    def keep_last(self, seconds: float | None = None, samples: int | None = None):
        pass
