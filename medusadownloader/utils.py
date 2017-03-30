import hashlib
import itertools
import os
import shutil
import tempfile

import requests
from requests import auth

from medusadownloader import errors
from medusadownloader.downloader import CHUNK_SIZE


def get_session(username, password):
    s = requests.Session()
    s.auth = auth.HTTPBasicAuth(username, password)
    return s


def download(url, save_as, session, metadata):
    def get_data_and_progress(stream):
        a, b = itertools.tee(stream)
        return zip(a, itertools.accumulate(map(lambda i: len(i), b)))

    dst_path = os.path.dirname(save_as)
    r = session.get(url, timeout=10)
    # If the data returned is not a binary file, then it's an error
    if r.encoding == "utf-8":

        msg = r.content.decode("utf8")

        known_error = errors.get_error(msg)
        if known_error:
            raise known_error
        else:
            raise ConnectionError(msg)
    else:
        hasher = hashlib.md5()

        # Download in a temp directory so if something fails, it'll be deleted
        with tempfile.TemporaryDirectory() as d:
            tmp_name = os.path.join(d, ".incompletedata")

            with open(tmp_name, "wb") as f:
                for chunk, data_downloaded in get_data_and_progress(r.iter_content(chunk_size=CHUNK_SIZE)):

                    # If the size is known, calculate the progress and yield it

                    hasher.update(chunk)
                    f.write(chunk)

                    if metadata is not None and "size" in metadata:
                        yield (data_downloaded / int(metadata['size'])) * 100
                    else:
                        yield data_downloaded

            # If an md5 hash is known, make sure matches
            if metadata is not None and 'md5_sum' in metadata:
                if metadata['md5_sum'] != hasher.hexdigest():
                    raise AssertionError("MD5 hash for \"{}\" doesn't match expected data".format(url))

            # If the destination folder doesn't exist, create it
            if not os.path.exists(dst_path):
                os.makedirs(dst_path)
            shutil.move(tmp_name, save_as)
