from html.parser import HTMLParser


class MedusaErrorParser(HTMLParser):
    def error(self, message):
        raise NotImplementedError

    def __init__(self):
        super().__init__()
        self.error_type = None

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            for name, value in attrs:
                if name == "id" and value == "shib_login":
                    self.error_type = ConnectionRefusedError(
                        "Redirected to shibboleth login. Make sure your username and password are correct.")


def get_error(html):
    parser = MedusaErrorParser()
    parser.feed(html)
    return parser.error_type
