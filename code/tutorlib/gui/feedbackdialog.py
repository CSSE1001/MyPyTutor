
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

## The feedback dialog for MyPyTutor

from tkinter import *
import urllib.request
import urllib.parse
import urllib.error
import tkinter.messagebox

## The URL for the feedback CGI script.
URL = 'http://csse1001.uqcloud.net/mpt/cgi-bin/feedback.py'


class FeedbackDialog(Toplevel):
    def __init__(self, parent, title, name, code=''):
        Toplevel.__init__(self, parent)
        self.parent = parent

        self.configure(borderwidth=5)
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 30,
                                  parent.winfo_rooty() + 30))
        self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)

        self.name = name
        self.subject_var = StringVar()
        self.subject_var.set(name)

        self.code = code

        self.create_widgets()

        self.grab_set()
        self.button_ok.focus_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind('<Escape>', self.cancel)

        self.wait_window()

    def create_widgets(self):
        if self.name == '':
            self.feedback_type = 'General'

            frame_general = Frame(self)
            frame_general.pack(fill=X)

            Label(frame_general, text='Subject: ').pack(side=LEFT, pady=10)

            Entry(
                frame_general,
                textvariable=self.subject_var,
                width=60
            ).pack(side=LEFT)
        else:
            self.feedback_type = 'Problem'

        # main feedback UI
        Label(self, text='Feedback: ').pack(anchor=W)

        frame_main = Frame(self, borderwidth=2)
        frame_main.pack(expand=TRUE, fill=BOTH)

        text = Text(frame_main, wrap=WORD, relief=SUNKEN)
        text.pack(side=LEFT)

        scrollbar = Scrollbar(frame_main)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)

        self.text = text

        # buttons
        frame_buttons = Frame(self)
        frame_buttons.pack()

        self.button_ok = Button(frame_buttons, text='OK', command=self.ok)
        self.button_ok.pack(side=LEFT, expand=1)

        self.button_cancel = Button(
            frame_buttons,
            text='Cancel',
            command=self.cancel
        )
        self.button_cancel.pack(side=LEFT, expand=1)

    def ok(self, event=None):
        values = {'problem_name': self.subject_var.get(),
                  'type': self.feedback_type,
                  'code_text': self.code,
                  'feedback': self.text.get(1.0, END)}
        try:
            data = urllib.parse.urlencode(values)
            req = urllib.request.Request(URL, data)
            response = urllib.request.urlopen(req)
            the_page = response.read()
            if 'Feedback not accepted' in the_page:
                tkinter.messagebox.showerror('Feedback Error',
                                             'Feedback not accepted')
        except:
            tkinter.messagebox.showerror('Feedback Error',
                                         'Cannot upload feedback')
        self.destroy()

    def cancel(self, event=None):
        self.destroy()
