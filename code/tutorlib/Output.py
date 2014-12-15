
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

from tkinter import *

from tutorlib.tester import TutorialTestResult


def get_code_font(fontsize):
    return ('courier', str(fontsize + 1), 'normal', 'roman')


class TestsListbox(Listbox):
    COLOR_NOT_RUN = 'black'
    COLOR_PASS = 'green'
    COLOR_FAIL = 'red'
    COLOR_ERROR = 'red'
    COLOR_INDETERMINATE = 'orange'

    def __init__(self, master, *args, fontsize=None, **kwargs):
        fontsize = 12 if fontsize is None else fontsize
        font = kwargs.pop('font', get_code_font(fontsize))
        super().__init__(master, *args, font=font, **kwargs)

        self.color_mappings = {
            TutorialTestResult.NOT_RUN: TestsListbox.COLOR_NOT_RUN,
            TutorialTestResult.PASS: TestsListbox.COLOR_PASS,
            TutorialTestResult.FAIL: TestsListbox.COLOR_FAIL,
            TutorialTestResult.ERROR: TestsListbox.COLOR_ERROR,
            TutorialTestResult.INDETERMINATE: TestsListbox.COLOR_INDETERMINATE,
        }

        self.results = None

    def update_font(self, fontsize):
        self.config(font=get_code_font(fontsize))

    def set_test_results(self, results):
        # remove existing entries
        self.delete(0, END)

        # add each new entry, configuring colors as we go
        for idx, result in enumerate(results):
            self.insert(END, result.description)

            color = self.color_mappings[result.status]
            self.itemconfig(idx, fg=color, selectbackground=color)

        # shrink ourself
        self.config(height=len(results))

        # store the results for later use
        self.results = results

    def get_selected_result(self):
        idx = self.curselection()[0]
        return self.results[idx]  # assume valid


class TestOutput(Frame):
    def __init__(self, master, fontsize, textlen):
        Frame.__init__(self, master)

        self.test_results = TestsListbox(self, fontsize=fontsize)
        self.test_results.pack(side=TOP, expand=1, fill=BOTH)
        self.test_results.bind('<<ListboxSelect>>', self.selected_test_result)

        self.output = Output(self, fontsize, textlen)
        self.output.pack(side=TOP, expand=1, fill=BOTH)

    def update_font(self, fontsize):
        self.test_results.update_font(fontsize)
        self.output.update_font(fontsize)

    def update_text_length(self, lines):
        pass  # TODO: I don't think this belongs (anywhere)?

    def selected_test_result(self, evt):
        result = self.test_results.get_selected_result()
        self.display_result(result)

    def set_test_results(self, results):
        self.test_results.set_test_results(results)
        self.output.clear_text()

    def display_result(self, result):
        self.output.clear_text()

        # show result
        self.output.add_text(result.message, Output.COLOR_BASE)

        # show output: prints first, then errors
        self.output.add_text(result.output_text, Output.COLOR_OUTPUT)
        self.output.add_text(result.error_text, Output.COLOR_ERROR)


class Output(Frame):
    COLOR_BASE = 'black'
    COLOR_OUTPUT = 'blue'
    COLOR_ERROR = 'red'
    COLOR_WARNING = 'orange'

    def __init__(self, master, fontsize, textlen):
        Frame.__init__(self, master)

        self.text = Text(self, height=textlen)
        self.text.config(state=DISABLED)
        self.text.pack(side=LEFT, fill=BOTH, expand=1)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

        self.text.tag_config("red", foreground="red")
        self.text.tag_config("blue", foreground="blue")
        self.text.config(font=get_code_font(fontsize))

    def update_font(self, fontsize):
        self.text.config(font=get_code_font(fontsize))

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
        self.text.config(height=lines)


class AnalysisOutput(Output):
    def __init__(self, master, fontsize, textlen):
        super().__init__(master, fontsize, textlen)

    def set_analyser(self, analyser):
        self.clear_text()

        # show the first error, and each warning
        for warning in analyser.warnings:
            self.add_text(warning, Output.COLOR_WARNING)

        if analyser.errors:
            self.add_text(analyser.errors[0], Output.COLOR_ERROR)