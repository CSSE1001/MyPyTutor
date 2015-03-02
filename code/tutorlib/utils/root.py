import tkinter as tk


def get_root_widget(widget=None):
    """
    Get the root widget of the widget heirarchy containing the given widget.

    If no widget is given, a tk.Toplevel widget will be briefly created and
    then immediately destroyed.  This enables us to get access to the internal
    tk reference to the root window (as this is the master of an unowned
    Toplevel instance).

    Note that in a multi-process environment, this will return the root for
    the current process.

    There is a minor danger of the user seeing the Toplevel flick on screen.

    Args:
      widget (tk.Widget): The widget to get the root of.

    Returns:
      The root widget in the hierarchy (usually a tk.Tk instance).

    """
    if widget is None:
        tl = tk.Toplevel()
        root = tl.master
        tl.destroy()

        return root

    child = widget
    parent = child.winfo_parent()

    while parent:
        child = child.nametowidget(parent)
        parent = child.winfo_parent()

    return child
