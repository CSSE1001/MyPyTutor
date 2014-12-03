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

## This define IO bindings for the code edit window 
## It is a modification of idlelib/IOBinding.py

from idlelib import IOBinding
import tkinter.messagebox

class TutorIOBinding(IOBinding.IOBinding):

    def __init__(self, parent):
        IOBinding.IOBinding.__init__(self, parent)
	self.editwin = parent

    def open(self, event=None, editFile=None):
        if self.editwin.flist:
            if not editFile:
                filename = self.askopenfile()
            else:
                filename=editFile
            if filename:
                #self.editwin.flist.open(filename, self.loadfile)
                self.loadfile(filename)
            else:
                self.text.focus_set()
            return "break"
        #
        # Code for use outside IDLE:
        if self.get_saved():
            reply = self.maybesave()
            if reply == "cancel":
                self.text.focus_set()
                return "break"
        if not editFile:
            filename = self.askopenfile()
        else:
            filename=editFile
        if filename:
            self.loadfile(filename)
        else:
            self.text.focus_set()
        return "break"

    ## NOTE: maybesave is essentially the same as in idlelib/IOBinding.py
    ## but is included because of a bug to do with the reply below
    ## The original defn has reply == "yes".
    ## The problem is that the message box (sometimes) returns a tk object
    ## rather than a string - wrapping with str() fixes the problem.
    def maybesave(self):
        if self.get_saved():
            return "yes"
        message = "Do you want to save %s before closing?" % (
            self.filename or "this untitled document")
        m = tkinter.messagebox.Message(
            title="Save On Close",
            message=message,
            icon=tkinter.messagebox.QUESTION,
            type=tkinter.messagebox.YESNOCANCEL,
            master=self.text)
        reply = str(m.show())
        if reply == "yes":
            self.save(None)
            if not self.get_saved():
                reply = "cancel"
        self.text.focus_set()
        return reply

