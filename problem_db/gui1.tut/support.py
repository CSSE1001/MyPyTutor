# first, we need to make all of the necessary tk constants available to the
# student; we do them all so that they can experiment, even with incorrect
# configurations
import tkinter as _tk


LEFT = _tk.LEFT
RIGHT = _tk.RIGHT
TOP = _tk.TOP
BOTTOM = _tk.BOTTOM

TRUE = _tk.TRUE
FALSE = _tk.FALSE

BOTH = _tk.BOTH
X = _tk.X
Y = _tk.Y


class Button(_tk.Button):
    """
    Wrapper around tk.Button which logs widget creation.

    There's obviouisly more robust ways of achieving this in general, but for
    a simple layout exercise, this actually isn't too bad.

    Class Attributes:
      LOG (list): A list of arguments given to init and pack.  Argument order
          is (init_args, init_kwargs, pack_args, pack__kwargs).

    """
    LOG = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._init_args = args
        self._init_kwargs = kwargs

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)

        Button.LOG.append((self._init_args, self._init_kwargs, args, kwargs))