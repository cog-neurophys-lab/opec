import zmq
import time
from .messages import HeartBeatMessage
import logging

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

    def __init__(self, ip: str = "localhost", data_port: int = 5556):
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

    def receive_multipart_data_message(self) -> list[bytes]:
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

    def send_heartbeat(self, msg: HeartBeatMessage):
        if self.event_socket_waits_reply:
            logger.warning(
                "Tried to send heartbeat while waiting for reply, skipping heartbeat"
            )
            return
        self.event_socket.send(msg.to_utf8())
        self.event_socket_waits_reply = True
        self.last_heartbeat_time = time.time()

    def reconnect(self):
        self.poller.unregister(self.event_socket)
        self.event_socket.close()
        self.event_socket = self.context.socket(zmq.REQ)
        self.event_socket.connect(f"tcp://{self.ip}:{self.port + 1}")
        self.poller.register(self.event_socket)
        self.event_socket_waits_reply = False
        self.last_reply_time = time.time()
