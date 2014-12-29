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

# This defines the code edit window - it inherits from
# idlelib/EditorWindow and so has the same look and feel

import os
from tkinter import *

from idlelib import EditorWindow, macosxSupport
import tutorlib.editor.bindings as Bindings  # consistent naming with idlelib
from tutorlib.editor.io_binding import TutorIOBinding
from tutorlib.gui.aboutdialog import TutAboutDialog
from tutorlib.gui.helpdialog import HelpDialog
import tkinter.filedialog
import tkinter.messagebox


class TutorEditor(EditorWindow.EditorWindow):
    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("format", "F_ormat"),
        ("check", "_Check"),
        ("options", "_Options"),
        ("windows", "_Windows"),
        ("help", "_Help"),
    ]

    Bindings = Bindings

    def __init__(self, parent, flist=None, root=None,
                 filename=None, online=False):

        # Support for Python >= 2.7.7 (TODO find a better way)
        if hasattr(macosxSupport, "_initializeTkVariantTests") and macosxSupport._tk_type is None:
            macosxSupport._initializeTkVariantTests(root)

        if online:
            self.menu_specs.insert(4, ("online", "_Online"))

        EditorWindow.EditorWindow.__init__(self, root=root, filename=filename)

        self.io = TutorIOBinding(self)
        self.io.set_filename_change_hook(self.filename_change_hook)

        self.parent = parent
        self.root = root

        # TODO: I have absolutely no idea why some of these events feel the
        # TODO: need to break out of the tk event loop (by return 'break',
        # TODO: naturally...stupid tk)
        # TODO: Because I don't want to break anything, I've left them as is
        # TODO: for now, but it's worth looking into this later
        self.text.bind("<<load-from>>", self.load_from_event)
        self.text.bind("<<revert>>", self.revert_event)
        self.text.bind("<<check>>", self.check_event)
        self.text.bind("<<about-tutor>>", self.about)
        self.text.bind("<<help-tutor>>", self.help)
        self.text.bind("<F5>", self.check_event)
        self.text.bind("<F6>", self.submit_answer_event)

        if online:
            self.text.bind("<<login>>", lambda e: self.parent.login())
            self.text.bind("<<logout>>", lambda e: self.parent.logout())
            self.text.bind(
                "<<change_password>>", lambda e: self.parent.change_password()
            )
            self.text.bind(
                "<<upload_answer>>", lambda e: self.parent.upload_answer()
            )
            self.text.bind(
                "<<download_answer>>", lambda e: self.parent.download_answer()
            )
            self.text.bind("<<submit_answer>>", self.submit_answer_event)
            self.text.bind(
                "<<show_submit>>", lambda e: self.parent.show_submit()
            )

        self.text.tag_config("orange", background="orange")

        self.filename = ''
        self.dirname = ''
        self.opendialog = None
        self.menudict['file'].delete(0, 1)

    def update_font(self, font_size):
        self.text.config(
            font=('courier', str(int(font_size)+1), 'normal', 'roman')
        )

    def revert_event(self, e):
        reply = self.possiblysave("Save on Revert")
        if str(reply) == "cancel":
            return
        self.preload(self.parent.get_preloaded())
        self.text.edit_modified(0)

    def load_from_event(self, e):
        file = tkinter.filedialog.askopenfile(title='Load From File')
        if file:
            self.preload(file.read())
            file.close()
            self.text.edit_modified(1)

    def check_event(self, e):
        self.parent.run_tests()
        return "break"

    def submit_answer_event(self, e):
        self.parent.submit_answer()
        return "break"

    def possiblysave(self, title):
        reply = "no"
        if self.io:
            if not self.get_saved():
                if self.top.state() != 'normal':
                    self.top.deiconify()
                self.top.lift()
                message = ("Do you want to save %s?" %
                           (self.filename or "this untitled document"))
                m = tkinter.messagebox.Message(
                    title=title,
                    message=message,
                    icon=tkinter.messagebox.QUESTION,
                    type=tkinter.messagebox.YESNOCANCEL,
                    master=self.text)
                reply = m.show()
                if reply == "yes":
                    self.io.save(None)
                    if not self.get_saved():
                        reply = "cancel"
        return reply

    def close(self):
        #print 'closing'
        reply = self.maybesave()
        if str(reply) != "cancel":
            self._close()
        return reply

    def reset(self, filename, default):
        self.filename = filename
        if os.path.exists(filename):
            self.io.open(editFile=filename)
        else:
            self.preload(default)
            self.io.set_filename(filename)

    def preload(self, text):
        self.text.delete(1.0, END)
        if text:
            self.text.insert(END, text)
        #self.set_saved(1)

    def get_text(self):
        return self.text.get(1.0, END)

    def error_line(self, line):
        self.error = True
        start = "%d.0" % line
        end = "%d.0 lineend" % line
        text = self.text
        text.tag_add("ERROR", start, end)

    def quit(self):
        #self.root.destroy()
        self.parent.quit_editor()

    def about(self, e):
        TutAboutDialog(self.root, "About Tutor")

    def help(self, e):
        HelpDialog(self.root, "Help")
