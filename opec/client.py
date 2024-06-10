from opec.collector_interface import CollectorInterface
from opec.connection import Connection
from opec.messages import HeartBeatMessage
from uuid import UUID, uuid4
import logging

logger = logging.getLogger("logger")


class Client:
    connection: Connection
    app_name: str
    uuid: UUID | str
    _heartbeat_msg: HeartBeatMessage
    collector: CollectorInterface | None
    _stop: bool = False

    def __init__(
        self,
        app_name: str,
        ip: str = "localhost",
        data_port: int = 5556,
        collector=None,
    ):
        self.app_name = app_name
        self.uuid = str(uuid4())
        self.connection = Connection(
            ip=ip,
            data_port=data_port,
            heartbeat_msg=HeartBeatMessage(app_name=self.app_name, uuid=self.uuid),
        )
        self.collector = collector

    def send_heartbeat(self):
        self.connection.send_heartbeat(self._heartbeat_msg)

    def loop(self):
        # TODO: Consider making this loop async
        while not self._stop:
            self.connection.check_connection()

            # TODO: move this to `Connection` class
            socks = dict(self.connection.poller.poll(1))
            if not socks:
                logger.debug("no data received")
                continue

            # data in the data socket
            if self.connection.data_socket in socks:
                header, data = self.connection.receive()

                if header is None or data is None:
                    logger.info(
                        f"Received data without header or data: header={header}, data={data}"
                    )
                    continue

                if self.collector is not None:
                    self.collector.collect_from_bytes(header, data)
                else:
                    logger.debug(
                        f"Received data without collector: header={header}, data={data}"
                    )
                    continue

            # data in the event/heartbeat socket
            elif (
                self.connection.event_socket in socks
                and self.connection.event_socket_waits_reply
            ):
                message = self.connection.event_socket.recv()
                logger.debug("event reply received")
                self.connection.event_socket_waits_reply = False

            if self.collector is not None:
                self.collector.keep_last(seconds=1)


def main():
    import logging

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    c = Client(app_name="Python Test Client")
    c.loop()


if __name__ == "__main__":
    main()
