
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

## The MyPyTutor help dialog


from tutorlib.gui.textdialog import TextDialog

HELP_TEXT = """
The MyPyTutor Python Tutorial System
------------------------------------

The main window displays a problem in the top frame and the output from testing your code in the bottom frame. You use the IDLE-like edit window in which to write your answers.

The main window has the following menus.

* The 'Problems' menu allows you to pick a particular tutorial problem to work on.

* The 'Online' menu (if present) provides an interface to your online information.

* The 'Preferences' menu allows you to configure MyPyTutor.

* The 'MyPyTutor Feedback' allows you to provide us with feedback on any given tutorial problem and on the system overall.

Once the first problem of a session is chosen, an IDLE-like edit window
will appear. You are to write your answer to the given problem in this window.
The menus for this window are mostly the same as the IDLE edit window.
The main differences are given below.

* Because your (partial) solutions are saved and loaded from your answers folder the File menu is a little different. The 'Revert' option replaces your code by the default code from the problem. The 'Save' option saves your code to the answers folder. When you choose a problem, your saved code is automatically loaded and so there is no 'Open' option. However, a 'Load From' option is provided so that code can be loaded from another source.

* The 'Check' menu is similar to the 'Run' menu of IDLE but instead of running the code in the interpreter, it checks to see your answer is correct.

* If present, the 'Online' menu behaves in the same way as the Online menu in the main window.

Window Resizing
---------------

You can resize the main MyPyTutor window in the usual way. By dragging on the bar containing the status information you can change the relative sizes of two parts of the main window. The new size information will be saved for next time you run MyPyTutor.

The Preferences Menu
--------------------

The 'Configure Tutor Fonts' item allows you to choose fonts. The font name determines the font used for the problem frame. The edit window and output frame use the courier font.

The 'Configure Tutorials Folder' item allows you to choose the folder containing
all the tutorial problems. The menu items in the 'Tutorials' menu are determined by the chosen folder.

The 'Configure Answers Folder' item allows you to choose the folder in which your (partial) answers are saved to and loaded from.

MyPyTutor can work with multiple tutorials (for example, from different courses). You are able to set up new tutorials and also remove them. You can change between tutorials and set the default tutorial (the one used on startup). If you are logged in when you change the tutorial or remove a tutorial you will be logged out.

The Online Menu (if present)
----------------------------

If the tutorial is configured to provide an online interface and you are registered (i.e. have a username and password for MyPyTutor) then you can use this menu to interact with your online information. A discription of the options are give below.

* Login: this connects you with online system using your MyPyTutor username and password.

* Logout: this disconnects you from the online system.

* Change Password: this allows you to change your MyPyTutor password.

* Upload Problem Answer: this allows you to upload your answer to the current problem. This provides an online mechanism for saving your code that complements your local save via the Save option in the File menu of the editor.

* Download Problem Answer: this downloads the previously uploaded code for the current problem.

* Submit Answer: submit your answer (for marks). Your answer must be checked (and correct) before you can submit your answer.

* Show Submissions: display all the tutorial problems showing which ones you have submitted on time ('OK') and which ones you have submitted late ('LATE'). It also shows your current percentage (late submissions are not counted).

"""


class HelpDialog(TextDialog):
    def __init__(self, parent, title='Help'):
        TextDialog.__init__(self, parent, title, HELP_TEXT, bg="#ffffaa")
