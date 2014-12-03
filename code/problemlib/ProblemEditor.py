
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

## A window for editing the test code for a tutorial problem.
## Inherits from idlelib/EditorWindow

from tkinter import *

from idlelib import EditorWindow, FileList, macosxSupport

from . import ProblemBindings, ProblemIOBinding


#from TutorialData import *

class ProblemEditor(EditorWindow.EditorWindow):

    menu_specs = [
        ("file", "_File"),
        ("edit", "_Edit"),
        ("format", "F_ormat"),
    ]

    def __init__(self, parent, root, save_method=None):
        FileList.FileList(self)
        self.title = None
        EditorWindow.EditorWindow.__init__(self,  root=root)
        self.io = io = ProblemIOBinding.ProblemIOBinding(self)
        io.set_filename_change_hook(self.filename_change_hook)
        self.save_method = save_method

        self.parent = parent
        self.root = root
        self.menubar.entryconfig(1, state=DISABLED)
        self.fill_menus(menudefs=ProblemBindings.menudefs,
                        keydefs={})
        self.text.tag_config("orange", background="orange")
        self.filename = ''
        self.dirname = ''
        self.opendialog = None
        self.top.protocol("WM_DELETE_WINDOW", self.close_event)

    def close_event(self, _event=None):
        pass

    def saved_change_hook(self):
        if self.title:
            self.set_the_title(self.title)
        else:
            self.set_the_title('Unknown')

    def set_the_title(self, title):
        if not self.get_saved():
            title = "*%s*" % title
        self.top.wm_title('Problem Code Editor: ' + title)

    def set_title(self, title): 
        self.title = title
        self.set_the_title(title)

    def update_recent_files_list(self, new_file=None):
        pass

    def get_text(self):
        return self.text.get(1.0, END)

    def error_line(self, line):
        self.error = True
        start = "%d.0" % line
        end = "%d.0 lineend" % line
        text = self.text
        text.tag_add("ERROR", start, end)
        


    def createmenubar(self):
        mbar = self.menubar
        self.menudict = menudict = {}
        for name, label in self.menu_specs:
            underline, label = EditorWindow.prepstr(label)
            menudict[name] = menu = Menu(mbar, name=name)
            mbar.add_cascade(label=label, menu=menu, underline=underline)

        if macosxSupport.runningAsOSXApp():
            # Insert the application menu
            menudict['application'] = menu = Menu(mbar, name='apple')
            mbar.add_cascade(label='IDLE', menu=menu)


