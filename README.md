# Python Example Client for OpenEphys ZMQ Interface

This project will provide a small library for receiving data from the OpenEphys ZMQ
interface (currently at version v0.3.2) Initial code and descriptions are from
https://github.com/open-ephys-plugins/zmq-interface. 


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

### Message Envelope

Contains the type of message being received (`data`, `spike`, or `event`), as well as the
index of the message (`message_num`).

### Message Header

A JSON string containing information about the incoming data packet:

#### Continuous data

```json
    "stream" : stream name
    "channel_num" : local channel index
    "num_samples": num of samples in this buffer
    "sample_num": index of first sample
    "sample_rate": sampling rate of this channel
```

#### Event data

```json
    "stream" : stream name
    "source_node" : processor ID that generated the event
    "type": specifies TTL vs. message,
    "sample_num": index of the event
```

#### Spike data

```json
    "stream" : stream name
    "source_node" : processor ID that generated the spike
    "electrode" : name of the spike channel
    "sample_num" : index of the peak sample
    "num_channels" : total number of channels in this spike
    "num_samples" : total number of samples in this spike
    "sorted_id" : sorted ID (default = 0)
    "threshold" : threshold values across all channels
```

#### Message Data

- **Continuous**: Continuous data from one channel
- **TTL Event**: "Event data (in order) = {1Byte\: 'Event Line', 1 Byte\: 'Event state(0 or 1)', 8 Bytes:'TTL Word'}
- **Spike**: Spike waveform
