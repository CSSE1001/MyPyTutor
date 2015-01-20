from functools import partial
import inspect
import tkinter.messagebox as tkmessagebox

from tutorlib.gui.utils.root import get_root_widget


def show(title, message, f=tkmessagebox.showinfo, *args, **kwargs):
    """
    Base method for showing a tkinter.messagebox popup.

    This function will instruct the root widget to update itself prior to
    returning.  It is necessary to do this explicitly on some versions of
    OS X in order to ensure that the window does in fact disappear.

    Args:
      title (str): The title to display.
      message (str): The message to display.
      f (() -> object): The function to call to display the messagebox.  Should
          be a tkinter.messagebox member.

    Returns:
      The result of executing f.

    """
    result = f(title, message, *args, **kwargs)

    root = get_root_widget()
    root.update()
    root.update_idletasks()

    return result


# make available every public member on tkinter.messagebox
for _name, _obj in inspect.getmembers(tkmessagebox):
    if inspect.isfunction(_obj) and not _name.startswith('_'):
        globals()[_name] = partial(show, f=_obj)
    else:
        globals()[_name] = _obj
