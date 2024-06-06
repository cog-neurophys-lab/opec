from openephys_client import Client
import logging


def main():
    c = Client(app_name="Foo")

    c.loop()


if __name__ == "__main__":
    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    main()
