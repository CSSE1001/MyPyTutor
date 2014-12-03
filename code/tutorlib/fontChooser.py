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

## A Font chooser - this is based on CreatePageFontTab in
## idlelib/configDialog.py

from tkinter import *
import tkinter.font
import tkinter.simpledialog
from idlelib.dynOptionMenuWidget import DynOptionMenu


class FontChooser(Toplevel):

    def __init__(self, master, parent, defaultfont):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.result = None
        self.title('Font Chooser')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        self.fontSize = StringVar(self)
        self.fontBold = BooleanVar(self)
        self.fontName = StringVar(self)
        self.spaceNum = IntVar(self)
        font_name = defaultfont[0]
        font_size = defaultfont[1]
        self.fontName.set(font_name)
        self.fontSize.set(font_size)
        self.editFont = tkinter.font.Font(self, (font_name,
                                                 int(font_size),
                                                 'normal'))
        frame = Frame(self)
        frame.pack(side=TOP, expand=TRUE, fill=BOTH)

        frameFont = LabelFrame(frame, borderwidth=2, relief=GROOVE,
                               text=' Tutorial Font ')
        frameFontName = Frame(frameFont)
        frameFontParam = Frame(frameFont)
        self.labelFontNameTitle = Label(frameFontName, justify=LEFT,
                                        text='Font Face : '+font_name)
        self.fontName.set(font_name)
        self.listFontName = Listbox(frameFontName, height=5, takefocus=FALSE,
                                    exportselection=FALSE)
        self.listFontName.bind('<ButtonRelease-1>',
                               self.OnListFontButtonRelease)
        scrollFont = Scrollbar(frameFontName)
        scrollFont.config(command=self.listFontName.yview)
        self.listFontName.config(yscrollcommand=scrollFont.set)
        labelFontSizeTitle = Label(frameFontParam, text='Size :')
        fonts = sorted(list(tkinter.font.families())+['Helvetica'])
        for font in fonts:
            self.listFontName.insert(END, font)
        self.optMenuFontSize = DynOptionMenu(frameFontParam, self.fontSize,
                                             None, command=self.SetFontSample)
        frameFontSample = Frame(frameFont, relief=SOLID, borderwidth=1)
        self.optMenuFontSize.SetMenu(('7', '8', '9', '10', '11', '12', '13',
                                      '14', '16', '18', '20', '22'), font_size)

        self.labelFontSample = Label(frameFontSample,
                                     atext='AaBbCcDdEe\nFfGgHhIiJjK\n1234567890\n#:+=(){}[]',
                                     justify=LEFT, font=self.editFont)

        frameFont.pack(side=LEFT, padx=5, pady=5, expand=TRUE, fill=BOTH)
        frameFontName.pack(side=TOP, padx=5, pady=5, fill=X)
        frameFontParam.pack(side=TOP, padx=5, pady=5, fill=X)
        self.labelFontNameTitle.pack(side=TOP, anchor=W)
        self.listFontName.pack(side=LEFT, expand=TRUE, fill=X)
        scrollFont.pack(side=LEFT, fill=Y)
        labelFontSizeTitle.pack(side=LEFT, anchor=W)
        self.optMenuFontSize.pack(side=LEFT, anchor=W)
        frameFontSample.pack(side=TOP, padx=5, pady=5, expand=TRUE, fill=BOTH)
        self.labelFontSample.pack(expand=TRUE, fill=BOTH)
        buttonFrame = Frame(self)
        buttonFrame.pack(side=TOP, expand=TRUE, fill=BOTH)
        okButton = Button(buttonFrame, text="OK", command=self.ok)
        applyButton = Button(buttonFrame, text="Apply", command=self.apply)
        cancelButton = Button(buttonFrame, text="Cancel", command=self.cancel)
        okButton.pack(side=LEFT, expand=TRUE)
        applyButton.pack(side=LEFT, expand=TRUE)
        cancelButton.pack(side=LEFT, expand=TRUE)
        self.wait_window(self)

    def destroy(self):
        Toplevel.destroy(self)

    def ok(self, e=None):
        self.result = (self.fontName.get(), self.fontSize.get())
        self.withdraw()
        self.update_idletasks()
        self.cancel()

    def apply(self, e=None):
        self.parent.font_apply(self.fontName.get(), self.fontSize.get())

    def cancel(self, e=None):
        self.master.focus_set()
        self.destroy()

    def OnListFontButtonRelease(self, event):
        font = self.listFontName.get(ANCHOR)
        self.fontName.set(font.lower())
        self.SetFontSample()

    def SetFontSample(self, event=None):
        fontName = self.fontName.get()
        fontWeight = tkinter.font.NORMAL
        self.labelFontNameTitle.config(text='Font Face : '+fontName)
        self.editFont.config(size=self.fontSize.get(),
                             weight=fontWeight, family=fontName)
