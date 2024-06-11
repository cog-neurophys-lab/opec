from opez.collector_interface import CollectorInterface
from opez.connection import Connection
from opez.continuous_data import OpenEphysContinuousData
from opez.events import OpenEphysEvent, OpenEphysSpikeEvent
from opez.messages import (
    ContinuousDataHeaderMessage,
    EventDataHeaderMessage,
    HeartBeatMessage,
    SpikeDataHeaderMessage,
)
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


def data_from_bytes(
    header: (
        SpikeDataHeaderMessage | EventDataHeaderMessage | ContinuousDataHeaderMessage
    ),
    data: bytes,
):
    if isinstance(header, ContinuousDataHeaderMessage):
        return OpenEphysContinuousData.from_message(header=header, data=data)

    elif isinstance(header, EventDataHeaderMessage):
        if header.data_size > 0:
            event = OpenEphysEvent(header.content, data)
        else:
            event = OpenEphysEvent(header.content)
        return event

    elif isinstance(header, SpikeDataHeaderMessage):
        return OpenEphysSpikeEvent(header.spike, data)

    return None


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

    def update(
        self,
    ) -> OpenEphysContinuousData | OpenEphysEvent | OpenEphysSpikeEvent | None:
        self.connection.check_connection()

        socks = self.connection.check_sockets_for_data()

        if not socks:
            logger.debug("no data received")
            return None

        # data in the data socket
        if self.connection.data_socket in socks:
            header, data = self.connection.receive()

            if header is None or data is None:
                logger.info(
                    f"Received data without header or data: header={header}, data={data}"
                )
                return None

            parsed_data = data_from_bytes(header, data)

            if self.collector is not None:
                self.collector.collect_data(parsed_data)
            else:
                logger.debug(
                    f"Received data without collector: header={header}, data={data}"
                )

            return parsed_data

        # data in the event/heartbeat socket
        elif (
            self.connection.event_socket in socks
            and self.connection.event_socket_waits_reply
        ):
            message = self.connection.event_socket.recv()
            logger.debug("event reply received")
            self.connection.event_socket_waits_reply = False

        return None

    def loop(self):
        logger.debug("loop started")
        data = self.update()
        while not self._stop:
            data = self.update()
            logger.debug(f"Received data: {data}")
            if data is not None:
                logger.warning(f"Received empty data: {data}")

        logger.debug("loop exited")


def main():
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)

    c = Client(app_name="Python Test Client")
    c.loop()


if __name__ == "__main__":
    main()
