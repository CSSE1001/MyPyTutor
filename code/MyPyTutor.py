from argparse import ArgumentParser
import os
import sys
import tkinter as tk
import tkinter.filedialog as tkFiledialog
from urllib.request import URLopener
from zipfile import ZipFile


DEFAULT_CONFIG = {
    'tutorials': {
        'names': ['CSSE1001Problems'],
        'default': 'CSSE1001Problems',
    },
    'CSSE1001Problems': {
        'tut_dir': '',
        'ans_dir': '',
    },
}
DEFAULT_MPT_URL = 'http://csse1001.uqcloud.net/mpt3/MyPyTutor34.zip'


def check_compatibility():
    """
    Print an error message and exit if the user is not running the correct
    Python version for MyPyTutor.

    This function will not return if the system is not compatible.

    """
    major, minor = sys.version_info[:2]
    allowed_minor_versions = [4]

    if major != 3 or minor not in allowed_minor_versions:
        print('Python {}.{} is unsupported by MyPyTutor'.format(major, minor))
        allowed_versions = ', '.join(
            '{}.{}'.format(major, m) for m in allowed_minor_versions
        )
        print('Please upgrade to one of Python {}'.format(allowed_versions))
        sys.exit(1)


def install_mpt(install_path, url=DEFAULT_MPT_URL):
    """
    Install MyPyTutor to the given directory.

    Args:
      install_path (str): The directory to install MyPyTutor in.
      url (str, optional): The URL of the MyPyTutor file to use.

    """
    # create our install path if it doesn't already exist
    if not os.path.exists(install_path):
        os.makedirs(install_path)

    # grab the latest zip file
    urlobj = URLopener()
    filename, _ = urlobj.retrieve(url)

    # extract the file
    with ZipFile(filename) as zf:
        zf.extractall(install_path)


def get_install_path(use_gui=True):
    """
    Get the install path to use for MyPyTutor.

    The user will be asked whether they wish to change the default path.
    If so, they will either be prompted with a GUI or text dialog to pick a
    directory, based on the value of use_gui.

    Args:
      use_gui (bool, optional): Whether to display a GUI prompt to pick a
        directory.  Defaults to True.

    Returns:
      The desired path to install MyPyTutor at.

    """
    # we should special-case the lab machines
    if sys.platform == 'win32' and os.path.exists('H:'):
        default_path = os.path.join('H:', 'MyPyTutor')
    else:
        default_path = os.path.join(os.path.expanduser('~'), 'MyPyTutor')

    print('Default MyPyTutor install directory: {}'.format(default_path))
    change_default = input('Change installation directory [yN]: ')

    if change_default != 'y':
        return default_path

    if use_gui:
        path = tkFiledialog.askdirectory(title='Choose MyPyTutor Directory')
        return path or default_path
    else:
        prompt = 'MyPyTutor install path [{}]: '.format(default_path)
        return input(prompt) or default_path


def bootstrap_install(use_gui):
    """
    Install MyPyTutor if it is not already installed.

    If so, re-exec as the newly installed script.  This means that this
    function will not return if it needed to install MPT.

    Args:
      use_gui (bool): Whether to display any GUI windows as part of the install
        process.  If not, only text prompts will be used.

    """
    # check if we are installed
    # if so, this import from tutorlib will succeed
    try:
        from tutorlib.config.shared import CONFIG_FILE
    except ImportError:
        install_path = get_install_path(use_gui=use_gui)
        install_mpt(install_path)

        # re-exec in MPT dir
        this_file = os.path.basename(__file__)
        mpt_path = os.path.join(install_path, this_file)

        argv = [mpt_path] + sys.argv[1:]

        os.execl(sys.executable, sys.executable, *argv)


def update_mpt():
    """
    Update MyPyTutor if necessary.

    If an update is available, this function will not return, but will instead
    re-exec the current script.

    """
    # if we've made it to here, we assume that we are running in the MyPyTutor
    # directory and that these imports will succeed
    from tutorlib.gui.app.app import VERSION
    from tutorlib.gui.app.support import safely_extract_zipfile
    from tutorlib.interface.web_api import WebAPI, WebAPIError

    print('Checking for MyPyTutor updates...', end='')

    def _check_for_updates():
        # grab the server version
        web_api = WebAPI()
        version = web_api.get_version()

        print('done')

        create_tuple = lambda v: tuple(map(int, v.split('.')))
        server_version = create_tuple(version)
        local_version = create_tuple(VERSION)

        if server_version > local_version:
            print('Updating MyPyTutor...', end='')

            # grab our new zip file
            mpt_zip_path = web_api.get_mpt_zipfile()

            # extract over the script path
            # do NOT delete things; the user could have other stuff here
            script_dir = os.path.dirname(os.path.realpath(__file__))

            safely_extract_zipfile(mpt_zip_path, script_dir)

            print('done')

            # re-exec with the new version
            os.execl(sys.executable, sys.executable, *sys.argv)

    try:
        _check_for_updates()
    except WebAPIError:
        print('failed')


def create_config_if_needed():
    """
    If no configuration file exists, create the default configuration file.

    Note that this will not download the initial tutorial set.

    """
    # if we've made it to here, assume these imports will succeed
    from tutorlib.config.configuration import config_exists, save_config
    from tutorlib.config.namespaces import Namespace

    if not config_exists():
        print('Creating default config...', end='')

        default_config = Namespace(**DEFAULT_CONFIG)
        save_config(default_config)

        print('done')


def bootstrap_tutorials():
    """
    If the default tutorial path does not exist, download and extract the
    tutorials zipfile.

    Note that this function assumes that CSSE1001Problems is the default
    tutorial package, and that the standard config file created by this script
    already exists.

    """
    # if we've made it to here, assume these imports will succeed
    from tutorlib.config.configuration import load_config, save_config
    from tutorlib.gui.app.support import safely_extract_zipfile
    from tutorlib.interface.web_api import WebAPI

    # grab our config file
    cfg = load_config()

    if not cfg.CSSE1001Problems.tut_dir:
        print('Downloading default tutorial package...', end='')

        web_api = WebAPI()
        filename = web_api.get_tutorials_zipfile()

        print('done')

        # set the default tutorial directory
        # our default tutorial directory is in the same directory as the script
        # note that this assumes we used the default config, which created the
        # CSSE1001Problems key
        print('Installing default tutorial package...', end='')

        script_dir = os.path.dirname(__file__)
        cfg.CSSE1001Problems.tut_dir = os.path.join(
            script_dir, 'CSSE1001Problems'
        )
        cfg.CSSE1001Problems.ans_dir = os.path.join(
            script_dir, 'CSSE1001Answers'
        )

        safely_extract_zipfile(filename, cfg.CSSE1001Problems.tut_dir)

        if not os.path.exists(cfg.CSSE1001Problems.ans_dir):
            os.mkdir(cfg.CSSE1001Problems.ans_dir)

        save_config(cfg)

        print('done')


def update_default_tutorial_package():
    """
    Update the default tutorial package if necessary.

    """
    # if we've made it to here, assume these imports will succeed
    from tutorlib.config.configuration import load_config
    from tutorlib.gui.app.support \
            import remove_directory_contents, safely_extract_zipfile
    from tutorlib.interface.problems \
            import TutorialPackage, TutorialPackageError
    from tutorlib.interface.web_api import WebAPI

    print('Checking for tutorial package updates...', end='')

    # grab our config file
    cfg = load_config()
    package_name = cfg.tutorials.default
    package_options = getattr(cfg, package_name)

    # try to open the tutorial package
    try:
        tutorial_package = TutorialPackage(package_name, package_options)
    except TutorialPackageError:
        print('failed')
        return

    # check if we need to do an update at all
    web_api = WebAPI()
    timestamp = web_api.get_tutorials_timestamp()

    # we need to be comparing as ints
    create_tuple = lambda t: tuple(map(int, t.split('.')))
    server_timestamp = create_tuple(timestamp)
    local_timestamp = create_tuple(tutorial_package.timestamp)

    print('done')

    # we only want to update if the server's version is more recent
    # a more recent local version should only arise in development, anyway
    if server_timestamp <= local_timestamp:
        return

    print('Updating tutorial package...', end='')

    # grab the zipfile
    zip_path = web_api.get_tutorials_zipfile()

    # extract the zipfile into our empty tutorial directory
    remove_directory_contents(tutorial_package.options.tut_dir)
    safely_extract_zipfile(zip_path, tutorial_package.options.tut_dir)

    print('done')


def print_version():
    """
    Print the current version of MyPyTutor.

    """
    from tutorlib.gui.app.app import VERSION
    print(VERSION)


def launch_mpt():
    """
    Launch MyPyTutor.

    This function enters the tkinter main loop and so will not return until
    the program has been closed.

    """
    # if we've made it to here, assume these imports will succeed
    from tutorlib.gui.app.app import TutorialApp

    root = tk.Tk()
    _ = TutorialApp(root)
    root.mainloop()


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run the installer without using a GUI',
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print the version and then terminate',
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.version:
        print_version()
        return 0

    check_compatibility()

    bootstrap_install(use_gui=not args.no_gui)
    update_mpt()

    create_config_if_needed()
    bootstrap_tutorials()

    update_default_tutorial_package()

    launch_mpt()

    return 0


if __name__ == '__main__':
    sys.exit(main())