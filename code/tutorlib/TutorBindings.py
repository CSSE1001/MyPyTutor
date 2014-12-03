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

## This define menus in the code edit window
## It is a modification of idlelib/Bindings.py

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
     ('file', [
       ('Load From...', '<<load-from>>'),
       ('Revert', '<<revert>>'),
       None,
       ('_Save', '<<save-window>>'),
       #('Save _As...', '<<save-window-as-file>>'),
       ('Save Cop_y As...', '<<save-copy-of-window-as-file>>'),
       None,
       ('Prin_t Window', '<<print-window>>'),
       None,
       ('_Close', '<<close-window>>'),
       ('E_xit', '<<close-all-windows>>'),
      ]),
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
      ('options', [
                ('_Configure IDLE...', '<<open-config-dialog>>'),
       None,
       ]),
      ("check", [
                ("Check    F5", '<<check>>')
                ]),
      ("online", [
                ("Login", '<<login>>'),
                ("Logout", '<<logout>>'),
                ("Change Password", '<<change_password>>'),
                None,
                ("Upload Problem Answer", '<<upload_answer>>'),
                ("Download Problem Answer", '<<download_answer>>'),
                None,
                ("Submit Answer              F6", '<<submit_answer>>'),
                ("Show Submissions", '<<show_submit>>')
                ]),

      ('help', [
       ('_About IDLE', '<<about-idle>>'),
       None,
       ('_IDLE Help', '<<help>>'),
       ('Python _Docs', '<<python-docs>>'),
       None,
       ('About _Tutor', '<<about-tutor>>'),
       ('Tutor Help', '<<help-tutor>>'),
       ]),
    ]

    if macosxSupport.runningAsOSXApp():
        # Running as a proper MacOS application bundle. This block restructures
        # the menus a little to make them conform better to the HIG.

        quitItem = menudefs[0][1][-1]
        closeItem = menudefs[0][1][-2]

        # Remove the last 3 items of the file menu: a separator, close window and
        # quit. Close window will be reinserted just above the save item, where
        # it should be according to the HIG. Quit is in the application menu.
        del menudefs[0][1][-3:]
        menudefs[0][1].insert(6, closeItem)

        # Remove the 'About' entry from the help menu, it is in the application
        # menu
        del menudefs[-1][1][0:2]

        menudefs.insert(0,
                        ('application', [
                            ('About IDLE', '<<about-idle>>'),
                            None,
                            ('_Preferences....', '<<open-config-dialog>>'),
                        ]))

    default_keydefs = idleConf.GetCurrentKeySet()
