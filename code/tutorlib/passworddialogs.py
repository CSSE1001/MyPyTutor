
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

## Dialogs involving passwords

from Tkinter import *

import tkMessageBox

class LoginDialog(Toplevel):
    def __init__(self,parent, callback, title="Login"):
        Toplevel.__init__(self, parent.master)
        x = parent.master.winfo_rootx()
        y = parent.master.winfo_rooty()
        self.geometry("+%d+%d" % (x+20, y+20))
        self.configure(borderwidth=5)
        self.user = StringVar()
        self.password = StringVar()
        self.CreateWidgets()
        self.resizable(height=FALSE, width=FALSE)
        self.transient(parent.master)
        self.wait_visibility()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Cancel)
        self.parent = parent
        self.user_entry.focus_set()
        self.bind('<Escape>',self.Cancel)
        self.bind('<Return>',self.submit)
        self.title(title)
        self.callback = callback
        self.wait_window()

    def CreateWidgets(self):
        userframe = Frame(self)
        userframe.pack(expand=TRUE,fill=X)
        Label(userframe, text = 'Username: ').pack(side=LEFT,
                                                   anchor=W,expand=TRUE)
        self.user_entry = Entry(userframe, textvariable=self.user, width=20)
        self.user_entry.pack(side=LEFT)
        passframe = Frame(self)
        passframe.pack(expand=TRUE,fill=X)
        Label(passframe, text = 'Password: ').pack(side=LEFT,
                                                   anchor=W,expand=TRUE)
        pass_entry = Entry(passframe, textvariable=self.password, 
                           width=20, show="*")
        pass_entry.pack(side=LEFT)
        frameButtons = Frame(self)
        frameButtons.pack()
        self.buttonSubmit = Button(frameButtons, text='Submit',
                                   command=self.submit)
        self.buttonSubmit.pack(side=LEFT, expand=1)
        self.buttonCancel = Button(frameButtons, text='Cancel',
                               command=self.Cancel)
        self.buttonCancel.pack(side=LEFT,expand=1)

    def Cancel(self, event=None):
        self.destroy()

    def submit(self, event=None):
        user = self.user.get().strip()
        password = self.password.get()
        result = self.callback(user, password)
        if result == None:
            self.destroy()
        elif result:
            self.destroy()
        else:
            tkMessageBox.showerror('Login Error', 
                                   'Incorrect user name or password')
            self.user.set('')
            self.password.set('')



class ChangePasswordDialog(Toplevel):
    def __init__(self,parent):
        Toplevel.__init__(self, parent.master)
        self.configure(borderwidth=5)
        self.title("Change Password")
        self.password0 = StringVar()
        self.password1 = StringVar()
        self.password2 = StringVar()
        self.CreateWidgets()
        self.resizable(height=FALSE, width=FALSE)
        self.transient(parent.master)
        self.wait_visibility()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.Cancel)
        self.parent = parent
        self.pass_entry.focus_set()
        self.bind('<Escape>',self.Cancel)
        self.bind('<Return>',self.submit)
        #self.wait_window()
        self.success = False

    def CreateWidgets(self):
        passframe = Frame(self)
        passframe.pack(expand=TRUE,fill=X)
        Label(passframe, text = 'Password: ').pack(side=LEFT,
                                                   anchor=W,expand=TRUE)
        self.pass_entry = Entry(passframe, textvariable=self.password0, 
                                width=20, show="*")
        self.pass_entry.pack(side=LEFT)
        pass1frame = Frame(self)
        pass1frame.pack(expand=TRUE,fill=X)
        Label(pass1frame, text = 'New Password: ').pack(side=LEFT,
                                                        anchor=W,expand=TRUE)
        pass1_entry = Entry(pass1frame, textvariable=self.password1, 
                            width=20, show="*")
        pass1_entry.pack(side=LEFT)
        pass2frame = Frame(self)
        pass2frame.pack(expand=TRUE,fill=X)
        Label(pass2frame, text = 'New Password: ').pack(side=LEFT,
                                                        anchor=W,expand=TRUE)
        pass2_entry = Entry(pass2frame, textvariable=self.password2, 
                            width=20, show="*")
        pass2_entry.pack(side=LEFT)
        frameButtons = Frame(self)
        frameButtons.pack()
        self.buttonSubmit = Button(frameButtons, text='Submit',
                                   command=self.submit)
        self.buttonSubmit.pack(side=LEFT, expand=1)
        self.buttonCancel = Button(frameButtons, text='Cancel',
                               command=self.Cancel)
        self.buttonCancel.pack(side=LEFT,expand=1)

    def Cancel(self, event=None):
        self.destroy()

    def submit(self, event=None):
        if self.password1.get() != self.password2.get():
            tkMessageBox.showerror('Change Password Error', 
                                   "New passwords don't match.")
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
            return
        if len(self.password1.get()) < 4:
            tkMessageBox.showerror('Change Password Error', 
                                   "New passwords is too short.")
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
            return

 
        result = self.parent.do_change_password(self.password0.get(), 
                                                self.password1.get())
        if result == None:
            self.destroy()
        elif result:
            self.success = True
            self.destroy()
        else:
            tkMessageBox.showerror('Change Password Error', 
                                   'Incorrect password or new password failure.')
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
