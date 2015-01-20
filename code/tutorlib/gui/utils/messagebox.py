from functools import partial
import inspect
import tkinter as tk
import tkinter.messagebox as tkmessagebox


def show(title, message, f=tkmessagebox.showinfo):
    result = f(title, message)

    # we want to wait on it
    # need a ref to the current Tk object
    # assuming we're in a single-process environment, and thus there can be
    # only one instance of Tk, we can use this hacky trick to get a reference
    # to the root window enagaged in the main loop
    # hopefully, this will be fast enough that the user won't see it
    tl = tk.Toplevel()
    root = tl.master
    tl.destroy()

    root.update()
    root.update_idletasks()

    return result


# make available every public member on tkinter.messagebox
for _name, _obj in inspect.getmembers(tkmessagebox):
    if inspect.isfunction(_obj) and not _name.startswith('_'):
        globals()[_name] = partial(show, f=_obj)
    else:
        globals()[_name] = _obj
