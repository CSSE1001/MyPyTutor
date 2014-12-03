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

## An application for creating and editing tutorial problems.

import os, sys
from tkinter import *
import tkinter.filedialog
import problemlib.ProblemEditor as ProblemEditor
import tkinter.messagebox  
import tutorlib.fontChooser as tut_fontchooser
import tutorlib.Output as tut_output
import tutorlib.StdOutErr as tut_out
import problemlib.htmlchecker as htmlchecker
import problemlib.Configuration as Configuration
import tutorlib.TutorialInterface as tut_interface


class StatusBar(Frame):

    def __init__(self, master, line_var, col_var):
        Frame.__init__(self, master)
        Label(self, bd=1, relief=SUNKEN, textvariable=col_var).pack(side=RIGHT)
        Label(self, bd=1, relief=SUNKEN, textvariable=line_var).pack(side=RIGHT)

class Editor(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.text = Text(self, height = 30, wrap=WORD)
        self.text.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

    def update_font(self, font_size):
        self.text.config(font = ('courier', 
                                 font_size, 
                                 'normal', 'roman'))   

class ProblemsApp():
    def __init__(self, master=None):
        master.title("Problem Editor: Untitled")
        self.config = Configuration.Configuration()
        self.master = master
        # the HTML editor
        self.editor = Editor(master)
        self.editor.pack()
        menubar = Menu(master)
        master.config(menu=menubar)
        # the code editor
        self.test_editor = \
            ProblemEditor.ProblemEditor(self, self.master, 
                                        save_method = self.save_file)
        self.editor.update_font(self.config.get_fontsize())
        self.line_var = StringVar()
        self.line_var.set('Ln: 1')
        self.col_var = StringVar()
        self.col_var.set('Col: 0')
        StatusBar(master, self.line_var, self.col_var).pack(anchor=E)
        self.editor.text.bind("<Button-1>", self.b1_callback)
        self.editor.after_idle(self.b1_callback)

        self.output = tut_output.Output(master, 
                                        int(self.config.get_fontsize())-1, 10)
        self.output.pack()

        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_separator()
        filemenu.add_command(label="Save", command=self.save_file, 
                             accelerator="Ctrl+S")
        filemenu.add_command(label="Save As", command=self.save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label="Close", command=self.close_event)
        filemenu.add_command(label="Exit", command=self.close_event)

        widget = self.editor.text
        editmenu = Menu(menubar)
        menubar.add_cascade(label="Edit", menu=editmenu)
        editmenu.add_command(label="Cut   Ctrl+X", 
                             command=lambda: widget.event_generate("<<Cut>>"))
        editmenu.add_command(label="Copy   Ctrl+C", 
                             command=lambda: widget.event_generate("<<Copy>>"))
        editmenu.add_command(label="Paste   Ctrl+V", 
                             command=lambda: widget.event_generate("<<Paste>>"))
        editmenu.add_command(label="Select All   Ctrl+/",  
                             command=self.select_all)

        editmenu.add_separator()

        checkmenu = Menu(menubar)
        menubar.add_cascade(label="Check", menu=checkmenu)
        checkmenu.add_command(label="Check Problem Syntax", 
                              command=self.check_syntax)

        optionsmenu = Menu(menubar)
        menubar.add_cascade(label="Options", menu=optionsmenu)
        optionsmenu.add_command(label="Configure Fonts", 
                                command=self.configure_tut_fonts)
        optionsmenu.add_command(label="Configure Problems Database", 
                                command=self.configure_tut_db)


        self.file = None
        self.editor.text.bind('<<Modified>>', self.been_modified)
        self.master.bind('<Control-s>', self.save_file) 
        self.master.protocol("WM_DELETE_WINDOW", self.close_event)
        self.db_dir = self.config.get_db_dir()
        if self.db_dir == '':
            self.configure_tut_db()
        trans = tut_interface.Trans(77213)
        self.parser = tut_interface.TutParser(trans)
        self.htmlcheck = htmlchecker.HTMLChecker()
        sys.stdout = tut_out.StdOut(self.output)
        sys.stderr = tut_out.StdErr(self.output)

    def select_all(self):
        self.editor.text.tag_add(SEL, 1.0, END)

    def b1_callback(self, event=None):
        line, col = self.editor.text.index(INSERT).split('.')
        self.line_var.set('Ln: %s' % line)
        self.col_var.set('Col: %s' % col)

    def check_syntax(self):
        """Check that the required subset of HTML tags are used and
        that the test code parses. If all goes well the information
        is dumped for human checking.
        """

        self.output.clear_text()
        text_data = self.editor.text.get(1.0, END)
        test_data = self.test_editor.text.get(1.0, END)
        if not (text_data+test_data):
            return
        print('Checking Syntax ...')
        print('Checking HTML ...', end=' ')
        self.htmlcheck.reset()
        self.htmlcheck.feed(text_data)
        if not self.htmlcheck.is_ok():
            print('\nSyntax Check Failed', file=sys.stderr)
            return
        else:
            print('OK')
        print('Checking Test Code ...', end=' ')
        text = text_data+'#{TestCode}#\n'+test_data
        data = self.parser.parse(text, True, False)
        if data:
            print('OK')
            print() 
            for key in data:
                if key != 'TestCode':
                    print(key+':')
                    print(data[key])
            for test in data['TestCode']:
                print('----- Test -----')
                for tkey in test:
                    print('----- '+tkey+':')
                    print(test[tkey])
 
        else:
            print('\nSyntax Check Failed', file=sys.stderr)

    def configure_tut_fonts(self):
        result = \
            tut_fontchooser.FontChooser(self.master, self,
                                        (self.config.get_fontname(), 
                                         self.config.get_fontsize())).result
        if result:
            self.config.set_font(result[0], result[1])
            self.editor.update_font(int(result[1]))
            self.output.update_font(int(result[1])-1)
    
    def configure_tut_db(self):
        folder = tkinter.filedialog.askdirectory(title='Choose Problem Database Folder')
        if folder:
            self.config.set_db_dir(folder)
            self.db_dir = folder


    def close_event(self, _e = None):
        if self.editor.text.edit_modified() or not self.test_editor.get_saved():
            fsave = tkinter.messagebox.askquestion("Save Changes?", 
                                             "Do you want to save changes?")
            if str(fsave) == 'yes':
                if self.file:
                    self.save_file()
                    self.master.destroy()
                elif self.save_as_file():
                    self.master.destroy()
            else:
                self.master.destroy()
        else:
            self.master.destroy()

    def been_modified(self, _evt):
        if self.file:
            self.master.title("Problem Editor: *"+self.file+'*')
        else:
            self.master.title("Problem Editor: *Untitled*")

    def open_file(self):
        if self.file and (self.editor.text.edit_modified() or \
                              not self.test_editor.get_saved()):
            fsave = tkinter.messagebox.askquestion("Save Changes?",
                                             "Do you want to save changes?")
            if str(fsave) =='yes':
                if not self.save_file():
                    return
        self.file = tkinter.filedialog.askopenfilename(initialdir = self.db_dir,
                                                 defaultextension='.tut')
        if self.file:
            fid = open(self.file, 'U')
            text = fid.read()
            fid.close()
            code_split = text.split('#{TestCode}#\n')
            self.editor.text.delete(1.0, END)
            self.editor.text.insert(END, code_split[0])
            self.editor.text.edit_modified(0)
            self.test_editor.text.delete(1.0, END)
            self.test_editor.text.insert(END, code_split[1])
            self.test_editor.set_saved(1)
            self.master.title("Problem Editor: "+self.file)
            self.test_editor.set_title(self.file)

    def new_file(self):
        if self.file and (self.editor.text.edit_modified() or \
                              not self.test_editor.get_saved()):
            fsave = tkinter.messagebox.askquestion("Save Changes?", 
                                             "Do you want to save changes?")
            if str(fsave) =='yes':
                if not self.save_file():
                    return
        self.editor.text.delete(1.0, END)
        self.test_editor.text.delete(1.0, END)
        self.test_editor.set_saved(1)
        self.master.title("Problem Editor: Untitled")
        self.file = None

    def save_file(self, _event=None):
        if not self.file:
            tut_file = tkinter.filedialog.asksaveasfilename(initialdir = self.db_dir,
                                                      defaultextension='.tut')
            if tut_file:
                self.file = tut_file
            else:
                return False            
        self.editor.text.edit_modified(0)
        self.test_editor.set_saved(1)
        fid = open(self.file, 'w')
        data = self.editor.text.get(1.0, END)
        fid.write(data)
        data = self.test_editor.text.get(1.0, END)
        fid.write('#{TestCode}#\n'+data)

        fid.close()
        self.master.title("Problem Editor: "+self.file)
        return True

    def save_as_file(self):
        saved = self.file
        self.file = None
        if not self.save_file():
            self.file = saved

def main():
    root = Tk()
    ProblemsApp(root)
    root.mainloop()
    
if __name__ == '__main__': 
    main()
