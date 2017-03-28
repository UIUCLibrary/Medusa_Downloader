import pytest
import medusadownloader

PASSWORD = "fakepassword"
USERNAME = "fakeuser"


@pytest.fixture(scope="session")
def key_file(tmpdir_factory):
    """
    
    This generates the following file.
    
    [http_auth]
    username=fakeuser
    password=fakepassword

    """

    fn = tmpdir_factory.mktemp("dummy").join("fakekey.ini")
    with open(str(fn), "w", encoding="utf8") as f:
        f.write("[http_auth]\n")
        f.write("username=%s\n" % USERNAME)
        f.write("password=%s\n" % PASSWORD)
    return str(fn)


# noinspection PyShadowingNames
def test_read(key_file):
    key = medusadownloader.read_key(key_file)
    assert isinstance(key, medusadownloader.key.Key)
    assert key.password == PASSWORD
    assert key.username == USERNAME
