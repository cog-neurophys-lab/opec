import zmq


class Connection:
    context: zmq.Context
    event_socket: zmq.Socket
    data_socket: zmq.Socket
    poller: zmq.Poller
    socket_waits_reply: bool
    ip: str
    port: int

    def __init__(self, ip: str = "localhost", data_port: int = 5556):
        self.context = zmq.Context()
        self.data_socket = self.context.socket(zmq.SUB)
        self.data_socket.connect(f"tcp://{ip}:{data_port}")
        self.event_socket: zmq.Socket = self.context.socket(zmq.REQ)
        self.event_socket.connect(f"tcp://{ip}:{data_port+1}")
        self.socket_waits_reply = False
        self.poller = zmq.Poller()
        self.ip = ip
        self.port = data_port

    def init_datasocket(self):
        if not self.data_socket:
            print("init socket")
            self.data_socket = self.context.socket(zmq.SUB)
            self.data_socket.connect(f"tcp://{self.ip}:{self.port}")

            self.data_socket.setsockopt(zmq.SUBSCRIBE, b"")
            self.poller.register(self.data_socket, zmq.POLLIN)
            self.poller.register(self.event_socket, zmq.POLLIN)
