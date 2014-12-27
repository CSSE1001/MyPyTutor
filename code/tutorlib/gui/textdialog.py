
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

from tkinter import *


class TextDialog(Toplevel):
    def __init__(self, parent, title, text, bg='#ffffff'):
        Toplevel.__init__(self, parent)
        self.parent = parent

        self.configure(borderwidth=5)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 30,
                                  parent.winfo_rooty() + 30))
        #self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)

        self.create_widgets(text, bg)

        #self.grab_set()
        self.button_ok.focus_set()

        self.protocol("WM_DELETE_WINDOW", self.ok)
        self.bind('<Return>', self.ok)
        self.bind('<Escape>', self.ok)

        self.wait_window()

    def create_widgets(self, text, bg):
        frame_main = Frame(self, borderwidth=2, relief=SUNKEN, bg=bg)
        frame_main.pack(side=TOP, expand=TRUE, fill=BOTH)

        textwin = Text(frame_main, width=80, height=40, bg=bg, wrap=WORD)
        textwin.pack(side=LEFT)

        scrollbar = Scrollbar(frame_main)
        scrollbar.pack(side=RIGHT, fill=Y)
        textwin.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textwin.yview)

        # buttons
        frame_buttons = Frame(self)
        frame_buttons.pack(fill=X)

        self.button_ok = Button(frame_buttons, text='Close', command=self.ok)
        self.button_ok.pack()

        textwin.insert(END, text)
        textwin.config(state=DISABLED)

    def ok(self, event=None):
        self.destroy()
