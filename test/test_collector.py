from opec.collector import Collector
from opec.continuous_data import OpenEphysContinuousData
from opec.messages import ContinuousDataHeaderMessage
import numpy as np


def test_collect_continuous_data():

    header = ContinuousDataHeaderMessage(
        message_num=1,
        type="data",
        content=ContinuousDataHeaderMessage.ContinuousDataHeaderMessageContent(
            stream="continuous",
            channel_num=1,
            num_samples=10,
            sample_num=0,
            sample_rate=30000,
        ),
        data_size=10,
        timestamp=0,
    )
    data = OpenEphysContinuousData(
        header=header,
        array=np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]).reshape(
            1, 10
        ),
    )

    collector = Collector()
    collector.collect_from_data(data)
    assert collector.has_data()
    assert len(collector.databuffer) == 10
