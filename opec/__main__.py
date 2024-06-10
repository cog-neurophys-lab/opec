from opec.client import Client


def main():
    import logging

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    c = Client(app_name="Python Test Client")
    c.loop()


if __name__ == "__main__":
    main()
