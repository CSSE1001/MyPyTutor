import os
from shutil import copyfileobj
from tempfile import mkstemp as _mkstemp
from urllib.request import urlopen

from tutorlib.config.shared import TMP_DIRECTORY


def mkstemp(suffix='', prefix='tmp', dir=TMP_DIRECTORY, text=False):
    """
    Wrapper around tempfile.mkstemp which defaults to creating temporary
    files in the MyPyTutor temporary directory.

    Arguments and return values as for tempfile.mkstemp

    """
    return _mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)


def retrieve(url, filename=None):
    """
    Retrieve the object at the given URL, and store it to the local filesystem.

    Args:
      url (str): The URL to retrieve.
      filename (str, optional): The path to save the retrieved file to.
        If None, the file will be saved to the MyPyTutor temporary directory.

    Returns:
      The path to the downloaded file.

    """
    if filename is None:
        _, filename = mkstemp()

    with urlopen(url) as response, open(filename, 'wb') as f:
        copyfileobj(response, f)

    return filename


def cleanup_temp_files():
    """
    Clean up the MyPyTutor temporary directory.

    """
    for fn in os.listdir(TMP_DIRECTORY):
        path = os.path.join(TMP_DIRECTORY, fn)

        try:
            os.remove(path)
        except Exception:
            pass  # ignore errors -- we'll get them next time