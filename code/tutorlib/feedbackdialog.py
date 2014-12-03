
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
        self.configure(borderwidth=5)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+30,
                                  parent.winfo_rooty()+30))
        self.name = name
        self.subject_var = StringVar()
        self.subject_var.set(name)
        self.code = code
        self.CreateWidgets()
        self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Cancel)
        self.parent = parent
        self.buttonOk.focus_set()
        self.bind('<Escape>', self.Cancel)
        self.wait_window()

    def CreateWidgets(self):
        if self.name == '':
            self.feedback_type = 'General'
            generalFrame = Frame(self)
            generalFrame.pack(fill=X)
            Label(generalFrame, text='Subject: ').pack(side=LEFT, pady=10)
            Entry(generalFrame,
                  textvariable=self.subject_var, width=60).pack(side=LEFT)
        else:
            self.feedback_type = 'Problem'
        Label(self, text='Feedback: ').pack(anchor=W)
        frameMain = Frame(self, borderwidth=2)
        frameMain.pack(expand=TRUE, fill=BOTH)
        text = Text(frameMain, wrap=WORD, relief=SUNKEN)
        text.pack(side=LEFT)
        scrollbar = Scrollbar(frameMain)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=text.yview)
        self.text = text
        frameButtons = Frame(self)
        frameButtons.pack()
        self.buttonOk = Button(frameButtons, text='OK',
                               command=self.Ok)
        self.buttonOk.pack(side=LEFT, expand=1)
        self.buttonCancel = Button(frameButtons, text='Cancel',
                                   command=self.Cancel)
        self.buttonCancel.pack(side=LEFT, expand=1)

    def Ok(self, event=None):
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

    def Cancel(self, event=None):
        self.destroy()
