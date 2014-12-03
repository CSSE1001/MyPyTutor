#!/usr/bin/env python3

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


## An application for creating tutorials by collecting together
## individual problems.

from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
import os
import tutorlib.TutorialInterface as tut_interface
import problemlib.Configuration as Configuration
from create_tutorial import generate_text, parse_tutorial

class GenerateDialog(Toplevel):
    def __init__(self, master, parent):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.result = None
        self.title('Generate Tutorials')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()

        Label(self, text='Tutorial Base Folder:').pack(anchor = 'w')
        destination_frame = Frame(self, relief=SUNKEN)
        destination_frame.pack()
        self.destination_var = StringVar()
        self.cwd = os.getcwd()
        self.destination_var.set(self.cwd)
        self.destination = Entry(destination_frame, 
                                 textvariable=self.destination_var, width=40)
        self.destination.pack(side=LEFT)
        self.destination_button = Button(destination_frame, text='Search', 
                                         command = self.destination_cb)
        self.destination_button.pack(side=LEFT)

        Label(self, text='Tutorial Folder:').pack(anchor = 'w')
        self.folder_var = StringVar()
        self.folder = Entry(self, 
                            textvariable=self.folder_var,width=40)
        self.folder.pack(anchor = 'w')
        button_frame = Frame(self)
        button_frame.pack()
        Button(button_frame, text='Generate', 
               command=self.generate_cb).pack(side=LEFT)
        Button(button_frame, text='Cancel', 
               command=self.cancel).pack(side=LEFT)
        self.wait_window(self)

    def destination_cb(self):
        dest_dir = tkinter.filedialog.askdirectory(initialdir=self.cwd)
        if dest_dir:
            self.destination_var.set(dest_dir)

    def destroy(self):
        Toplevel.destroy(self)

    def generate_cb(self):
        self.result = os.path.join(self.destination_var.get(), 
                                   self.folder_var.get())
        self.withdraw()
        self.update_idletasks()
        self.cancel()
        self.destroy()

    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class TextWidget(Frame):
    def __init__(self, master, height):
        Frame.__init__(self, master)
        self.text = Text(self, height = height, wrap=WORD)
        self.text.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

    def update_fonts(self, font_name, font_size):
        self.text.config(font = (font_name, 
                                 font_size, 
                                 'normal', 'roman'))   



class CreateTutorialApp():
    def __init__(self, master=None):
        master.title("Create Tutorial: Untitled")
        self.config = Configuration.Configuration()
        self.master = master
        self.editor = TextWidget(master, 30)
        self.editor.pack()
        self.output = TextWidget(master, 10)
        self.output.text.tag_config("red", foreground="red")
        self.output.text.tag_config("blue", foreground="blue")

        self.output.pack()
        menubar = Menu(master)
        master.config(menu=menubar)
        fontname = self.config.get_fontname()
        fontsize = self.config.get_fontsize()
        self.editor.update_fonts(fontname, fontsize) 
        self.output.update_fonts(fontname, fontsize)  
        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save  Ctrl+S", command=self.save_file)
        filemenu.add_command(label="Save As", command=self.save_as_file)

        generatemenu = Menu(menubar)
        menubar.add_cascade(label="Generate Tutorial", menu=generatemenu)
        generatemenu.add_command(label="Check", command=self.check)
        generatemenu.add_command(label="Generate", command=self.generate)
        self.file = None
        self.editor.text.bind('<<Modified>>', self._been_modified)
        self.master.protocol("WM_DELETE_WINDOW", self.close_event)
        self.master.bind('<Control-s>', self.save_file) 
        self.db_dir = self.config.get_db_dir()

    def close_event(self, _e = None):
        if self.editor.text.edit_modified():
            fsave = tkinter.messagebox.askquestion("Save Changes?",  
                                             "Do you want to save changes?")
            if str(fsave)=='yes':
                if self.file:
                    self.save_file()
                    self.master.destroy()
                elif self.save_as_file():
                    self.master.destroy()
            else:
                self.master.destroy()
        else:
            self.master.destroy()

    def _been_modified(self, _evt):
        if self.file:
            self.master.title("Tutorial Editor: *"+self.file+'*')
        else:
            self.master.title("Tutorial Editor: *Untitled*")

    def open_file(self):
        self.output.text.delete(1.0, END)
        if self.editor.text.edit_modified():
            fsave = tkinter.messagebox.askquestion("Save Changes?", 
                                             "Do you want to save changes?")
            if str(fsave)=='yes':
                if not self.save_file():
                    return
        self.file = tkinter.filedialog.askopenfilename(initialdir = self.db_dir)
        if self.file:
            fid = open(self.file, 'U')
            text = fid.read()
            fid.close()
            self.editor.text.delete(1.0, END)
            self.editor.text.insert(END, text)
            self.editor.text.edit_modified(0)
            self.master.title("Tutorial Editor: "+self.file)

    def save_file(self, _event=None):
        if not self.file:
            sfile = tkinter.filedialog.asksaveasfilename(initialdir = self.db_dir)
            if sfile:
                self.file = sfile
            else:
                return False
        self.editor.text.edit_modified(0)
        fid = open(self.file, 'w')
        data = self.editor.text.get(1.0, END).strip('\n')+'\n'
        fid.write(data)
        fid.close()
        self.master.title("Tutorial Editor: "+self.file)
        return True

    def save_as_file(self):
        saved = self.file
        self.file = None
        if not self.save_file():
            self.file = saved

    def check(self):
        self.output.text.delete(1.0, END)
        data = self.editor.text.get(1.0, END)
        return parse_tutorial(data)

    def generate(self):
        self.output.text.delete(1.0, END)
        result = GenerateDialog(self.master, self).result
        if not result:
            return
        generate_text(self.editor.text.get(1.0, END), result, self.db_dir)


def main():
    root = Tk()
    CreateTutorialApp(root)
    root.mainloop()


if __name__ == '__main__': 
    main()
