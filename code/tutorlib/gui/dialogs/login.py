
## A Python Tutorial System
## Copyright (C) 2009,2010  Peter Robinson <pjr@itee.uq.edu.au>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but tk.WITHOUT ANY tk.WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.

## Dialogs involving passwords

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmessagebox

from tutorlib.gui.dialogs.dialog import Dialog


class LoginDialog(Dialog):
    def __init__(self, parent, callback, title="Login"):
        # set up vars needed to create widgets
        self.callback = callback

        # defer remaining setup to parent
        super().__init__(parent, title, allow_cancel=True)

    def create_widgets(self):
        # username
        userframe = ttk.Frame(self.frame_top)
        userframe.pack(expand=tk.TRUE, fill=tk.X)

        ttk.Label(
            userframe,
            text='Username: ',
        ).pack(side=tk.LEFT, anchor=tk.W, expand=tk.TRUE)

        self.user_entry = ttk.Entry(
            userframe,
            width=20,
        )
        self.user_entry.pack(side=tk.LEFT)

        # password
        passframe = ttk.Frame(self.frame_top)
        passframe.pack(expand=tk.TRUE, fill=tk.X)

        ttk.Label(
            passframe,
            text='Password: ',
        ).pack(side=tk.LEFT, anchor=tk.W, expand=tk.TRUE)

        self.pass_entry = ttk.Entry(
            passframe,
            width=20,
            show="*",
        )
        self.pass_entry.pack(side=tk.LEFT)

    def ok(self, event=None):
        user = self.user_entry.get().strip()
        password = self.pass_entry.get()  # don't strip, for obvious reasons

        success = self.callback(user, password)
        if success:
            self.destroy()
        else:
            tkmessagebox.showerror(
                'Login Error', 'Incorrect username or password',
            )
            self.pass_entry.delete(0, tk.END)
