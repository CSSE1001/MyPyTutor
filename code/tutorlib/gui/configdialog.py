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

## For initial configuration

from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import os

from tutorlib.gui.dialog import Dialog

LABEL_TEXT = """Before using MyPyTutor or when adding a new tutorial you need to set two folders.
The tutorial folder contains the tutorial problems that you should have already installed.
The answers folder is used to store your (partial) answers. When you save an answer it is put in this folder and when you choose a problem to work on that you have saved previously, your code will be automatically loaded.
The tutorial name can be supplied (default the tutorial folder name)."""


class TutorialDirectoryPrompt(Dialog):
    def __init__(self, master):
        # set up vars needed to create widgets
        self.result = None

        # defer remaining setup to parent
        super().__init__(master, 'Tutorial Configuration', allow_cancel=True)

    def create_widgets(self):
        Label(
            self.frame_top,
            text=LABEL_TEXT,
            wraplength=400,
            justify=LEFT,
        ).pack(side=TOP)

        labels = ['Tutorial Folder: ', 'Answers Folder: ', 'Tutorial Name: ']
        callbacks = [self.select_tut_dir, self.select_ans_dir, None]
        entries = []

        for lbl, callback in zip(labels, callbacks):
            frame = Frame(self.frame_top, relief=SUNKEN, border=3)
            frame.pack(side=TOP, expand=TRUE, fill=BOTH, pady=20)

            Label(
                frame,
                text=lbl,
            ).pack(side=LEFT)

            entry = Entry(frame, width=50)
            entry.pack(side=LEFT)
            entries.append(entry)

            if callback is not None:
                Button(
                    frame,
                    text='Select',
                    command=callback,
                ).pack(side=LEFT, padx=10)

        self.tut_entry, self.ans_entry, self.name_entry = entries

    def select_tut_dir(self):
        self.tut_entry.delete(0, END)
        dirname = tkinter.filedialog.askdirectory(
            title='Choose Tutorial Folder'
        )
        if dirname:
            self.tut_entry.insert(0, dirname)
            if self.name_entry.get() == '':
                self.name_entry.insert(0, os.path.basename(dirname))

    def select_ans_dir(self):
        self.ans_entry.delete(0, END)
        dirname = tkinter.filedialog.askdirectory(
            title='Choose Answers Folder'
        )
        if dirname:
            self.ans_entry.insert(0, dirname)

    def ok(self, e=None):
        tut_dir = self.tut_entry.get()
        ans_dir = self.ans_entry.get()
        name = self.name_entry.get()
        if not (os.path.exists(tut_dir)
                and os.path.exists(os.path.join(tut_dir, 'tutorials.txt'))
                and os.path.exists(os.path.join(tut_dir, 'config.txt'))):
            tkinter.messagebox.showerror('Tutorial Configuration Error',
                                         'Invalid tutorial folder.')
        elif ans_dir == '':
            tkinter.messagebox.showerror('Tutorial Configuration Error',
                                         'Invalid answers folder.')
        else:
            self.result = tut_dir, self.ans_entry.get(), name
            self.withdraw()
            self.update_idletasks()
            self.cancel()

    def cancel(self, e=None):
        self.master.focus_set()
        self.destroy()
