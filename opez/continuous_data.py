from dataclasses import dataclass
from typing import ClassVar
import numpy as np
import numpy.typing
from .messages import ContinuousDataHeaderMessage


@dataclass
class OpenEphysContinuousData:

    header: ContinuousDataHeaderMessage
    array: np.ndarray
    dtype: ClassVar[numpy.typing.DTypeLike] = np.float32

    @staticmethod
    def from_message(data: bytes, header: ContinuousDataHeaderMessage):

        n_arr = np.frombuffer(data, dtype=OpenEphysContinuousData.dtype)
        n_arr = np.reshape(n_arr, (-1, header.content.num_samples))

        return OpenEphysContinuousData(array=n_arr, header=header)
