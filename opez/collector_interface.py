from abc import ABC, abstractmethod
import numpy as np
from opez.events import OpenEphysEvent, OpenEphysSpikeEvent
from opez.continuous_data import OpenEphysContinuousData


class CollectorInterface(ABC):

    @abstractmethod
    def add_continuous_data(self, data: OpenEphysContinuousData):
        pass

    @abstractmethod
    def get_continuous_data(self) -> OpenEphysContinuousData | np.ndarray:
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
    def collect_data(
        self, data: OpenEphysContinuousData | OpenEphysSpikeEvent | OpenEphysEvent
    ):
        pass

    @abstractmethod
    def keep_last(self, seconds: float | None = None, samples: int | None = None):
        pass
