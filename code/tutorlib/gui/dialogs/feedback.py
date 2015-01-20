
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

import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.parse
import urllib.error

from tutorlib.gui.dialogs.dialog import Dialog
import tutorlib.gui.utils.messagebox as tkmessagebox

## The URL for the feedback CGI script.
URL = 'http://csse1001.uqcloud.net/mpt/cgi-bin/feedback.py'


class FeedbackDialog(Dialog):
    def __init__(self, parent, title, name='', code=''):
        # set up vars needed to create widgets
        self.name = name
        self.subject_var = tk.StringVar()
        self.subject_var.set(name)

        self.code = code

        # defer remaining setup to parent
        super().__init__(parent, title, allow_cancel=True)

    def create_widgets(self):
        if self.name == '':
            self.feedback_type = 'General'

            frame_general = ttk.Frame(self.frame_top)
            frame_general.pack(fill=tk.X)

            ttk.Label(
                frame_general, text='Subject: '
            ).pack(side=tk.LEFT, pady=10)

            ttk.Entry(
                frame_general,
                textvariable=self.subject_var,
                width=60
            ).pack(side=tk.LEFT)
        else:
            self.feedback_type = 'Problem'

        # main feedback UI
        ttk.Label(self.frame_top, text='Feedback: ').pack(anchor=tk.W)

        frame_main = ttk.Frame(self.frame_top, borderwidth=2)
        frame_main.pack(expand=tk.TRUE, fill=tk.BOTH)

        text = tk.Text(frame_main, wrap=tk.WORD, relief=tk.SUNKEN)
        text.pack(side=tk.LEFT)

        scrollbar = ttk.Scrollbar(frame_main)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)

        self.text = text

    def ok(self, event=None):
        values = {'problem_name': self.subject_var.get(),
                  'type': self.feedback_type,
                  'code_text': self.code,
                  'feedback': self.text.get(1.0, tk.END)}
        try:
            data = urllib.parse.urlencode(values)
            req = urllib.request.Request(URL, data)
            response = urllib.request.urlopen(req)
            the_page = response.read()
            if 'Feedback not accepted' in the_page:
                tkmessagebox.showerror('Feedback Error',
                                             'Feedback not accepted')
        except:
            tkmessagebox.showerror('Feedback Error',
                                         'Cannot upload feedback')

        super().ok(event=event)
