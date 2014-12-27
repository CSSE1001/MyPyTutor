import configparser
import os
import sys

from tutorlib.config.namespaces import Namespace
from tutorlib.TutorConfigure import TutorialDirectoryPrompt


# The config file is stored in the same directory as MyPyTutor.py
SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'mypytutor.cfg')

SPECIAL_FORMATS = {
    ('font', 'size'): int,
    ('tutorials', 'names'): list,
    ('window_sizes', 'analysis'): int,
    ('window_sizes', 'output'): int,
    ('window_sizes', 'output'): int,
}


def load_config():
    # parse the config file
    parser = configparser.ConfigParser()

    try:
        with open(CONFIG_FILE, 'rU') as f:
            parser.read_file(f)
    except (IOError, FileNotFoundError, configparser.ParsingError):
        # ignore parsing errors - we will just revert to defaults
        pass

    # transform this to a more useful format
    # this involves hard-coding the keys, but that would have to happen in some
    # place to *use* them anyway
    defaults = {
        'font': {
            'name': 'helvetica',
            'size': 10,
        },
        'tutorials': {
            'names': '',
            'default': '',
        },
        'window_sizes': {
            'analysis': 5,
            'output': 5,
            'problem': 20,
        },
    }

    cfg_dict = defaults

    # add in all parsed config values
    for section in parser.sections():
        if section not in defaults:
            defaults[section] = {}

        for option in parser.options(section):
            cfg_dict[section][option] = parser.get(section, option)

    # our final step is 'unwrapping' values
    # this handles non-standard config formats, such as lists
    # (side note: this is why it would have been better to use json)
    cfg_dict = {
        section: {
            option: unwrap_value(section, option, value)
                for option, value in options.items()
        } for section, options in cfg_dict.items()
    }

    return Namespace(**cfg_dict)


def save_config(config):
    # build up the config parser
    parser = configparser.ConfigParser()

    for section, options in config:
        parser.add_section(section)

        for option, value in options:
            value = wrap_value(section, option, value)
            parser.set(section, option, value)

    # write the config to file
    with open(CONFIG_FILE, 'w') as f:
        parser.write(f)


def unwrap_value(section, option, value):
    special_type = SPECIAL_FORMATS.get((section, option))
    if special_type is None:
        return value

    # TODO: I vaguely remember a bug using is on builtins, should check
    if special_type is list:
        return [elem for elem in value.split(',') if elem]
    elif special_type is int:
        return int(value)

    assert 0, 'Unknown special type {}'.format(special_type)


def wrap_value(section, option, value):
    special_type = SPECIAL_FORMATS.get((section, option))
    if special_type is None:
        return str(value)

    # TODO: I vaguely remember a bug using is on builtins, should check
    if special_type is list:
        assert all(',' not in elem for elem in value), \
                'Cannot create comma-separated list; one or more list ' \
                'elements contain commas: {}'.format(value)
        return ','.join(value)
    elif special_type is int:
        return str(value)

    assert 0, 'Unknown special type {}'.format(special_type)


def add_tutorial(config, window=None, as_default=True):  # TODO: check None works
    # TODO: proper comment; for now NB that None means ok, string means error
    # prompt for a tutorial directory to add
    prompt = TutorialDirectoryPrompt(window)
    if prompt.result is None:
        return

    tut_dir, ans_dir, name = prompt.result

    if name in config.tutorials.names:
        return 'The tutorial name {} already exists'.format(name)

    config.tutorials.names.append(name)

    if as_default:
        config.tutorials.default = name

    options = {
        'tut_dir': tut_dir,
        'ans_dir': ans_dir,
    }

    setattr(config, name, options)
