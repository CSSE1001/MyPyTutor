import os


MPT_DIR = os.path.join(os.path.expanduser('~'), '.mptrc')
if not os.path.exists(MPT_DIR):
    os.mkdir(MPT_DIR)
else:
    assert os.path.isdir(MPT_DIR), \
        '{} should be a directory.  Please delete the existing config ' \
    'file at that location.'.format(MPT_DIR)

CONFIG_FILE = os.path.join(MPT_DIR, 'config')
TUTORIAL_ATTEMPTS_FILE = os.path.join(MPT_DIR, 'tutorial_attempts')
