from openephys_client import Client


def main():
    c = Client(app_name="Foo")

    c.loop()


if __name__ == "__main__":
    main()
