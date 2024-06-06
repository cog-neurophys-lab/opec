from .connection import Connection
from .messages import HeartBeatMessage, header_message_from_string
import time
from uuid import UUID, uuid4
import numpy as np
import json
from .events import OpenEphysEvent, OpenEphysSpikeEvent
import logging

logger = logging.getLogger("logger")


class Client:
    connection: Connection
    app_name: str
    uuid: UUID | str
    _heartbeat_msg: HeartBeatMessage
    heartbeat_interval_seconds: float
    message_num: int = -1

    def __init__(
        self,
        app_name: str,
        ip: str = "localhost",
        data_port: int = 5556,
        heartbeat_interval_seconds: float = 2.0,
    ):
        self.connection = Connection(ip=ip, data_port=data_port)
        self.app_name = app_name
        self.uuid = str(uuid4())
        self._heartbeat_msg = HeartBeatMessage(app_name=self.app_name, uuid=self.uuid)
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def send_heartbeat(self):
        self.connection.send_heartbeat(self._heartbeat_msg)

    def check_connection(self):
        # TODO: move this to `Connection` class
        if (
            time.time() - self.connection.last_heartbeat_req_time
        ) > self.heartbeat_interval_seconds:
            if self.connection.event_socket_waits_reply:
                self.connection.last_heartbeat_req_time += 1.0
                if (time.time() - self.connection.last_reply_time) > 10.0:
                    self.connection.reconnect()
            else:
                self.send_heartbeat()

    def loop(self):

        while True:
            self.check_connection()

            # TODO: move this to `Connection` class
            socks = dict(self.connection.poller.poll(1))
            if not socks:
                logger.debug("no data received")
                break

            # data in the data socket
            if self.connection.data_socket in socks:
                message = self.connection.receive_multipart_data_message()

                if len(message) == 0:
                    logger.debug("no data received or error during reception")
                    break

                envelope_msg, header_msg, data_msg = message

                header = header_message_from_string(
                    envelope_msg.decode("utf-8"), header_msg.decode("utf-8")
                )

                if header is None:
                    logger.error("header message could not be parsed")
                    continue

                if (
                    self.message_num != -1
                    and header.message_num != self.message_num + 1
                ):
                    logger.warning("missing a message at number", self.message_num)
                self.message_num = header.message_num

                # TODO: process the in data_ms based on the header
                # ...

            # data in the event/heartbeat socket
            elif (
                self.connection.event_socket in socks
                and self.connection.event_socket_waits_reply
            ):
                message = self.connection.event_socket.recv()
                logger.debug("event reply received")
                self.connection.event_socket_waits_reply = False

        return True


def main():
    c = Client(app_name="Foo")
    c.loop()


if __name__ == "__main__":
    main()
