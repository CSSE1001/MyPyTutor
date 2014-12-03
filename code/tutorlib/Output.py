
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


# The output frame where stdout and stderr are displayed

from Tkinter import *


class Output(Frame):
    def __init__(self, master,fontsize, textlen):
        Frame.__init__(self, master)
        self.text = Text(self, height = textlen)
        self.text.config(state=DISABLED)
        self.text.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)
        self.text.tag_config("red", foreground="red")
        self.text.tag_config("blue", foreground="blue")
        self.text.config(font = ('courier', str(fontsize+1), 
                                 'normal', 'roman'))

    def update_font(self, fontsize):
        self.text.config(font = ('courier', str(fontsize+1), 
                                 'normal', 'roman'))

    def clear_text(self):
        self.text.config(state=NORMAL)
        self.text.delete(1.0, END)
        self.text.config(state=DISABLED)

    def add_text(self, text, style=None): 
        self.text.config(state=NORMAL)
        if style:
            self.text.insert(END, text, (style,))
        else:
            self.text.insert(END, text)
        self.text.config(state=DISABLED)

    def set_font(self, font):
        self.text.config(font=font)

    def update_text_length(self, lines):
        self.text.config(height = lines)
