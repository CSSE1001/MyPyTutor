
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

from Tkinter import *

class TutAboutDialog(Toplevel):
    def __init__(self,parent,title):
        Toplevel.__init__(self, parent)
        self.configure(borderwidth=5)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+30,
                                  parent.winfo_rooty()+30))
        self.bg = "#707070"
        self.fg = "#ffffff"
        self.CreateWidgets()
        self.resizable(height=FALSE, width=FALSE)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Ok)
        self.parent = parent
        self.buttonOk.focus_set()
        self.bind('<Return>',self.Ok) #dismiss dialog
        self.bind('<Escape>',self.Ok) #dismiss dialog
        self.wait_window()

    def CreateWidgets(self):
        frameMain = Frame(self, borderwidth=2, relief=SUNKEN, bg = "#ffffaa")
        frameMain.pack(side=TOP, expand=TRUE, fill=BOTH)
        Label(frameMain, text = 'MyPyTutor: A Python Tutorial System', bg = "#ffffaa").pack(padx=10,pady=10)
        Label(frameMain, text = 'Copyright 2010 Peter Robinson', bg = "#ffffaa").pack(padx=10,pady=10)
        Label(frameMain, text = 'email: pjr@itee.uq.edu.au', bg = "#ffffaa").pack(padx=10,pady=10)
        
        frameButtons = Frame(self)
        frameButtons.pack(fill=X)
        self.buttonOk = Button(frameButtons, text='Close',
                               command=self.Ok)
        self.buttonOk.pack()

    def Ok(self, event=None):
        self.destroy()

