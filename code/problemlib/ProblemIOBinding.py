
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

## This provides an interface to configuration of fonts
## and the tutorial folder and the problem batabase folder

## Setting up the IO bindings for teh ProblemEditor window
## Inherits from idlelib/IOBinding

from idlelib import IOBinding


class ProblemIOBinding(IOBinding.IOBinding):

    def __init__(self, parent):
        IOBinding.IOBinding.__init__(self, parent)
        self.editwin = parent

    def open(self, event=None, editFile=None):
        pass

    def save(self, event):
        if self.editwin.save_method:
            self.editwin.save_method()
        else:
            if not self.filename:
                self.save_as(event)
            else:
                if self.writefile(self.filename):
                    self.set_saved(1)
                    try:
                        self.editwin.store_file_breaks()
                    except AttributeError:  # may be a PyShell
                        pass
                    self.text.focus_set()
        return "break"
