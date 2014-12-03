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

# For setting up menus in the problem edit window (ProblemEditor)
# based on idlelib/Bindings.py

from idlelib.configHandler import idleConf
from idlelib import macosxSupport

menudefs = default_keydefs = None

def initialise():
    import sys
    global menudefs
    global default_keydefs

    if menudefs is not None:
        return

    menudefs = [
     # underscore prefixes character to underscore
     #('file', [
     #           ]),
     ('edit', [
       ('_Undo', '<<undo>>'),
       ('_Redo', '<<redo>>'),
       None,
       ('Cu_t', '<<cut>>'),
       ('_Copy', '<<copy>>'),
       ('_Paste', '<<paste>>'),
       ('Select _All', '<<select-all>>'),
       None,
       ('_Find...', '<<find>>'),
       ('Find A_gain', '<<find-again>>'),
       ('Find _Selection', '<<find-selection>>'),
       ('Find in Files...', '<<find-in-files>>'),
       ('R_eplace...', '<<replace>>'),
       ('Go to _Line', '<<goto-line>>'),
      ]),
    ('format', [
       ('_Indent Region', '<<indent-region>>'),
       ('_Dedent Region', '<<dedent-region>>'),
       ('Comment _Out Region', '<<comment-region>>'),
       ('U_ncomment Region', '<<uncomment-region>>'),
       ('Tabify Region', '<<tabify-region>>'),
       ('Untabify Region', '<<untabify-region>>'),
       ('Toggle Tabs', '<<toggle-tabs>>'),
       ('New Indent Width', '<<change-indentwidth>>'),
       ]),
    ]

    if macosxSupport.runningAsOSXApp():
        # Running as a proper MacOS application bundle. This block restructures
        # the menus a little to make them conform better to the HIG.

        quitItem = menudefs[0][1][-1]
        closeItem = menudefs[0][1][-2]


    default_keydefs = idleConf.GetCurrentKeySet()
