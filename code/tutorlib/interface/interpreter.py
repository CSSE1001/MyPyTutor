from base64 import b64encode
from contextlib import contextmanager
import os
from subprocess import Popen
import sys
from tempfile import mkstemp

from tutorlib.gui.utils.fonts import FIXED_FONT


CODE_FILE_FORMAT = """
from base64 import b64decode
__student_code = b64decode({data}).decode('utf-16')
print(__student_code)

print()
print('--------------------')
print()

{code}
"""


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
        self.kill()
        os.remove(self.path)  # will gen before removing, but meh

    @property
    def is_alive(self):
        return self.subprocess is not None \
               and self.subprocess.poll() is None

    @property
    def args(self):
        """
        Return the arguments to use to launch the interpreter.

        If we are on Windows, we need to run python with the idle script as
        its argument, ie /Lib/idlelib/idle.py

        On a decent OS, idle3 will already be in PATH.

        Fail if neither of these conditions are true.

        """
        base_args = [
            '-t', 'MyPyTutor',  # window title
            '-r', self.path,  # script to run
        ]

        if sys.platform == 'win32':
            python_dir = os.path.dirname(sys.executable)
            idle_script = os.path.join(python_dir, 'Lib', 'idlelib', 'idle.py')

            return [sys.executable, idle_script] + base_args
        else:
            return ['idle3'] + base_args

    @property
    def path(self):
        if self._path is None:
            _, self._path = mkstemp()
        return self._path

    def kill(self):
        if self.is_alive:
            self.subprocess.kill()

    def reload(self, code):
        """
        Reload the interepreter with the given code.

        The interpreter will use the font settings of MPT, not those the user
        has set for IDLE.

        Args:
          code (str): The code to run.

        """
        # write the startup file
        data = b64encode(code.strip().encode('utf-16'))
        code_file_string = CODE_FILE_FORMAT.format(
            code=code,
            data=data,
        )

        # write the student's code to a file
        with open(self.path, 'w') as f:
            f.write(code_file_string)

        # terminate existing subprocess if necessary
        if self.is_alive:
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
