from opec.client import Client
import opec.collector


def main():
    import logging

    logger = logging.getLogger("logger")
    logger.setLevel(logging.DEBUG)

    collector = opec.collector.Collector()
    c = Client(app_name="Python Test Client", collector=collector)
    c.loop()


if __name__ == "__main__":
    main()
