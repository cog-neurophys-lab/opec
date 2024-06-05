from .connection import Connection
from .messages import HeartBeatMessage
import time
from uuid import UUID, uuid4
import threading
import numpy as np
import zmq
import json
from .events import OpenEphysEvent, OpenEphysSpikeEvent


class Client:

    connection: Connection
    app_name: str
    uuid: UUID
    last_heartbeat_time: float
    last_reply_time: float

    # timer: threading.Timer

    def __init__(
        self, app_name: str, ip: str = "tcp://localhost", data_port: int = 5556
    ):
        self.connection = Connection(ip=ip, port=data_port)
        self.app_name = app_name
        self.uuid = uuid4()
        self.last_heartbeat_time = 0
        self.timer = threading.Timer(2, self.send_heartbeat)

    def send_heartbeat(self):
        print("sending heartbeat")
        self.connection.event_socket.send(
            HeartBeatMessage(self.app_name, self.uuid).to_utf8
        )
        self.connection.socket_waits_reply = True
        self.last_heartbeat_time = time.time()

    def loop(self):

        self.connection.init_datasocket()

        while True:
            if (time.time() - self.last_heartbeat_time) > 2.0:
                if self.connection.socket_waits_reply:
                    print("heartbeat haven't got reply, retrying...")
                    self.last_heartbeat_time += 1.0
                    if (time.time() - self.last_reply_time) > 10.0:
                        # reconnecting the socket as per
                        # the "lazy pirate" pattern (see the ZeroMQ guide)
                        print("connection lost, trying to reconnect")
                        self.connection.poller.unregister(self.event_socket)
                        self.connection.event_socket.close()
                        self.connection.event_socket = self.context.socket(zmq.REQ)
                        self.connection.event_socket.connect(f"tcp://{ip}:{port + 1}")
                        self.connection.poller.register(self.event_socket)
                        self.connection.socket_waits_reply = False
                        self.last_reply_time = time.time()
                else:
                    self.send_heartbeat()

            socks = dict(self.poller.poll(1))
            if not socks:
                # print("poll exits")
                break

            if self.data_socket in socks:
                try:
                    message = self.data_socket.recv_multipart(zmq.NOBLOCK)
                except zmq.ZMQError as err:
                    print("got error: {0}".format(err))
                    break
                if message:
                    if len(message) < 2:
                        print("no frames for message: ", message[0])
                    try:
                        header = json.loads(message[1].decode("utf-8"))
                    except ValueError as e:
                        print("ValueError: ", e)
                        print(message[1])
                    if (
                        self.message_num != -1
                        and header["message_num"] != self.message_num + 1
                    ):
                        print("missing a message at number", self.message_num)
                    self.message_num = header["message_num"]
                    if header["type"] == "data":
                        c = header["content"]
                        num_samples = c["num_samples"]
                        channel_num = c["channel_num"]
                        # sample_rate = c['sample_rate']

                        if channel_num == 1:
                            try:
                                n_arr = np.frombuffer(message[2], dtype=np.float32)
                                n_arr = np.reshape(n_arr, num_samples)

                                if num_samples > 0:
                                    self.update_plot(n_arr)

                            except IndexError as e:
                                print(e)
                                print(header)
                                print(message[1])
                                if len(message) > 2:
                                    print(len(message[2]))
                                else:
                                    print("only one frame???")

                    elif header["type"] == "event":

                        if header["data_size"] > 0:
                            event = OpenEphysEvent(header["content"], message[2])
                        else:
                            event = OpenEphysEvent(header["content"])

                        self.update_plot_event(event)

                    elif header["type"] == "spike":
                        spike = OpenEphysSpikeEvent(header["spike"], message[2])
                        self.update_plot_spike(spike)

                    elif header["type"] == "param":
                        c = header["content"]
                        self.__dict__.update(c)
                        print(c)
                    else:
                        raise ValueError("message type unknown")
                else:
                    print("got not data")

                    break
            elif self.event_socket in socks and self.socket_waits_reply:
                message = self.event_socket.recv()
                print("event reply received")
                print(message)
                if self.socket_waits_reply:
                    self.socket_waits_reply = False

                else:
                    print("???? getting a reply before a send?")

        return True
