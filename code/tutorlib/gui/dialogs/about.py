
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

## The about dialog for MyPyTutor

from tkinter import *

from tutorlib.gui.dialogs.dialog import Dialog


class TutAboutDialog(Dialog):
    def create_widgets(self):
        frame_main = Frame(
            self.frame_top,
            borderwidth=2,
            relief=SUNKEN,
            bg="#ffffaa",
        )
        frame_main.pack(side=TOP, expand=TRUE, fill=BOTH)

        Label(
            frame_main,
            text='MyPyTutor: A Python Tutorial System',
            bg="#ffffaa",
        ).pack(padx=10, pady=10)

        Label(
            frame_main,
            text='Copyright 2010 Peter Robinson',
            bg="#ffffaa",
        ).pack(padx=10, pady=10)

        Label(
            frame_main,
            text='email: pjr@itee.uq.edu.au',
            bg="#ffffaa",
        ).pack(padx=10, pady=10)
