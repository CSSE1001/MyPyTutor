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

## a checker for the problem HTML 

import sys
from HTMLParser import HTMLParser

VALID_TAGS = ['br', 'p', 'ul', 'li', 'span', 'pre', 
              'h1', 'h2', 'h3', 'h4', 'h5',
              'it', 'b', 'tt', 'img']

class HTMLChecker(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_stack = []
        self.okay = True

    def reset(self):
        self.tag_stack = []
        self.okay = True
        HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        pos = self.getpos()
        if tag not in VALID_TAGS:
            print  >> sys.stderr, 'Invalid tag: '+tag+' at position '+str(pos)
            self.okay = False
            self.close()
        if tag == 'img':
            if attrs[0][0] != 'src' or '.gif' not in attrs[0][1]:
              print  >> sys.stderr, 'Invalid tag: '+tag+' at position '+str(pos)
              self.okay = False
              self.close()  
        if tag != 'br':
            self.tag_stack.append((pos, tag))

    def handle_endtag(self, tag):
        top_pos, top_tag = self.tag_stack.pop(-1)
        pos = self.getpos()
        if top_tag != tag and top_tag != 'p':
            print  >> sys.stderr, 'Tag '+tag+' at position '+\
                str(pos)+' does not match tag '+top_tag+\
                ' at position '+str(top_pos)
            self.okay = False
            self.close()

    def is_ok(self):
        return self.okay
