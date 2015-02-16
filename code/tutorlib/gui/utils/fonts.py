import platform
import tkinter as tk


_SYSTEM = platform.system()

SIZE = 12

_NORMAL = {
    'Windows': 'Calibri',
    'Darwin': 'Helvetica',
}
_NORMAL_DEFAULT = 'Arial'
NORMAL_NAME = _NORMAL.get(_SYSTEM, _NORMAL_DEFAULT)

NORMAL_FONT = (NORMAL_NAME, SIZE, 'normal')

_FIXED = {
    'Windows': 'Consolas',
    'Darwin': 'Menlo Regular',
}
_FIXED_DEFAULT = 'Courier'
FIXED_NAME = _FIXED.get(_SYSTEM, _FIXED_DEFAULT)

FIXED_FONT = (FIXED_NAME, SIZE, 'roman')
