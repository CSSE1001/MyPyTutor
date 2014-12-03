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

## For initial configuration

from Tkinter import *
import tkFileDialog
import tkMessageBox
import os

label_text = \
"Before using MyPyTutor or when adding a new tutorial you need to set two folders.\nThe tutorial folder contains the tutorial problems that you should have already installed.\nThe answers folder is used to store your (partial) answers. When you save an answer it is put in this folder and when you choose a problem to work on that you have saved previously, your code will be automatically loaded.\n The tutorial name can be supplied (default the tutorial folder name)."


class TutorConfigure( Toplevel ):

    def __init__(self, master, parent):
        Toplevel.__init__( self, master)
        self.master = master
        self.parent = parent
        self.result = None
        self.title('Tutorial Configuration')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        info = Label(self, text=label_text, wraplength = 400, justify = LEFT)
        info.pack()
        tut_frame=Frame(self, relief=SUNKEN,border=3)
        tut_frame.pack(side=TOP,expand=TRUE,fill=BOTH,pady=20)
        Label(tut_frame, text='Tutorial Folder: ').pack(side=LEFT)
        self.tut_entry = Entry(tut_frame, width=50)
        self.tut_entry.pack(side=LEFT)
        Button(tut_frame, text='Select', command = self.select_tut_dir).pack(side=LEFT,padx=10)

        ans_frame=Frame(self, relief=SUNKEN,border=3)
        ans_frame.pack(side=TOP,expand=TRUE,fill=BOTH,pady=20)
        Label(ans_frame, text='Answers Folder:').pack(side=LEFT)
        self.ans_entry = Entry(ans_frame, width=50)
        self.ans_entry.pack(side=LEFT)
        Button(ans_frame, text='Select', command = self.select_ans_dir).pack(side=LEFT,padx=10)
        name_frame=Frame(self, relief=SUNKEN,border=3)
        name_frame.pack(side=TOP,expand=TRUE,fill=BOTH,pady=20)
        Label(name_frame, text='Tutorial Name: ').pack(side=LEFT)
        self.name_entry = Entry(name_frame, width=50)
        self.name_entry.pack(side=LEFT)

        buttonFrame = Frame(self)
        buttonFrame.pack(side=TOP,expand=TRUE,fill=BOTH)
        okButton = Button(buttonFrame, text="OK", command=self.ok)
        cancelButton = Button(buttonFrame, text="Cancel", command=self.cancel)
        okButton.pack(side=LEFT,expand=TRUE)
        cancelButton.pack(side=LEFT,expand=TRUE)
        self.wait_window(self)

    def select_tut_dir(self):
        self.tut_entry.delete(0,END)
        dir = tkFileDialog.askdirectory(title='Choose Tutorial Folder')
        if dir:
           self.tut_entry.insert(0, dir)
           if self.name_entry.get() == '':
               self.name_entry.insert(0, os.path.basename(dir))
 
    def select_ans_dir(self):
        self.ans_entry.delete(0,END)
        dir = tkFileDialog.askdirectory(title='Choose Answers Folder')
        if dir:
           self.ans_entry.insert(0, dir)
 
    def destroy(self):
        Toplevel.destroy(self)

    def ok(self, e = None):
        tut_dir = self.tut_entry.get()
        ans_dir = self.ans_entry.get()
        name = self.name_entry.get()
        if not (os.path.exists(tut_dir) and \
                    os.path.exists(os.path.join(tut_dir, 'tutorials.txt')) and \
                    os.path.exists(os.path.join(tut_dir, 'config.txt'))):
            tkMessageBox.showerror('Tutorial Configuration Error', 
                                   'Invalid tutorial folder.')
        elif ans_dir == '':
            tkMessageBox.showerror('Tutorial Configuration Error', 
                                   'Invalid answers folder.')
        else:    
            self.result = tut_dir, self.ans_entry.get(), name
            self.withdraw()
            self.update_idletasks()
            self.cancel()

    def cancel(self, e = None):
        self.master.focus_set()
        self.destroy()
        
    def OnListFontButtonRelease(self,event):
        font = self.listFontName.get(ANCHOR)
        self.fontName.set(font.lower())
        self.SetFontSample()

    def SetFontSample(self,event=None):
        fontName=self.fontName.get()
        fontWeight=tkFont.NORMAL
        self.labelFontNameTitle.config(text='Font Face : '+fontName)
        self.editFont.config(size=self.fontSize.get(),
                             weight=fontWeight,family=fontName)




