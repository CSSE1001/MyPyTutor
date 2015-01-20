def get_root_widget(widget):
    """
    Get the root widget of the widget heirarchy containing the given widget.

    Args:
      widget (tk.Widget): The widget to get the root of.

    Returns:
      The root widget in the hierarchy (usually a tk.Tk instance).

    """
    child = widget
    parent = child.winfo_parent()

    while parent:
        child = child.nametowidget(parent)
        parent = child.winfo_parent()

    return child
