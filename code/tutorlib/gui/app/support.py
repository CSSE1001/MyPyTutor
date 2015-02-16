from functools import partial
import os
import shutil
from zipfile import ZipFile


def safely_extract_zipfile(zip_path, extraction_path):
    # in Py3, it looks like ZipFile does safe-ish extraction
    # we have a trusted source anyway, so this will do
    with ZipFile(zip_path) as zf:
        return zf.extractall(extraction_path)


def remove_directory_contents(path):
    for p in map(partial(os.path.join, path), os.listdir(path)):
        if os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)
        else:
            raise ValueError('Unexpected directory entry: {}'.format(p))