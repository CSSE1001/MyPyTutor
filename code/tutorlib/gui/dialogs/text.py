
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

from tutorlib.gui.dialogs.dialog import Dialog


class TextDialog(Dialog):
    def __init__(self, parent, title, text, bg='#ffffff'):
        # set up vars needed to create widgets
        self.text = text
        self.bg = bg

        # defer remaining setup to parent
        super().__init__(parent, title, allow_cancel=False)

    def create_widgets(self):
        frame_main = Frame(
            self.frame_top,
            borderwidth=2,
            relief=SUNKEN,
            bg=self.bg)
        frame_main.pack(side=TOP, expand=TRUE, fill=BOTH)

        textwin = Text(frame_main, width=80, height=40, bg=self.bg, wrap=WORD)
        textwin.pack(side=LEFT)

        scrollbar = Scrollbar(frame_main)
        scrollbar.pack(side=RIGHT, fill=Y)
        textwin.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textwin.yview)

        textwin.insert(END, self.text)
        textwin.config(state=DISABLED)
