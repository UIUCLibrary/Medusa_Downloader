from medusadownloader import utils

CHUNK_SIZE = 1024


def download_file(save_as, url, username, password, metadata=None):
    """
    Generator function that downloads the files and yields the progress

    Args:
        save_as: Path and filename for the data to be saved
        url: Source of the data to be downloaded
        username: Medusa Http Auth user name
        password: Medusa Http Auth password
        metadata: Optional. Dictionary of the json data that the file.

    Yields: Progress of the download. If the size is mentioned included the metadata, this is percentage.
            Otherwise, it's in bytes

    """

    session = utils.get_session(username=username, password=password)

    with session as s:
        yield from utils.download(url, save_as, s, metadata)
