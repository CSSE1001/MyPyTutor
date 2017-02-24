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

# This defines the code edit window - it inherits from EditorWindow
# in idlelib/editor and so has the same look and feel.

import os
import tkinter as tk
import tkinter.filedialog as tkfiledialog
from idlelib import editor, macosx

from tutorlib.gui.app.menu import TutorialMenuDelegate
import tutorlib.gui.editor.bindings as Bindings  # be consistent with idlelib
from tutorlib.gui.editor.delegate import TutorEditorDelegate
from tutorlib.gui.editor.io_binding import TutorIOBinding
from tutorlib.utils.fonts import FIXED_FONT
import tutorlib.utils.messagebox as tkmessagebox


class TutorEditor(editor.EditorWindow):
    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("format", "F_ormat"),
        ("check", "_Check"),
        ("online", "_Online"),
        ("options", "_Options"),
        ("windows", "_Windows"),
        ("help", "_Help"),
    ]

    Bindings = Bindings

    def __init__(self, menu_delegate, editor_delegate, flist=None, root=None,
                 filename=None, online=False):

        # Support for Python >= 2.7.7 (TODO find a better way)
		# Changes for Python 3.6
		# The library macosxSupport was changed to macosx
		# _initializeTkVariantTests was changed to _init_tk_type
        if hasattr(macosx, "_init_tk_type") and macosx._tk_type is None:
            macosx._init_tk_type()

        super().__init__(root=root, filename=filename)

        self.io = TutorIOBinding(self)
        self.io.set_filename_change_hook(self.filename_change_hook)

        assert isinstance(menu_delegate, TutorialMenuDelegate)
        self.menu_delegate = menu_delegate

        assert isinstance(editor_delegate, TutorEditorDelegate)
        self.editor_delegate = editor_delegate

        self.root = root

        # TODO: previously, a number of these events broke out of the event
        # TODO: loop, by returning 'break'
        # TODO: this has been removed; if bugs appear, that's probably why
        noevt = lambda f: lambda e=None: f()

        self.text.bind("<<load-from>>", self.load_from)
        self.text.bind("<<revert>>", self.revert)

        self.text.bind("<<check>>", noevt(editor_delegate.check_solution))

        self.text.bind("<<login>>", noevt(menu_delegate.login))
        self.text.bind("<<logout>>", noevt(menu_delegate.logout))
        self.text.bind("<<submit_answer>>", noevt(menu_delegate.submit))
        self.text.bind("<<show_submit>>", noevt(menu_delegate.show_submissions))
        self.text.bind("<<sync_solutions>>", noevt(menu_delegate.synchronise))

        self.text.bind("<<about-tutor>>", noevt(menu_delegate.show_about_dialog))
        self.text.bind("<<help-tutor>>", noevt(menu_delegate.show_help_dialog))

        # it's less than ideal to have to bind these here, but it's proved to
        # be the safest approach in practice
        # ideally, we'd just .bind_all on tk.Tk, and capture and 'break' all
        # key bindings here, but that seems to interfere with idlelib; it
        # doesn't grab all the bindings as it should
        # my best guess (without wishing to delve too deeply) is that something
        # other than self.text is doing some of the event handling
        # anyway, we hard-code these bindings here :(
        self.text.bind("<F5>", noevt(editor_delegate.check_solution))
        self.text.bind("<F6>", noevt(menu_delegate.submit))

        self.text.config(font=FIXED_FONT)
        self.text.tag_config("orange", background="orange")

        self.tutorial = None
        self.menudict['file'].delete(0, 1)  # TODO: huh?

    ## Menu Callbacks
    # file
    def load_from(self, e):
        file = tkfiledialog.askopenfile(title='Load From File')
        if file:
            self.set_text(file.read())
            file.close()
            self.text.edit_modified(1)

    def revert(self, e):
        reply = self.possiblysave("Save on Revert")
        if str(reply) == tkmessagebox.CANCEL:
            return

        self.set_text(self.tutorial.preload_code_text)
        self.text.edit_modified(0)

    def possiblysave(self, title):
        reply = tkmessagebox.NO
        if self.io:
            if not self.get_saved():
                if self.top.state() != 'normal':
                    self.top.deiconify()
                self.top.lift()
                message = "Do you want to save {}?".format(
                    self.tutorial.answer_path
                )
                m = tkmessagebox.Message(
                    title=title,
                    message=message,
                    icon=tkmessagebox.QUESTION,
                    type=tkmessagebox.YESNOCANCEL,
                    master=self.text,
                )
                reply = m.show()
                if reply == tkmessagebox.YES:
                    self.io.save(None)
                    if not self.get_saved():
                        reply = tkmessagebox.CANCEL
        return reply

    def close(self):
        reply = self.maybesave()
        if str(reply) != tkmessagebox.CANCEL:
            self._close()
        return reply

    def reset(self, tutorial):
        self.tutorial = tutorial

        if os.path.exists(self.tutorial.answer_path):
            self.io.open(editFile=self.tutorial.answer_path)
        else:
            # only preload if no answer exists
            self.set_text(self.tutorial.preload_code_text)
            self.io.set_filename(self.tutorial.answer_path)

    def set_text(self, text):
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, text)

    def get_text(self):
        return self.text.get(1.0, tk.END)

    def error_line(self, line):
        self.error = True
        start = "%d.0" % line
        end = "%d.0 lineend" % line
        text = self.text
        text.tag_add("ERROR", start, end)

    def quit(self):
        self.editor_delegate.quit_editor()
