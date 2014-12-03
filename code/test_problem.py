#!/usr/bin/env python

## A Python Tutorial System
## Copyright (C) 2009  Peter Robinson <pjr@itee.uq.edu.au>
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

## An application for testing tutorial problems.

import threading, thread
import time
from Tkinter import * 
import os, sys

import tutorlib.Output as tut_output
import tutorlib.Tutorial as tut_tutorial
import tutorlib.TutorEditor as tut_editor
import tutorlib.StdOutErr as tut_stdouterr
import problemlib.Configuration as tut_config
import tutorlib.TutorialInterface as tut_interface

import tutorlib.fontChooser
import tkFileDialog





class Toolbar(Frame):
    def __init__(self, parent, master=None):
        Frame.__init__(self, master)
        self.parent = parent
        self.hintbutton = Button(self, text="Next Hint", 
                                command=self.parent.showhint)

    def set_hints(self, flag):
        if flag:
            self.hintbutton.pack(side = LEFT)
        else:
            self.hintbutton.pack_forget()
        



class TestProblemApp():
    def __init__(self, master=None):
        master.title("Test Tutorial Problem")
        self.master = master
        self.config = tut_config.Configuration()
        self.editor = None 
        self.output = tut_output.Output(master, int(self.config.get_fontsize()),10)
        self.tut = tut_tutorial.Tutorial(master, (self.config.get_fontname(), 
                                                  self.config.get_fontsize()),30)
        self.tut.pack(fill=BOTH, expand=1)
        self.toolbar = Toolbar(self, master)
        self.toolbar.pack()
        self.output.pack()
        self.tut_interface = \
            tut_interface.TutorialInterface(master, self, self.output, enc=False)
        menubar = Menu(master)
        sectionmenu = Menu(menubar, tearoff=0)
        sectionmenu.add_command(label="Open", 
                                command=self.open_tutorial)
        sectionmenu.add_command(label="Reload  Ctrl+R", 
                                command=self.reload)
        sectionmenu.add_command(label="Reload and Clear", 
                                command=self.reload_clear)
        sectionmenu.add_separator()
        sectionmenu.add_command(label="Close", command=self.close_event)
        sectionmenu.add_command(label="Exit", command=self.close_event)

        menubar.add_cascade(label="File", menu=sectionmenu)
        master.config(menu=menubar)
        sys.stdout = tut_stdouterr.StdOut(self.output)
        sys.stderr = tut_stdouterr.StdErr(self.output)
        self.db_dir = self.config.get_db_dir()
        self.tut.set_directory(self.db_dir)
        self.master.protocol("WM_DELETE_WINDOW", self.close_event)
        self.master.bind('<Control-r>', self.reload)
        self.file = None

    def open_tutorial(self):

        self.file = tkFileDialog.askopenfilename(initialdir = self.db_dir,

                                                 defaultextension='.tut')
        self.reload_file(True)

    def reload(self, _event=None):
        self.reload_file(False)

    def reload_clear(self):
        self.reload_file(True)

    def reload_file(self, do_clear):
        if self.file:
            self.output.clear_text()
            if not self.editor:
                self.editor = tut_editor.TutorEditor(self, root=self.master)
                fontsize = self.config.get_fontsize()
                self.output.update_font(int(fontsize))
                self.editor.update_font(fontsize)
                self.tut_interface.set_editor(self.editor)
            self.master.title("Test Tutorial Problem: "+self.file)
            self.tut_interface.load_data(self.file, self.file)

            if self.tut_interface.get_text():
                try:
                    self.tut.add_text(self.tut_interface.get_text())
                    if do_clear:
                        self.editor.preload(self.tut_interface.get_preloaded())
                    self.editor.text.edit_modified(0)
                    self.toolbar.set_hints(self.tut_interface.get_hints())
                except Exception, ex_obj:
                    print >> sys.stderr, 'Exception: '+ str(ex_obj)
        
 
    def close_event(self, _e = None):
        if self.editor:
            result = self.editor.close()
            if str(result) == 'yes':
                self.master.destroy()
        else:
            self.master.destroy()



    def run_tests(self):
        self.tut_interface.run_tests(self.editor.get_text())


    def showhint(self):
        hint = self.tut_interface.get_next_hint()
        if hint:
            self.tut.show_hint(hint)


def main():
    root = Tk()
    TestProblemApp(root)
    root.mainloop()
    
if __name__ == '__main__': 
    main()
