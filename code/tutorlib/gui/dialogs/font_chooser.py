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

import tkinter as tk
from tkinter import ttk
import tkinter.font
import tkinter.simpledialog
from idlelib.dynOptionMenuWidget import DynOptionMenu


class FontChooser(tk.Toplevel):

    def __init__(self, master, parent, defaultfont):
        super().__init__(master)
        self.master = master
        self.parent = parent
        self.result = None
        self.title('Font Chooser')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        self.fontSize = tk.StringVar(self)
        self.fontBold = tk.BooleanVar(self)
        self.fontName = tk.StringVar(self)
        self.spaceNum = tk.IntVar(self)
        font_name = defaultfont[0]
        font_size = defaultfont[1]
        self.fontName.set(font_name)
        self.fontSize.set(font_size)
        self.editFont = tkinter.font.Font(self, (font_name,
                                                 int(font_size),
                                                 'normal'))
        frame = ttk.Frame(self)
        frame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)

        frameFont = ttk.LabelFrame(
            frame, borderwidth=2, relief=tk.GROOVE, text=' Tutorial Font '
        )
        frameFontName = ttk.Frame(frameFont)
        frameFontParam = ttk.Frame(frameFont)
        self.labelFontNameTitle = ttk.Label(
            frameFontName, justify=tk.LEFT, text='Font Face : '+font_name
        )
        self.fontName.set(font_name)
        self.listFontName = tk.Listbox(
            frameFontName,
            height=5,
            takefocus=tk.FALSE,
            exportselection=tk.FALSE,
        )
        self.listFontName.bind('<ButtonRelease-1>',
                               self.OnListFontButtonRelease)
        scrollFont = ttk.Scrollbar(frameFontName)
        scrollFont.config(command=self.listFontName.yview)
        self.listFontName.config(yscrollcommand=scrollFont.set)
        labelFontSizeTitle = ttk.Label(frameFontParam, text='Size :')
        fonts = sorted(list(tkinter.font.families())+['Helvetica'])
        for font in fonts:
            self.listFontName.insert(tk.END, font)
        self.optMenuFontSize = DynOptionMenu(frameFontParam, self.fontSize,
                                             None, command=self.SetFontSample)
        frameFontSample = ttk.Frame(frameFont, relief=tk.SOLID, borderwidth=1)
        self.optMenuFontSize.SetMenu(('7', '8', '9', '10', '11', '12', '13',
                                      '14', '16', '18', '20', '22'), font_size)

        self.labelFontSample = ttk.Label(
            frameFontSample,
            text='AaBbCcDdEe\nFfGgHhIiJjK\n1234567890\n#:+=(){}[]',
            justify=tk.LEFT,
            font=self.editFont,
        )

        frameFont.pack(
            side=tk.LEFT,
            padx=5,
            pady=5,
            expand=tk.TRUE,
            fill=tk.BOTH,
        )
        frameFontName.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        frameFontParam.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        self.labelFontNameTitle.pack(side=tk.TOP, anchor=tk.W)
        self.listFontName.pack(side=tk.LEFT, expand=tk.TRUE, fill=tk.X)
        scrollFont.pack(side=tk.LEFT, fill=tk.Y)
        labelFontSizeTitle.pack(side=tk.LEFT, anchor=tk.W)
        self.optMenuFontSize.pack(side=tk.LEFT, anchor=tk.W)
        frameFontSample.pack(side=tk.TOP, padx=5, pady=5, expand=tk.TRUE, fill=tk.BOTH)
        self.labelFontSample.pack(expand=tk.TRUE, fill=tk.BOTH)
        buttonFrame = ttk.Frame(self)
        buttonFrame.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        okButton = ttk.Button(buttonFrame, text="OK", command=self.ok)
        applyButton = ttk.Button(buttonFrame, text="Apply", command=self.apply)
        cancelButton = ttk.Button(buttonFrame, text="Cancel", command=self.cancel)
        okButton.pack(side=tk.LEFT, expand=tk.TRUE)
        applyButton.pack(side=tk.LEFT, expand=tk.TRUE)
        cancelButton.pack(side=tk.LEFT, expand=tk.TRUE)
        self.wait_window(self)

    def destroy(self):
        super().destroy()

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
        font = self.listFontName.get(tk.ANCHOR)
        self.fontName.set(font.lower())
        self.SetFontSample()

    def SetFontSample(self, event=None):
        fontName = self.fontName.get()
        fontWeight = tkinter.font.NORMAL
        self.labelFontNameTitle.config(text='Font Face : '+fontName)
        self.editFont.config(size=self.fontSize.get(),
                             weight=fontWeight, family=fontName)
