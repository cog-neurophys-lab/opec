import opec
import numpy as np


def test_append():
    itemcnt = 10000
    cb = opec.CircularBuffer(
        capacity=itemcnt,
        initial_shape=(10, itemcnt * 2),
        allocated=itemcnt * 2,
        append_axis=1,
    )

    assert cb.size() == itemcnt
    assert len(cb) == 0
    arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]).reshape(10, 1)
    cb.append(arr)
    assert len(cb) == 1
    for index in range(10):
        assert cb[index] == arr[index]
