from contextlib import contextmanager
import os
from subprocess import Popen
from tempfile import mkstemp

from tutorlib.gui.utils.fonts import FIXED_FONT


class Interpreter():
    """
    A wrapper around a Python interpreter process.

    Attributes:
      subprocess (Popen): A handle to the interpreter subprocess.

    """
    def __init__(self):
        self.subprocess = None

        self._path = None

    def __del__(self):
        os.remove(self.path)  # will gen before removing, but meh

    @property
    def args(self):
        # we hope that idle3 is correctly defined
        # (idle could be idle2, though it might be worth falling back to it)
        return [
            'idle3',
            '-t', 'MyPyTutor',  # window title
            '-r', self.path,  # script to run
        ]

    @property
    def path(self):
        if self._path is None:
            _, self._path = mkstemp()
        return self._path

    def reload(self, code):
        """
        Reload the interepreter with the given code.

        The interpreter will use the font settings of MPT, not those the user
        has set for IDLE.

        Args:
          code (str): The code to run.

        """
        # write the student's code to a file
        with open(self.path, 'w') as f:
            f.write(code)

        # terminate existing subprocess if necessary
        if self.subprocess is not None:
            self.subprocess.terminate()

        # create the shell
        with altered_idle_config():
            self.subprocess = Popen(self.args)


@contextmanager
def altered_idle_config():
    """
    Inject the appropriate font settings into the idle config file.

    Note that this will ignore any specific config files (eg, config-unix.cfg).
    It's very unlikely that students will be using these.

    """
    from idlelib.configHandler import idleConf

    # save originals
    font_name = idleConf.GetOption('main', 'EditorWindow', 'font-name')
    font_size = idleConf.GetOption('main', 'EditorWindow', 'font-size')

    # replace them
    name, size, _ = map(str, FIXED_FONT)
    idleConf.SetOption('main', 'EditorWindow', 'font-name', name)
    idleConf.SetOption('main', 'EditorWindow', 'font-size', size)

    # save the config file
    idleConf.SaveUserCfgFiles()

    yield

    # replace the values
    if font_name is not None:
        idleConf.SetOption('main', 'EditorWindow', 'font-name', font_name)
    if font_size is not None:
        idleConf.SetOption('main', 'EditorWindow', 'font-size', font_size)

    if font_name is not None or font_size is not None:
        idleConf.SaveUserCfgFiles()
