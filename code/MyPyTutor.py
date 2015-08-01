#!/usr/bin/env python3
from __future__ import print_function
import sys
from argparse import ArgumentParser

ALLOWED_VERSIONS = [(3, 4)]

if sys.version_info.major == 3:
    from getpass import getpass
    import os
    import subprocess
    import tkinter as tk
    import tkinter.filedialog as tkFiledialog
    from urllib.request import URLopener
    from zipfile import ZipFile

DEFAULT_CONFIG = {
    'online': {
        'store_credentials': True,
        'username': '',
    },
    'tutorials': {
        'names': ['CSSE1001Tutorials'],
        'default': 'CSSE1001Tutorials',
    },
    'CSSE1001Tutorials': {
        'tut_dir': '',
        'ans_dir': '',
    },
}
DEFAULT_MPT_URL = 'http://csse1001.uqcloud.net/mpt3/MyPyTutor34.zip'
MPT_SERVICE = 'MyPyTutor'
MPT_FILENAME = 'MyPyTutor.py'  # usually __file__, but need to support renaming
GLOBAL_TIMEOUT = 10.  # seconds


def execl(cmd, *args):
    """
    Execute the given command with the given arguments.

    This is an alisas for the underlying execl system call on Unix.
    Windows does not support a sensible fork + exec mechanism; as a result,
    this method makes use of subprocess on that OS.

    """
    if sys.platform == 'win32':
        # by convention, cmd == args[0], but Popen only needs it the once
        argv = [cmd] + list(args[1:])
        process = subprocess.Popen(argv)

        sys.exit(process.wait())
    else:
        os.execl(cmd, *args)


def get_script_dir():
    """
    Return the path to the script.

    The use of realpath in both places is necessary to get sensible behaviour
    under Windows.

    """
    return os.path.realpath(os.path.dirname(os.path.realpath(__file__)))


def setup_modules():
    """
    Perform any global module setup needed by MyPyTutor.

    """
    import socket
    socket.setdefaulttimeout(GLOBAL_TIMEOUT)


def check_compatibility():
    """
    Print an error message and exit if the user is not running the correct
    Python version for MyPyTutor.

    This function will not return if the system is not compatible.

    """
    major, minor = sys.version_info[:2]

    for version in ALLOWED_VERSIONS:
        if version == (major, minor):
            return

    print('Python {}.{} is unsupported by MyPyTutor.'.format(major, minor))
    allowed_versions = ', '.join(
        '{}.{}'.format(*version) for version in ALLOWED_VERSIONS
    )
    print('Please upgrade to {}Python {}'.format("one of " if len(ALLOWED_VERSIONS) > 1 else "", allowed_versions))

    import subprocess
    import platform
    if platform.system() in ['Darwin', 'Linux']:
        p = subprocess.Popen(["which", "python3"], stdout=subprocess.PIPE)
        output = p.communicate()[0]
        if not p.returncode:
            print("Python 3 auto-detected at: {}".format(output.strip()))
        else:
            print("Failed to auto-detect Python 3.")
    print("For more information, please visit the following url: http://csse1001.uqcloud.net/installing-mpt#common-errors")

    (input if major == 3 else raw_input)("\nPress Enter to continue...")

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

    print('Installing MyPyTutor...', end='', flush=True)

    # grab the latest zip file
    # we use an explicit filename here because we don't yet have access
    # to the tutorlib module for abstracting away temporary file creation
    try:
        urlobj = URLopener()
        filename, _ = urlobj.retrieve(url, 'MyPyTutor.zip')
    except Exception:
        print('failed')
        sys.exit(1)

    # extract the file
    with ZipFile(filename) as zf:
        zf.extractall(install_path)

    print('done')


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
    # we should special-case the lab machines to use H: drive
    # windows machines should use Documents (NB: it's not always at this path;
    # if not, default to the home dir)
    documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
    if sys.platform == 'win32' and os.path.exists('H:'):
        default_path = os.path.join('H:', 'MyPyTutor')
    elif sys.platform == 'win32' and os.path.exists(documents_dir):
        default_path = os.path.join(documents_dir, 'MyPyTutor')
    else:
        default_path = os.path.join(os.path.expanduser('~'), 'MyPyTutor')

    print('Default MyPyTutor install directory: {}'.format(default_path))
    change_default = input(
        "Type 'yes' if you would like to change the install directory: "
    )

    if change_default != 'yes':
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

        # remove the installer, so the user can't keep running it
        this_path = os.path.realpath(__file__)
        os.remove(this_path)

        # re-exec in MPT dir
        this_filename = os.path.basename(MPT_FILENAME)
        mpt_path = os.path.join(install_path, this_filename)

        argv = [mpt_path] + sys.argv[1:]

        execl(sys.executable, sys.executable, *argv)


def update_mpt(force_update=False):
    """
    Update MyPyTutor if necessary.

    If an update is available, this function will not return, but will instead
    re-exec the current script.

    Args:
      force_update (bool, optional): If True, update regardless of whether a
        newer version of MyPyTutor is available on the server.

    """
    # if we've made it to here, we assume that we are running in the MyPyTutor
    # directory and that these imports will succeed
    from tutorlib.gui.app.app import VERSION
    from tutorlib.gui.app.support import safely_extract_zipfile
    from tutorlib.interface.web_api import WebAPI, WebAPIError

    print('Checking for MyPyTutor updates...', end='', flush=True)

    def _check_for_updates():
        # grab the server version
        web_api = WebAPI()
        version = web_api.get_version()

        print('done')

        create_tuple = lambda v: tuple(map(int, v.split('.')))
        server_version = create_tuple(version)
        local_version = create_tuple(VERSION)

        if server_version > local_version or force_update:
            print('Updating MyPyTutor...', end='', flush=True)

            # grab our new zip file
            mpt_zip_path = web_api.get_mpt_zipfile()

            # extract over the script path
            # do NOT delete things; the user could have other stuff here
            script_dir = get_script_dir()

            safely_extract_zipfile(mpt_zip_path, script_dir)

            print('done')

            # re-exec with the new version
            # remove update arg, or we get an infinite loop
            argv = sys.argv
            if '--force-update-mpt' in argv:
                argv.remove('--force-update-mpt')

            execl(sys.executable, sys.executable, *argv)

    try:
        _check_for_updates()
    except WebAPIError:
        print('failed')


def create_config_if_needed():
    """
    If no configuration file exists, create the default configuration file.

    Note that this will not download the initial tutorial set.

    """
    from tutorlib.config.configuration import config_exists, save_config
    from tutorlib.config.namespaces import Namespace

    if not config_exists():
        print('Creating default config...', end='', flush=True)

        default_config = Namespace(**DEFAULT_CONFIG)
        save_config(default_config)

        print('done')


def bootstrap_tutorials():
    """
    If the default tutorial path does not exist, download and extract the
    tutorials zipfile.

    If no default tutorial package is specified, CSSE1001Tutorials will be
    assumed (this is the default package name used by this script).

    """
    from tutorlib.config.configuration import load_config, save_config
    from tutorlib.gui.app.support import safely_extract_zipfile
    from tutorlib.interface.problems \
            import TutorialPackage, TutorialPackageError
    from tutorlib.interface.web_api import WebAPI, WebAPIError

    # grab our config file
    cfg = load_config()
    options = getattr(cfg, cfg.tutorials.default or 'CSSE1001Tutorials')

    def tutorials_are_installed():
        if not options.tut_dir:  # no entry in config at all (default)
            return False
        if not os.path.exists(options.tut_dir):  # no package directory at all
            return False
        if not os.path.exists(options.ans_dir):  # no answers dir
            return False

        try:
            _ = TutorialPackage(cfg.tutorials.default, options)
        except TutorialPackageError:
            return False

        return True

    if not tutorials_are_installed():
        print('Downloading default tutorial package...', end='', flush=True)

        web_api = WebAPI()
        try:
            filename = web_api.get_tutorials_zipfile()
        except WebAPIError:
            print('failed')
            sys.exit(1)

        print('done')

        # set the default tutorial directory
        # our default tutorial directory is in the same directory as the script
        # note that this assumes we used the default config, which created the
        # CSSE1001Tutorials key
        print('Installing default tutorial package...', end='', flush=True)

        script_dir = get_script_dir()
        options.tut_dir = os.path.join(script_dir, 'CSSE1001Tutorials')
        options.ans_dir = os.path.join(script_dir, 'CSSE1001Answers')

        safely_extract_zipfile(filename, options.tut_dir)

        if not os.path.exists(options.ans_dir):
            os.mkdir(options.ans_dir)

        save_config(cfg)

        print('done')


def update_default_tutorial_package(force_update=False):
    """
    Update the default tutorial package if necessary.

    Args:
      force_update (bool, optional): If True, update regardless of whether a
        newer version of the tutorial package is available on the server.

    """
    from tutorlib.config.configuration import load_config
    from tutorlib.gui.app.support \
            import remove_directory_contents, safely_extract_zipfile
    from tutorlib.interface.problems \
            import TutorialPackage, TutorialPackageError
    from tutorlib.interface.web_api import WebAPI, WebAPIError

    print('Checking for tutorial package updates...', end='', flush=True)

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

    try:
        timestamp = web_api.get_tutorials_timestamp()
    except WebAPIError:
        print('failed')
        return

    # we need to be comparing as ints
    create_tuple = lambda t: tuple(map(int, t.split('.')))
    server_timestamp = create_tuple(timestamp)
    local_timestamp = create_tuple(tutorial_package.timestamp)

    print('done')

    # we only want to update if the server's version is more recent
    # a more recent local version should only arise in development, anyway
    if server_timestamp <= local_timestamp and not force_update:
        return

    print('Updating tutorial package...', end='', flush=True)

    # grab the zipfile
    try:
        zip_path = web_api.get_tutorials_zipfile()
    except WebAPIError:
        print('failed')
        return

    # extract the zipfile into our empty tutorial directory
    remove_directory_contents(tutorial_package.options.tut_dir)
    safely_extract_zipfile(zip_path, tutorial_package.options.tut_dir)

    print('done')


def install_keyring_module():
    """
    Install the keyring module using pip.

    If pip is not installed, print an error message and exit.

    This function does not attempt to install with admin privileges.

    Returns:
      Whether the installation was successful.

    """
    try:
        import pip
    except ImportError:
        print('Cannot install keyring: pip does not appear to be installed')
        return False

    args = ['install', 'keyring', '--quiet']
    if pip.main(args):
        # something went wrong
        # we could potentially try running as admin, but for now just fail
        return False
    return True


def try_get_credentials():
    """
    Try to get the user's credentials.

    If the keyring module is not installed, prompt the user to install it.
    If the user refuses, set a flag so as not to prompt again.

    If the module is installed and the user has saved credentials, return them.
    Otherwise, prompt the user to enter credentials to save.

    Returns:
      A tuple containing the user's username and password.

    """
    # we need access to the config file
    from tutorlib.config.configuration import load_config, save_config
    cfg = load_config()

    # return if the user has said not to store anything
    if not cfg.online.store_credentials:
        return None, None

    try:
        import keyring
    except ImportError:
        print()
        print(
            'We can securely store your username and password using the '
            'keyring module'
        )
        store = input(
            "Type 'yes' if you would like us to store your credentials: "
        )
        if store == 'yes':
            install = input(
                "Type 'yes' if you would like to install the keyring module: "
            )

        # if the user said no, remember their choice
        # we also remember if the install failed, as this is unlikely to change
        if store != 'yes' or install != 'yes' or not install_keyring_module():
            cfg.online.store_credentials = False
            save_config(cfg)

            return None, None

        import keyring  # should cause no problems at this point

    # if we have a username, return the associated password
    if cfg.online.username:
        password = keyring.get_password(MPT_SERVICE, cfg.online.username)
        return cfg.online.username, password

    # grab the user's username and password
    print()
    print('Please enter your UQ username and password')
    cfg.online.username = input('Username: ')
    password = getpass()
    print()

    save_config(cfg)
    keyring.set_password(MPT_SERVICE, cfg.online.username, password)

    return cfg.online.username, password


def try_login(username, password):
    """
    Try to log in with the given username and password.

    Args:
      username (str): The username to log in with.
      password (str): The password to use.

    Returns:
      If successful, the logged-in WebAPI instance.
      If unsuccessful, None.

    """
    from tutorlib.interface.web_api import WebAPI, WebAPIError
    web_api = WebAPI()

    print('Attempting to login as {}...'.format(username), end='', flush=True)

    def reset_credentials():
        import keyring
        from tutorlib.config.configuration import load_config, save_config
        cfg = load_config()

        try:
            keyring.delete_password(MPT_SERVICE, cfg.online.username)
        except Exception:  # PasswordDeleteError isn't defined anywhere!
            pass

        cfg.online.username = ''

        save_config(cfg)

    try:
        success = web_api.login(username, password)
    except WebAPIError:
        success = False

    # it's safer to clear the credentials even if the login threw
    # this will cause users to have to log in again if they try to run MPT
    # without an internet connection, but oh well
    if not success:
        reset_credentials()

    print('done' if success else 'failed')
    return web_api if success else None


def synchronise_problems(web_api):
    """
    Synchronise problems for the default tutorial package.

    Args:
      web_api (WebAPI): The WebAPI instance to use.  This must be logged in.

    """
    from tutorlib.config.configuration import load_config
    from tutorlib.interface.problems \
            import TutorialPackage, TutorialPackageError
    from tutorlib.online.sync import SyncClient

    print('Synchronising tutorial problems...', end='', flush=True)

    cfg = load_config()
    try:
        options = getattr(cfg, cfg.tutorials.default)
    except AttributeError:
        print('failed')
        return

    try:
        tutorial_package = TutorialPackage(cfg.tutorials.default, options)
    except TutorialPackageError:
        print('failed')
        return

    client = SyncClient(web_api)
    if not client.synchronise(tutorial_package):
        print('failed')
        return

    print('done')


def print_version():
    """
    Print the current version of MyPyTutor.

    """
    from tutorlib.gui.app.app import VERSION
    print(VERSION)


def launch_mpt(web_api=None):
    """
    Launch MyPyTutor.

    This function enters the tkinter main loop and so will not return until
    the program has been closed.

    Args:
      web_api (WebAPI, optional): The WebAPI object, if any, to pass to the
        TutorialApp instance.  Defaults to None.  If provided, this must be
        logged in.

    Returns:
      The TutorialApp instance which was used.

    """
    # if we've made it to here, assume these imports will succeed
    from tutorlib.gui.app.app import TutorialApp

    print('Running MyPyTutor...', end='', flush=True)

    root = tk.Tk()
    app = TutorialApp(root, web_api=web_api)
    root.mainloop()

    print('done')

    return app


def shutdown(app):
    """
    Shut down the given app, and perform any necessary cleanup.

    Args:
      app (TutorialApp): The app which has just terminated.

    """
    from tutorlib.interface.web_api import WebAPIError
    from tutorlib.utils.tmp import cleanup_temp_files

    # sync tutorials if necessary
    if app.web_api.is_logged_in:
        synchronise_problems(app.web_api)

        print('Logging out of MyPyTutor...', end='', flush=True)

        try:
            app.web_api.logout()
        except WebAPIError:
            pass  # who cares at this point

        print('done')

    # wipe out our temp files
    print('Cleaning up...', end='', flush=True)
    cleanup_temp_files()
    print('done')



def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        '--force-update-mpt',
        action='store_true',
        help='Update MyPyTutor even if this would not normally be required',
    )
    parser.add_argument(
        '--force-update-tutorials',
        action='store_true',
        help='Update tutorials even if this would not normally be required',
    )
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
    # parse args, and exit early where necessary
    args = parse_args()

    if args.version:
        print_version()
        return 0

    # exit if the user's system is not compatible with MyPyTutor
    check_compatibility()

    # set up module globals (eg, socket timeout)
    setup_modules()

    # install and update MyPyTutor
    bootstrap_install(use_gui=not args.no_gui)
    update_mpt(force_update=args.force_update_mpt)

    create_config_if_needed()

    # install and update the default tutorial package
    bootstrap_tutorials()
    update_default_tutorial_package(force_update=args.force_update_tutorials)

    # try to log the user in automatically
    username, password = try_get_credentials()
    if username is not None:
        web_api = try_login(username, password)
    else:
        web_api = None

    if web_api is not None:
        synchronise_problems(web_api)

    # launch MyPyTutor itself
    app = launch_mpt(web_api)

    # cleanup (syncrhonise, logout etc)
    shutdown(app)

    return 0


if __name__ == '__main__':
    sys.exit(main())
