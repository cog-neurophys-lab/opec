from __future__ import annotations
import zmq
import time
from .messages import HeartBeatMessage, header_message_from_string
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .messages import (
        ContinuousDataHeaderMessage,
        EventDataHeaderMessage,
        SpikeDataHeaderMessage,
    )

logger = logging.getLogger("logger")


class Connection:
    ip: str
    port: int
    context: zmq.Context
    event_socket: zmq.Socket
    data_socket: zmq.Socket
    poller: zmq.Poller
    event_socket_waits_reply: bool
    last_reply_time: float
    last_heartbeat_req_time: float
    message_num: int = -1
    hearbeat_message: HeartBeatMessage
    heartbeat_interval_seconds: float = 2.0

    def __init__(
        self,
        ip: str,
        heartbeat_msg: HeartBeatMessage,
        data_port: int = 5556,
        heartbeat_interval_seconds: float = 2.0,
    ):
        self.ip = ip
        self.port = data_port

        self.context = zmq.Context()

        # set up data socket for receiving data
        self.data_socket = self.context.socket(zmq.SUB)
        self.data_socket.connect(f"tcp://{self.ip}:{self.port}")
        self.data_socket.setsockopt(zmq.SUBSCRIBE, b"")

        # set up event socket for sending out heartbeats
        self.event_socket = self.context.socket(zmq.REQ)
        self.event_socket.connect(f"tcp://{ip}:{data_port+1}")
        self.event_socket_waits_reply = False

        # initialize poller with both sockets
        self.poller = zmq.Poller()
        self.poller.register(self.data_socket, zmq.POLLIN)
        self.poller.register(self.event_socket, zmq.POLLIN)

        self.last_reply_time = time.time()
        self.last_heartbeat_req_time = 0.0
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self.heartbeat_msg = heartbeat_msg

    def _receive_multipart_data_message(self) -> list[bytes]:
        try:
            message = self.data_socket.recv_multipart(zmq.NOBLOCK)
        except zmq.ZMQError as err:
            logger.error(
                f"Error while reciving multipart message from data socket: {err}"
            )
            message = []

        if len(message) != 3:
            logger.error(
                f"received message with less than the expected 3 parts: {message}"
            )
            message = []

        logger.debug(f"received message: {message}")
        return message

    def receive(
        self,
    ) -> tuple[
        ContinuousDataHeaderMessage
        | EventDataHeaderMessage
        | SpikeDataHeaderMessage
        | None,
        bytes | None,
    ]:
        message = self._receive_multipart_data_message()

        if len(message) == 0:
            logger.debug("no data received or error during reception")
            return None, None

        envelope_msg, header_msg, data_msg = message

        header = header_message_from_string(
            envelope_msg.decode("utf-8"), header_msg.decode("utf-8")
        )

        if header is None:
            logger.error("header message could not be parsed")
            return None, None

        if self.message_num != -1 and header.message_num != self.message_num + 1:
            logger.warning("missing a message at number", self.message_num)

        self.message_num = header.message_num

        # TODO: handle different types of messages
        data = data_msg

        return header, data

    def check_connection(self):
        if (
            time.time() - self.last_heartbeat_req_time
        ) > self.heartbeat_interval_seconds:
            if self.event_socket_waits_reply:
                self.last_heartbeat_req_time += 1.0
                if (time.time() - self.last_reply_time) > 10.0:
                    self.reconnect()
            else:
                self.send_heartbeat()

    def send_heartbeat(self):
        if self.event_socket_waits_reply:
            logger.warning(
                "Tried to send heartbeat while waiting for reply, skipping heartbeat"
            )
            return
        self.event_socket.send(self.heartbeat_msg.to_utf8())
        self.event_socket_waits_reply = True
        self.last_heartbeat_req_time = time.time()

    def reconnect(self):
        self.poller.unregister(self.event_socket)
        self.event_socket.close()
        self.event_socket = self.context.socket(zmq.REQ)
        self.event_socket.connect(f"tcp://{self.ip}:{self.port + 1}")
        self.poller.register(self.event_socket)
        self.event_socket_waits_reply = False
        self.last_reply_time = time.time()
