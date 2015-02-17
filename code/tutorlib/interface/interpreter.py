import os
from subprocess import Popen
from tempfile import mkstemp


class Interpreter():
    def __init__(self):
        self.subprocess = None

        self._path = None

    def __del__(self):
        os.remove(self.path)  # will gen before removing, but meh

    @property
    def path(self):
        if self._path is None:
            _, self._path = mkstemp()
        return self._path

    @property
    def args(self):
        # we hope that idle3 is correctly defined
        # (idle could be idle2, though it might be worth falling back to it)
        return [
            'idle3',
            '-t', 'MyPyTutor',
            '-r', self.path,
        ]

    def reload(self, code):
        # write the student's code to a file
        with open(self.path, 'w') as f:
            f.write(code)

        # terminate existing subprocess if necessary
        if self.subprocess is not None:
            self.subprocess.terminate()

        # create the shell
        self.subprocess = Popen(self.args)
