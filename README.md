# OpenEphys ZMQ Client (OPEZ) for Python 

This project will provide a small library for receiving data from the OpenEphys ZMQ
interface (currently at version v0.3.2) Initial code and descriptions are from
https://github.com/open-ephys-plugins/zmq-interface. 

This library is based on code from the [Opeth](https://opeth.readthedocs.io) package by
Andras Szell and others licensed with GPLv3. Opez will be used to build similar applications
to Opeth.

Tests: [![Tests](https://github.com/cog-neurophys-lab/opez/actions/workflows/python-app.yml/badge.svg)](https://github.com/cog-neurophys-lab/opez/actions/workflows/python-app.yml)

## Installation

```
pip install opez
```


## Get Started

- Checkout [simple_plotter.py](opez/simple_plotter.py) on how to use the `Client` in your application

## Heartbeat messages

In order for a client to be detected, it must periodically send heartbeat messages to the
plugin's listening port. Each heartbeat message is a JSON string with the following fields:

```json
    "application" : application name
    "uuid" : universally unique identifier (string)
    "type": "heartbeat"
```

The recommended heartbeat interval is 2 seconds. 

## Data Packets

The ZMQ Interface sends multi-part ZMQ messages. Each message consists of three parts:

### 1. Message Envelope

Contains the type of message being received (`DATAx\00` or `EVENT\x00`).


### 2. Message Header

A JSON string containing information about the incoming data packet:

#### Continuous data

```python
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
    type: str  # type of message, should always be "data"
    content: ContinuousDataHeaderMessageContent
    data_size: int  # size of the data buffer in bytes
    timestamp: int  # timestamp of the message in milliseconds
```

#### Event data

```python
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
```

#### Spike data

```python
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
```

### 3. Message Data

- **Continuous**: Continuous data from one channel
- **TTL Event**: "Event data (in order) = {1Byte\: 'Event Line', 1 Byte\: 'Event state(0 or 1)', 8 Bytes:'TTL Word'}
- **Spike**: Spike waveform
