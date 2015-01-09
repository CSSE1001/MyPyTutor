import os
import zipfile


def unzipit(zf, path):
    z = zipfile.ZipFile(zf)
    info = z.namelist()
    if not os.path.exists(path):
        os.mkdir(path)
    for item in info:
        if item.endswith('/') or item.endswith('\\'):
            fulldir = os.path.join(path, item)
            if not os.path.exists(fulldir):
                os.mkdir(fulldir)
        else:
            flags = (z.getinfo(item).external_attr >> 16) & 0o777
            text = z.read(item)
            fullpath = os.path.join(path, item)
            fd = open(fullpath, 'wb')
            fd.write(text)
            fd.close()
            os.chmod(fullpath, flags)
    z.close()
