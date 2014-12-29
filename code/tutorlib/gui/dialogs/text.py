
## A Python Tutorial System
## Copyright (C) 2009,2010  Peter Robinson <pjr@itee.uq.edu.au>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.

## The MyPyTutor text dialog

import tkinter as tk
from tkinter import ttk

from tutorlib.gui.dialogs.dialog import Dialog


class TextDialog(Dialog):
    def __init__(self, parent, title, text):
        # set up vars needed to create widgets
        self.text = text

        # defer remaining setup to parent
        super().__init__(parent, title, allow_cancel=False)

    def create_widgets(self):
        # TODO: sort out style
        frame_main = ttk.Frame(
            self.frame_top,
            borderwidth=2,
            relief=tk.SUNKEN,
        )
        frame_main.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        # TODO: sort out style
        textwin = tk.Text(
            frame_main,
            width=80,
            height=40,
            wrap=tk.WORD,
        )
        textwin.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame_main)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        textwin.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textwin.yview)

        textwin.insert(tk.END, self.text)
        textwin.config(state=tk.DISABLED)
