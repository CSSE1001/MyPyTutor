from functools import partial
import os
import shutil
import zipfile


def safely_extract_zipfile(zip_path, extraction_path):
    """
    Safely extract a zipfile, with defence against path traversal attacks.

    Code is from http://stackoverflow.com/a/12886818/1103045

    Args:
      zip_path (str): The path of the zip file to extract.
      extraction_path (str): The directory to extract to.  This must exist.

    """
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = extraction_path

            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)

                if word in (os.curdir, os.pardir, ''):
                    continue

                path = os.path.join(path, word)

            zf.extract(member, path)


def remove_directory_contents(path):
    for p in map(partial(os.path.join, path), os.listdir(path)):
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)
        else:
            raise ValueError('Unexpected directory entry: {}'.format(p))