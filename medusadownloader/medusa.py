import os
from json import JSONDecodeError

import requests
from requests.auth import HTTPBasicAuth
from collections import namedtuple

import medusadownloader.utils
from medusadownloader import errors

MedusaData = namedtuple("MedusaData", ['filename', 'download_link', 'metadata'])


class Medusa:
    def __init__(self, root, username, password):
        self.root = root
        self._auth = HTTPBasicAuth(username, password)

    def __enter__(self):
        self._session = requests.session()
        self._session.auth = self._auth
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_collection_json(self, collection_id):
        """

        Args:
            collection_id: Collection id number.

        Returns: Collection level metadata.

        """
        url = self.root + "/collections/" + str(collection_id) + ".json"
        data = self._session.get(url, timeout=5)
        if data.ok:
            try:
                json_data = data.json()
            except JSONDecodeError:
                msg = data.content.decode()
                known_error = errors.get_error(msg)
                if known_error:
                    raise known_error
                raise ConnectionError(data.text)
            return json_data
        else:
            raise ConnectionError(data.status_code)

    def get_bit_level_file_group_json(self, bit_level_file_groups):
        """

        Args:
            bit_level_file_groups: bit level file group id number

        Returns: bit level file group metadata

        """
        url = self.root + "/bit_level_file_groups/" + str(bit_level_file_groups) + ".json"
        data = self._session.get(url, timeout=5)
        if data.ok:
            try:
                json_data = data.json()
            except JSONDecodeError:
                msg = data.content.decode()
                known_error = errors.get_error(msg)
                if known_error:
                    raise known_error
                raise ConnectionError(data.text)
            return json_data
        else:
            raise ConnectionError(data.status_code)

    def get_folder_json_url(self, bit_level_file_groups):
        json_data = self.get_bit_level_file_group_json(bit_level_file_groups)
        return self.root + json_data['cfs_directory']['path']

    def get_file_binaries_url(self, bit_level_file_group_id):
        """

        Get the list of URLS to needed to download the files

        Args:
            bit_level_file_group_id: Id number of the file group

        Yields: list of urls to download the files from a group

        """
        binary_path = self.get_folder_json_url(bit_level_file_group_id)

        r = self._session.get(binary_path)
        data = r.json()

        for file_metadata in data['files']:
            download_path = self.root + "/cfs_files/" + str(file_metadata['id']) + "/download"
            relative_path = file_metadata['relative_pathname']
            yield MedusaData(relative_path, download_path, metadata=file_metadata)

    def download(self, medusa_file: MedusaData, path):
        yield from medusadownloader.utils.download(url=medusa_file.download_link,
                                                   save_as=os.path.join(path, medusa_file.filename),
                                                   session=self._session, metadata=medusa_file.metadata)
