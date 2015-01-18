
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

## The frame in which the problem description is rendered as HTML
## The possible HTML tags are
## h1, h2, h3, h4, h5, it, tt, b, br, p, pre, ul, li, img
## and span as long as <span style='color:c'> where c is red, blue or green

from abc import ABCMeta, abstractmethod
from html.parser import HTMLParser
import os
import tkinter as tk
from tkinter import ttk


HEADERS = ['h1', 'h2', 'h3', 'h4', 'h5']
INDENT = 'indent{}'
COLORS = ['red', 'green', 'blue']


def get_configs(name, size, style='roman', max_indents=6):
    tags = {
        'it': {
            'font': (name, size, 'italic'),
        },
        'b': {
            'font': (name, size, 'bold'),
        },
        'tt': {
            'font': ('courier', size, style),
            'foreground': 'grey',
        },
    }

    header_sizes = reversed(range(0, 2*len(HEADERS), 2))  # step in 2s from 0
    for tag, sz in zip(HEADERS, header_sizes):
        tags[tag] = {
            'font': (name, size + sz, 'bold')
        }

    for n in range(max_indents):
        tags[INDENT.format(n)] = {
            'lmargin1': 40*n,
            'lmargin2': 40*n + 14,
        }

    for color in COLORS:
        tags[color] = {
            'foreground': color,
        }

    return tags


INTRO_TEXT = """
<p>
<p>
<h3>Welcome to MyPyTutor {version}</h3>

The Problems menu contains the
collection of problems to choose from.
"""

ONLINE_TEXT = """
<p>
Use the Online menu to interact with your online information.
</p>
"""


class TutorialHTMLParserDelegate(metaclass=ABCMeta):
    @abstractmethod
    def append_text(self, text, *args):
        pass

    @abstractmethod
    def append_image(self, image_name):
        pass


class TutorialFrame(ttk.Frame, TutorialHTMLParserDelegate):
    def __init__(self, master, fontinfo, textlen):
        super().__init__(master)

        font_name = fontinfo[0]
        font_size = int(fontinfo[1])

        self.text = tk.Text(self, height=textlen, wrap=tk.WORD)
        self.text.config(
            state=tk.DISABLED,
            font=(font_name, str(font_size), 'normal', 'roman')
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text.yview)

        self.update_fonts(font_name, font_size)

        self.parser = TutorialHTMLParser(delegate=self)
        self._tutorial = None
        self._next_hint_index = 0

    # Properties
    @property
    def tutorial(self):
        return self._tutorial

    @tutorial.setter
    def tutorial(self, tutorial):
        # set the property
        # do this FIRST, in case the later calls rely on it being present
        self._tutorial = tutorial

        # display the tutorial text
        self._set_text(tutorial.description)
        self._next_hint_index = 0

    # Public methods
    def splash(self, version):
        text = INTRO_TEXT.format(version=version)

        # this version of MPT is always online
        text += ONLINE_TEXT

        self._set_text(text)

    def update_fonts(self, font_name, font_size):
        for tag, attrs in get_configs(font_name, font_size).items():
            self.text.tag_config(tag, **attrs)

        # reset default font (I think?)
        self.text.config(
            font=(font_name, str(font_size), 'normal', 'roman')
        )

    def show_next_hint(self):
        # actually get the hint
        try:
            hint = self.tutorial.hints[self._next_hint_index]
            self._next_hint_index += 1
        except IndexError:
            return False

        html = '<p>\n<b>Hint: </b>{}'.format(hint)

        self.text.config(state=tk.NORMAL)

        self.parser.reset()
        self.parser.feed(html)

        self.text.yview(tk.MOVETO, 1)

        self.text.config(state=tk.DISABLED)

        return True

    # Private methods
    def _set_text(self, text):
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)

        self.text.insert(tk.END, '\n')

        self.parser.reset()
        self.parser.feed(text)

        self.text.config(state=tk.DISABLED)

    # TutorialHTMLParserDelegate
    def append_text(self, text, *args):
        self.text.insert(tk.END, text, *args)

    def append_image(self, image_name):
        # img_obj must be stored on self, or tk will garbage collect it
        path = os.path.join(self.tutorial.tutorial_path, image_name)
        self._img_obj = tk.PhotoImage(file=path)

        img_label = ttk.Label(self.text, image=self._img_obj)
        self.text.window_create(tk.END, window=img_label)


class TutorialHTMLParser(HTMLParser):
    def __init__(self, delegate):
        super().__init__(self)

        self.delegate = delegate

        self.header = ''
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False

    def reset(self):
        self.indent = 0
        self.active_tags = []
        self.do_lstrip = False
        self.end_ul = False
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        self.do_lstrip = False
        if tag == 'span':
            if len(attrs) == 1 and len(attrs[0]) == 2 \
                    and attrs[0][0] == 'style':
                style = attrs[0][1].split(':')
                if len(style) == 2 and style[0].strip() == 'color':
                    self.active_tags.append(style[1].strip())
                else:
                    self.active_tags.append(tag)
            else:
                self.active_tags.append(tag)
        elif tag == 'br':
            self.do_lstrip = True
            self.delegate.append_text('\n')
        elif tag == 'p':
            self.do_lstrip = True
            self.delegate.append_text('\n\n')
        elif tag == 'img':
            img_file = attrs[0][1]
            self.delegate.append_image(img_file)
            self.active_tags.append(tag)
        else:
            if tag == 'ul':
                self.delegate.append_text('\n')
                self.indent += 1
                self.active_tags.append(tag)
            elif tag == 'li':
                self.active_tags.append(INDENT.format(self.indent))
                self.do_lstrip = True
                if not self.end_ul:
                    self.delegate.append_text('\n')
                self.delegate.append_text('* ', tuple(self.active_tags))
            else:
                self.active_tags.append(tag)
        self.end_ul = False

    def handle_endtag(self, tag):
        if tag == 'ul':
            self.delegate.append_text('\n\n')
            self.indent -= 1
            self.do_lstrip = True
            self.end_ul = True
        elif tag == 'li':
            self.do_lstrip = True
        elif tag == 'p':
            self.do_lstrip = True
            return
        elif tag in HEADERS:
            self.delegate.append_text('\n\n')
            self.do_lstrip = True
        self.active_tags.pop(-1)

    def _compress_data(self, data):
        # TODO: I'm not remotely happy with this method.
        # TODO: It doesn't really do what it says on the tin, and when, eg, it
        # TODO: is told not to strip indents, it does so anyway (replacing them
        # TODO: with a single space).
        data = data.replace('\n', ' ')
        if len(data) > 1:
            first = data[0]
            last = data[-1]
        elif data == ' ':
            first = ' '
            last = ' '
        else:
            first = ''
            last = ''
        data = ' '.join(data.split())
        if self.do_lstrip:
            self.do_lstrip = False
            if data and last == ' ':
                data = data + last
        else:
            if first == ' ':
                data = first+data
            if data != ' ' and last == ' ':
                data = data + last
        return data

    def handle_data(self, data):
        if self.active_tags:
            tag = self.active_tags[-1]
            if tag == 'ul':
                return
            if tag == 'pre':
                self.delegate.append_text(data, ('tt',))
                return
            data = self._compress_data(data)
            # TODO: I'm not sure why it was necessary to give priority to
            # TODO: all non-indent tags; this seems to also reverse the order
            # TODO: of the active tags, which is a bit odd
            #for tag in self.active_tags:
            #    if 'indent' not in tag:
            #        self.textobj.tag_raise(tag)
            self.delegate.append_text(data, tuple(self.active_tags))
        else:
            data = self._compress_data(data)
            self.delegate.append_text(data)
