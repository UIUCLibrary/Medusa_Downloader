import configparser


class Key:
    def __init__(self, username, password):
        self.username = username
        self.password = password


def read_key(keyfile) -> Key:
    parser = configparser.ConfigParser()
    parser.read(keyfile)
    return Key(username=parser.get("http_auth", "username"), password=parser.get("http_auth", "password"))
