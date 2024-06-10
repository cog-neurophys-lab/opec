from .connection import Connection
from .messages import HeartBeatMessage
from .client import Client
from .circular_buffer import CircularBuffer


__all__ = ["Connection", "HeartBeatMessage", "Client", "CircularBuffer"]

ZMQ_PLUGIN_MIN_VERSION = ["0.3.0"]


def main():
    import logging

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    c = Client(app_name="Python Test Client")
    c.loop()


if __name__ == "__main__":
    main()
