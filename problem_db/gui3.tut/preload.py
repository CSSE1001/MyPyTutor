import tkinter as tk


def pressed():
    """
    Button callback function (command).

    You may alter what this function does if you wish, but you must not rename
    or delete it.

    """
    print("Button Pressed!")


def create_layout(frame):
    """
    Add four buttons to the frame in the given formt.

    Both buttons should have the callback (command) pressed, and they should
    have the labels "Button1" through "Button4".

    The layout in the frame after running this function will be:
      +---------------------------------------+
      |                                       |
      |  [Button1]                            |
      |               [Button3]    [Button4]  |
      |  [Button2]                            |
      |                                       |
      +---------------------------------------+

    Parameters:
      frame (tk.Frame): The frame to create the two buttons in.

    """
