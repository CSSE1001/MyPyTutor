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


def update_fonts(widget, font_info):
    try:
        widget.config(font=font_info)
    except tk.TclError:
        pass  # probably has no font config option

    for child in widget.winfo_children():
        update_fonts(child, font_info)