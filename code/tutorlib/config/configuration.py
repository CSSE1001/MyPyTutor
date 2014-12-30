'''
Attributes:
  CONFIG_FILE (str, constant): The full path to the MyPyTutor config file.
  SPECIAL_FORMATS ({(str, str): function(str) -> type}): Special formats for
      specific configuration keys.  Keys are identified by the pair (section,
      option).  The corresponding value is the special type used for the
      configuration key (eg int, float, list).

'''
import configparser
import os
import sys

from tutorlib.config.namespaces import Namespace
from tutorlib.gui.dialogs.config import TutorialDirectoryPrompt


# The config file is stored in the same directory as MyPyTutor.py
_SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
CONFIG_FILE = os.path.join(_SCRIPT_DIR, 'mypytutor.cfg')

SPECIAL_FORMATS = {
    ('font', 'size'): int,
    ('tutorials', 'names'): list,
    ('window_sizes', 'analysis'): int,
    ('window_sizes', 'output'): int,
    ('window_sizes', 'output'): int,
}


def load_config():
    '''
    Load the MyPyTutor configuration file.

    If the file does not exist, cannot be opened, or cannot be parsed, then
    revert to using default configuration values.

    If the config file can be opened and parsed, but is missing any default
    configuration value, revert to using that value for the relevant key.

    All values will be unwrapped (and so converted to the appropriate format,
    according to the SPECIAL_FORMATS module variable).

    Returns:
      A Namespace mapping configuration sections to a Namespace mapping
      section options to values.

      For example, if the configuration file looks like this:

          [section_name]
          key1 = value

      Then the attribute `result.section_name.key1` will equal `value`.

    '''
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
    '''
    Save the given config data to disk.

    All values will be wrapped before saving (and so converted back to strings,
    which is necessary for the ConfigParser to play nice).

    Args:
      config (Namespace): The configuration data to save.

    '''
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
    '''
    Return the unwrapped value corresponding to the given config key.

    Unwrapping values involves converting them to the appropriate Python data
    type (from strs, which is all the ConfigParser can understand).  The module
    variable SPECIAL_FORMATS is used to determine the types to convert to.

    Args:
      section (str): The configuration section corresponding to the value.
      option (str): The configuration option corresponding to the value.
      value: (str): The value to convert.

    Returns:
      The value, converted to the relevant special format.

      If no special format applies, return the value as a string.

    '''
    special_type = SPECIAL_FORMATS.get((section, option))
    if special_type is None:
        return value

    # TODO: I vaguely remember a bug using is on builtins, should check
    if special_type is list:
        return [elem for elem in value.split(',') if elem]
    elif special_type is int:
        return int(value)

    raise AssertionError('Unknown special type {}'.format(special_type))


def wrap_value(section, option, value):
    '''
    Return the wrapped value corresponding to the given config key.

    Wrapping values involves converting them back from the appropriate Python
    data type to strs, which is all the ConfigParser can understand.  The
    module variable SPECIAL_FORMATS is used to determine the types to convert
    from, and it is assumed that the value is in fact of the correct type.

    Args:
      section (str): The configuration section corresponding to the value.
      option (str): The configuration option corresponding to the value.
      value: (object): The value to convert.

    Returns:
      The value, converted to a string.

    '''
    special_type = SPECIAL_FORMATS.get((section, option))
    if special_type is None:
        return str(value)

    assert isinstance(value, special_type)

    # TODO: I vaguely remember a bug using is on builtins, should check
    if special_type is list:
        assert all(',' not in elem for elem in value), \
                'Cannot create comma-separated list; one or more list ' \
                'elements contain commas: {}'.format(value)
        return ','.join(value)
    elif special_type is int:
        return str(value)

    raise AssertionError('Unknown special type {}'.format(special_type))


def add_tutorial(config, window=None, as_default=True):
    '''
    Prompt the user to add a tutorial to the given configuration datta.

    Args:
      config (Namespace): The configuration data to work with.
      window (tk.Wm, optional): The base window of the prompt to show the user.
          Defaults to None (which, in tk, is eqivalent to the root window).
      as_default (bool, optional): Whether the added tutorial should be set as
          the new default tutorial.  Defaults to True.

    Returns:
      None, if the tutorial was successfully added.

      An error message as a string, otherwise.

    '''
    # prompt for a tutorial directory to add
    prompt = TutorialDirectoryPrompt(window)
    if prompt.result is None:
        return 'Cancelled'

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
