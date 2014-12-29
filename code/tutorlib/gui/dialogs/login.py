
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

from tkinter import *
import tkinter.messagebox

from tutorlib.gui.dialogs.dialog import Dialog


class LoginDialog(Dialog):
    def __init__(self, parent, callback, title="Login"):
        # set up vars needed to create widgets
        self.user = StringVar()
        self.password = StringVar()

        self.callback = callback

        # defer remaining setup to parent
        super().__init__(parent, title, allow_cancel=True)

        # change the default focus to the username field
        self.user_entry.focus_set()

    def create_widgets(self):
        # username
        userframe = Frame(self.frame_top)
        userframe.pack(expand=TRUE, fill=X)

        Label(
            userframe,
            text='Username: ',
        ).pack(side=LEFT, anchor=W, expand=TRUE)

        self.user_entry = Entry(userframe, textvariable=self.user, width=20)
        self.user_entry.pack(side=LEFT)

        # password
        passframe = Frame(self.frame_top)
        passframe.pack(expand=TRUE, fill=X)

        Label(
            passframe,
            text='Password: ',
        ).pack(side=LEFT, anchor=W, expand=TRUE)

        pass_entry = Entry(
            passframe,
            textvariable=self.password,
            width=20,
            show="*",
        )
        pass_entry.pack(side=LEFT)

    def ok(self, event=None):
        user = self.user.get().strip()
        password = self.password.get()
        result = self.callback(user, password)
        if result is None:
            self.destroy()
        elif result:
            self.destroy()
        else:
            tkinter.messagebox.showerror(
                'Login Error', 'Incorrect user name or password'
            )
            self.user.set('')
            self.password.set('')


class ChangePasswordDialog(Dialog):
    def __init__(self, parent, title='Change Password'):
        # set up vars needed to create widgets
        self.password0 = StringVar()
        self.password1 = StringVar()
        self.password2 = StringVar()

        self.success = False

        # defer remaining setup to parent
        super().__init__(parent, title)

        # change the default focus to the current password field
        self.pass_entry.focus_set()

    def create_widgets(self):
        # current, new, and confirmed new passwords
        labels = ['Password: ', 'New Password: ', 'New Password: ']
        variables = [self.password0, self.password1, self.password2]
        entries = []

        for lbl, var in zip(labels, variables):
            frame = Frame(self.frame_top)
            frame.pack(expand=TRUE, fill=X)

            Label(frame, text=lbl).pack(side=LEFT, anchor=W, expand=TRUE)

            entry = Entry(frame, textvariable=var, width=20, show="*")
            entry.pack(side=LEFT)
            entries.append(entry)

        self.pass_entry = entries[0]

    def ok(self, event=None):
        if self.password1.get() != self.password2.get():
            tkinter.messagebox.showerror(
                'Change Password Error', "New passwords don't match."
            )
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
            return
        if len(self.password1.get()) < 4:
            tkinter.messagebox.showerror(
                'Change Password Error', "New passwords is too short."
            )
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
            return

        result = self.parent.do_change_password(
            self.password0.get(), self.password1.get()
        )
        if result is None:
            self.destroy()
        elif result:
            self.success = True
            self.destroy()
        else:
            tkinter.messagebox.showerror(
                'Change Password Error',
                'Incorrect password or new password failure.',
            )
            self.password0.set('')
            self.password1.set('')
            self.password2.set('')
