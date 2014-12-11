
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

## The MyPyTutor application


import time
import sys
import os
from io import StringIO
from . import fontChooser
import tkinter.messagebox
import zipfile

from tkinter import *
import tkinter.filedialog
from configparser import *

import tutorlib.Output as tut_output
import tutorlib.Tutorial as tut_tutorial
import tutorlib.TutorEditor as tut_editor
import tutorlib.TutorialInterface as tut_interface
import tutorlib.aboutdialog as tut_dialog
import tutorlib.helpdialog as tut_help
import tutorlib.feedbackdialog as tut_feedback
import tutorlib.passworddialogs as tut_password_dialogs
import tutorlib.textdialog as tut_textdialog
import tutorlib.TutorConfigure as tut_configure

# Version number of MyPyTutor
version_number = "2.03"

# The config file is stored in the home directory
HOME_DIR = os.path.expanduser('~')
CONFIG_FILE = os.path.join(HOME_DIR, 'mypytutor.cfg')

DEFAULT_CONFIG = StringIO("""
[FONT]
name=helvetica
size=10
[WINDOW_SIZES]
problem=20
output=5
[TUTORIALS]
names=
default=
""")


# This application is intended to be run on the students machine.
# Consequently, attempts have been made to hide how the program works.
# First, the code is supplied in compiled form.
# Secondly, comments have been written in such a way that help will not
# show the comments.

# unzip the zipfile (zf) to the given folder (path)

def unzipit(zf, path):
    z = zipfile.ZipFile(zf)
    info = z.namelist()
    if not os.path.exists(path):
        os.mkdir(path)
    for item in info:
        if item.endswith('/') or item.endswith('\\'):
            fulldir = os.path.join(path, item)
            if not os.path.exists(fulldir):
                os.mkdir(fulldir)
        else:
            flags = (z.getinfo(item).external_attr >> 16) & 0o777
            text = z.read(item)
            fullpath = os.path.join(path, item)
            fd = open(fullpath, 'wb')
            fd.write(text)
            fd.close()
            os.chmod(fullpath, flags)
    z.close()


# Toolbar is used to show the Hint button if there are any hints
# for the problem and show to show the login status if MyPyTutor is
# configured for online use.

class Toolbar(Frame):
    def __init__(self, parent, master=None):
        Frame.__init__(self, master, bg='grey80')
        self.parent = parent
        self.hintbutton = Button(self, text="Next Hint",
                                 command=self.parent.showhint)

        self.bind("<Button-1>", self.button_pressed)
        self.bind("<B1-Motion>", self.button_motion)
        self.bind("<ButtonRelease-1>", self.button_released)
        self.status_var = StringVar()

    def button_pressed(self, event):
        self.parent.allow_resize = False
        self.y = event.y
        self.start_len = self.parent.output_len
        self.start_height = self.parent.output.winfo_height()

    def button_motion(self, event):
        diff = (self.y - event.y)*self.start_len/self.start_height
        if (self.parent.output_len + diff > 5 and
                self.parent.problem_len - diff > 5):
            self.parent.update_text_lengths(diff)

    def button_released(self, event):
        self.parent.allow_resize = True

    def set_hints(self, flag):
        if flag:
            self.hintbutton.pack(side=LEFT, expand=1)
        else:
            self.hintbutton.pack_forget()

    def enable_status(self):
        self.status_var.set("Status: Not Logged In")
        self.status = Label(self, textvariable=self.status_var, relief=SUNKEN)
        self.status.pack(side=RIGHT, pady=3, ipady=2, padx=2, ipadx=2)

    def set_login(self, user):
        self.status_var.set("Status: Logged in as %s" % user)

    def unset_login(self):
        self.status_var.set("Status: Not Logged In")


# The main application

class TutorialApp():
    def __init__(self, master=None):
        #print "Starting..."
        self.mpt_home = os.getcwd()
        self.app_height = 0
        self.allow_resize = False
        master.title("MyPyTutor")
        master.protocol("WM_DELETE_WINDOW", self.close_event)
        self.master = master
        self.URL = None
        os.chdir(HOME_DIR)
        self.config = ConfigParser()
        if os.path.exists(CONFIG_FILE):
            try:
                fp = open(CONFIG_FILE)
                self.config.readfp(fp)
                fp.close()
                config_found = True
            except:
                self.config = ConfigParser()
                self.config.readfp(DEFAULT_CONFIG)
                config_found = False
                tkinter.messagebox.showerror('Configuration Error',
                                             'Your configuration file is corrupted. You will now be asked to choose tutorial and answer folders again.')
        else:
            self.config.readfp(DEFAULT_CONFIG)
            config_found = False
        self.tutorial_names = self.config.get('TUTORIALS', 'names').split(',')
        self.problem_len = int(self.config.get('WINDOW_SIZES', 'problem'))
        self.output_len = int(self.config.get('WINDOW_SIZES', 'output'))
        #print "done configuration"

        #### Create GUI Widgets
        ## Top Frame
        top_frame = Frame(master)
        top_frame.pack(fill=BOTH, expand=1)
        self.editor = None

        ## Tutorial (html display of tutorial problem)
        self.tut = tut_tutorial.Tutorial(top_frame,
                                         (self.config.get('FONT', 'name'),
                                          self.config.get('FONT', 'size')),
                                         self.problem_len)
        self.tut.pack(fill=BOTH, expand=1)

        ## Short Problem Description
        self.short_description = Label(top_frame, fg='blue')
        self.short_description.pack(fill=X)

        ## Toolbar (hints, login status etc)
        self.toolbar = Toolbar(self, top_frame)
        self.toolbar.pack(fill=X)

        ## Test Output
        self.test_output = tut_output.TestOutput(top_frame,
                int(self.config.get('FONT', 'size')), self.output_len)
        self.test_output.pack(fill=BOTH, expand=0)

        ## Analysis Output
        self.analysis_output = tut_output.AnalysisOutput(top_frame,
                int(self.config.get('FONT', 'size')), self.output_len)
        self.analysis_output.pack(fill=BOTH, expand=0)

        self.tut_interface = \
            tut_interface.TutorialInterface(master, self)

        #print "done packing"
        menubar = Menu(master)
        sectionmenu = Menu(menubar, tearoff=0)
        sectionmenu.add_command(label="Next Tutorial", accelerator="N",
                                command=self.next_tutorial)
        sectionmenu.add_command(label="Previous Tutorial",
                                accelerator="P",
                                command=self.previous_tutorial)
        menubar.add_cascade(label="Problems", menu=sectionmenu)
        self.sectionmenu = sectionmenu
        self.sections = 0
        # When MyPyTutor is started for the first time the configuration
        # has not been set up and so tut_dir and ans_dir are empty
        # This causes an initial configuration that sets both directories.
        if not config_found:
            config = tut_configure.TutorConfigure(self.master, self)
            if config.result is None:
                return
            self.tut_dir, self.ans_dir, default = config.result
            self.config.add_section(default)
            self.config.set('TUTORIALS', 'names', default)
            self.config.set('TUTORIALS', 'default', default)
            self.config.set(default, 'tut_dir', self.tut_dir)
            self.config.set(default, 'ans_dir', self.ans_dir)
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
            self.tutorial_names = [default]
        else:
            default = self.config.get('TUTORIALS', 'default')
            self.tut_dir = self.config.get(default, 'tut_dir')
            self.ans_dir = self.config.get(default, 'ans_dir')
        self.default = default
        if self.tut_dir == '' or self.ans_dir == '':
            return
        self.current_tutorial = default
        self.setup_tutorial()
        #print "done tutorial menu"
        # If a URL is given then MyPyTutor has an online component and
        # the following sets up a menu for online interaction
        if self.URL:
            wwwmenu = Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Online", menu=wwwmenu)
            wwwmenu.add_command(label="Login",
                                command=self.login)
            wwwmenu.add_command(label="Logout",
                                command=self.logout)
            wwwmenu.add_command(label="Change Password",
                                command=self.change_password)
            wwwmenu.add_separator()
            wwwmenu.add_command(label="Upload Problem Code",
                                command=self.upload_answer)
            wwwmenu.add_command(label="Download Problem Code",
                                command=self.download_answer)
            wwwmenu.add_separator()
            wwwmenu.add_command(label="Submit Answer              F6",
                                command=self.submit_answer)
            wwwmenu.add_command(label="Show Submissions",
                                command=self.show_submit)
            master.bind("<F6>", self.submit_answer)
            self.toolbar.enable_status()

        self.tut.splash(self.URL, version_number)

        optionsmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Preferences", menu=optionsmenu)
        optionsmenu.add_command(label="Configure Tutor Fonts",
                                command=self.configure_tut)
        optionsmenu.add_command(label="Configure Tutorial Folder",
                                command=self.configure_tut_dir)
        optionsmenu.add_command(label="Configure Answers Folder",
                                command=self.configure_answers_dir)
        optionsmenu.add_separator()
        optionsmenu.add_command(label="Set As Default Tutorial",
                                command=self.set_default_tutorial)
        optionsmenu.add_command(label="Add New Tutorial",
                                command=self.add_new_tutorial)
        optionsmenu.add_command(label="Remove Current Tutorial",
                                command=self.remove_current_tutorial)
        self.tut_choice = StringVar()
        self.tut_choice.set(self.current_tutorial)
        self.radio_menu = Menu(optionsmenu, tearoff=0)
        optionsmenu.add_cascade(label="Change Tutorial", menu=self.radio_menu)
        for name in self.tutorial_names:
            self.radio_menu.add_radiobutton(label=name,
                                            variable=self.tut_choice,
                                            command=self.choose_tutorial)

        feedbackmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="MyPyTutor Feedback", menu=feedbackmenu)
        feedbackmenu.add_command(label="Problem Feedback",
                                 command=self.give_problem_feedback)
        feedbackmenu.add_command(label="General Feedback",
                                 command=self.give_general_feedback)

        helpmenu = Menu(menubar, name='help', tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About MyPyTutor",
                             command=self.about)
        helpmenu.add_command(label="Help",
                             command=self.help)
        master.config(menu=menubar)
        #print "done all menus"
        master.bind("n", self.next_tutorial)
        master.bind("N", self.next_tutorial)
        master.bind("p", self.previous_tutorial)
        master.bind("P", self.previous_tutorial)
        self.current_problem_index = -1
        self.current_problem = None
        #master.update_idletasks()
        master.bind("<Configure>", self.resize)
        self.allow_resize = True
        self.current_tut_name = None
        self.current_prob_name = None
        #print "done init"

    def set_default_tutorial(self):
        if self.default != self.current_tutorial:
            self.default = self.current_tutorial
            self.config.set('TUTORIALS', 'default', self.default)
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()

    def remove_current_tutorial(self):
        if self.default == self.current_tutorial:
            tkinter.messagebox.showerror('Remove Current Tutorial Error',
                                         'You cannot remove the default tutorial.')
            return
        if len(self.tutorial_names) == 1:
            tkinter.messagebox.showerror('Remove Current Tutorial Error',
                                         'You cannot remove the last tutorial.')
            return
        remove_answer = tkinter.messagebox.askquestion("Remove Tutorial",
                                                       "Do you really want to remove %s?" % self.current_tutorial)
        if str(remove_answer) == 'yes':
            self.config.remove_section(self.current_tutorial)
            self.tutorial_names.remove(self.current_tutorial)
            self.config.set('TUTORIALS', 'names', ','.join(self.tutorial_names))
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
            self.logout()
            self.current_tutorial = self.default
            self.tut_dir = self.config.get(self.current_tutorial, 'tut_dir')
            self.ans_dir = self.config.get(self.current_tutorial, 'ans_dir')
            self.setup_tutorial()
            self.radio_menu.delete(0, END)
            for name in self.tutorial_names:
                self.radio_menu.add_radiobutton(label=name,
                                                variable=self.tut_choice,
                                                command=self.choose_tutorial)

    def setup_tutorial(self):
        self.master.title("MyPyTutor: " + self.current_tutorial)
        self.tut.set_directory(self.tut_dir)
        if not self.process_tutorial_file():
            tkinter.messagebox.showerror('Configuration Error',
                                         'Your Tutorial folder is incorrect. Please use the Preferences menu to choose the correct folder.')
        self.tut_interface.set_url(self.URL)
        self.make_section_menu_entries()
        if os.path.exists(self.ans_dir):
            os.chdir(self.ans_dir)
        else:
            tkinter.messagebox.showerror('Configuration Error',
                                         'Your Answer folder does not exist. Please use the Preferences menu to choose the folder.')

    def resize(self, e):
        if self.allow_resize:
            self.problem_len = self.gettextlen(self.tut)
            self.output_len = self.gettextlen(self.test_output.output)

    def gettextlen(self, text_obj):
        #print text_obj.winfo_height(), text_obj.text.dlineinfo("@0,0")
        return text_obj.winfo_height()//text_obj.text.dlineinfo("@0,0")[3]

    def update_text_lengths(self, delta):
        #print "update_lengths"
        self.problem_len -= delta
        self.output_len += delta
        self.tut.update_text_length(self.problem_len)
        self.test_output.update_text_length(self.output_len)

    def login(self):
        if self.tut_interface.logged_on():
            tkinter.messagebox.showerror('Login Error', 'You are already logged in.')
            return
        tut_password_dialogs.LoginDialog(self, self.do_login)
        if self.tut_interface.logged_on():
            self.toolbar.set_login(self.tut_interface.user)
            #print self.timestamp, self.tut_interface.timestamp
            if self.timestamp < self.tut_interface.timestamp:
                zf = self.tut_interface.get_tut_zipfile()
                #print zf
                if zf is None:
                    tkinter.messagebox.showerror('MyPyTutor', 'Error occurred when updating tutorials - try again later.')
                    return
                try:
                    unzipit(zf, self.tut_dir)
                    os.remove(zf)
                    tkinter.messagebox.showinfo('MyPyTutor', 'Tutorial Problems Updated')
                    self.tutorials = self.get_tutorial_info()
                    self.make_section_menu_entries()
                except:
                    #print 'exception'
                    tkinter.messagebox.showerror('MyPyTutor', 'Error occurred when updating tutorials - try again later.')
        version = self.tut_interface.get_version()
        if version is not None:
            verlst = version.split('.')
            currverlst = version_number.split('.')
            #print currverlst
            if verlst > currverlst:
                if sys.version_info > (2, 6):
                    zf = self.tut_interface.get_mpt27()
                else:
                    tkinter.messagebox.showerror('MyPyTutor',
                                                 'You are not using Python 2.7 - you need to upgrade')
                    return
                #print zf
                if zf is None:
                    tkinter.messagebox.showerror('MyPyTutor',
                                                 'Error occurred when updating MyPyTutor - try again later.')
                    return
                try:
                    unzipit(zf, self.mpt_home)
                    z = zipfile.ZipFile(zf)
                    os.remove(zf)
                    tkinter.messagebox.showinfo('MyPyTutor',
                                                'MyPyTutor Updated - Please Restart')
                except Exception as e:
                    #print str(e)
                    tkinter.messagebox.showerror('MyPyTutor', 'Error occurred when updating MyPyTutor - try again later.')
        self.set_menu_colours()

    def reset_menus(self):
        self.sectionmenu.delete(0, END)
        self.sectionmenu.add_command(label="Next Tutorial",
                                     accelerator="N",
                                     command=self.next_tutorial)
        self.sectionmenu.add_command(label="Previous Tutorial",
                                     accelerator="P",
                                     command=self.previous_tutorial)

    def do_login(self, user, passwd):
        return self.tut_interface.login(user, passwd)

    def logout(self):
        self.toolbar.unset_login()
        self.tut_interface.logout()

    def change_password(self):
        if self.tut_interface.logged_on():
            cpdlg = tut_password_dialogs.ChangePasswordDialog(self)
            self.master.wait_window(cpdlg)
            if cpdlg.success:
                print("Password changed")
        else:
            tkinter.messagebox.showerror('Change Password Error',
                                         'You need to log in first.')

    def do_change_password(self, passwd0, passwd1):
        return self.tut_interface.change_password(passwd0, passwd1)

    def upload_answer(self):
        if self.current_problem:
            if not self.tut_interface.logged_on():
                self.login()
            if not self.tut_interface.logged_on():
                tkinter.messagebox.showerror('Upload Error', 'Not logged in.')
                return
            result = self.tut_interface.upload_answer(self.editor.get_text())
            if result is None:
                return
            if result:
                print("Code uploaded correctly")
                print("WARNING: this does not submit an answer - use Submit Answer")
            else:
                tkinter.messagebox.showerror('Upload Error', 'Upload Error')

    def download_answer(self):
        if self.current_problem:
            reply = self.editor.possiblysave("Save on Download Code")
            if str(reply) == "cancel":
                return
            if not self.tut_interface.logged_on():
                self.login()
            if not self.tut_interface.logged_on():
                tkinter.messagebox.showerror('Download Error', 'Not logged in.')
                return
            result = self.tut_interface.download_answer()
            if result is None:
                return
            if result.startswith('Error'):
                tkinter.messagebox.showerror('Downloadload Error', result)
            else:
                self.editor.preload(result)

    def submit_answer(self, e=None):
        if self.current_problem:
            if not self.tut_interface.logged_on():
                self.login()
            if not self.tut_interface.logged_on():
                tkinter.messagebox.showerror('Submit Error', 'Not logged in.')
                return
            result = self.tut_interface.submit_answer(self.editor.get_text())
            if result == 'OK':
                self.current_problem.set_status('OK')
                self.set_menu_colours()
                print("Answer submitted on time")
                return
            if result == 'LATE':
                self.current_problem.set_status('LATE')
                self.set_menu_colours()
                tkinter.messagebox.showinfo('Late Submission',
                                            'Problem submitted late.')
            if result is None:
                return
            if result.startswith('Error'):
                tkinter.messagebox.showerror('Submit Error', result)

    def set_menu_colours(self):
        result = self.tut_interface.show_submit()
        if result is None:
            return
        result_dict = self.parse_results(result)
        for tut_index, tut_name in enumerate(self.tutorials.tut_list):
            has_not_done = False
            has_late = False
            tut_info = self.tutorials.tut_dict[tut_name]
            menuobj = self.tutorials.get_menu(tut_name)
            for index, problem_name in enumerate(tut_info.problems_list):
                sub = result_dict.get(problem_name, '-')
                tut_info.set_problem_status(problem_name, sub)
                if sub == '-':
                    menuobj.entryconfig(index, foreground='black')
                    has_not_done = True
                elif sub == 'OK':
                    menuobj.entryconfig(index, foreground='blue')
                else:
                    menuobj.entryconfig(index, foreground='red')
                    has_late = True
            if has_not_done:
                self.sectionmenu.entryconfig(tut_index+2, foreground='black')
            elif has_late:
                self.sectionmenu.entryconfig(tut_index+2, foreground='red')
            else:
                self.sectionmenu.entryconfig(tut_index+2, foreground='blue')

    def show_submit(self):
        text = str(self.tutorials)
        tut_textdialog.TextDialog(self.master, "Results", text)

    # Each student results file is of the form
    # ##$$Name of tutorial$$##
    # string flag: 'OK' - submitted on time 'LATE' - submitted late
    # number of checks
    # student code

    def parse_results(self, result):
        lines = result.split('\n')
        result_dict = {}
        length = len(lines)
        i = 0
        while i < length:
            line = lines[i]
            if line.startswith('##$$'):
                header = line[4:-4]
                result_dict[header] = lines[i+1]
                i += 3
            i += 1
        return result_dict

    # Create the tutorial menu based on the information in the tutorials file

    def make_section_menu_entries(self):
        self.reset_menus()
        for index, tutname in enumerate(self.tutorials.tut_list):
            tutinfo = self.tutorials.get_tutorial(tutname)
            tutmenu = Menu(self.sectionmenu, tearoff=0)
            self.sectionmenu.add_cascade(label=tutname, menu=tutmenu)
            self.tutorials.set_menu(tutname, tutmenu)
            for i, prob_name in enumerate(tutinfo.problems_list):
                prob = tutinfo.problems_info[prob_name]
                tutmenu.add_command(label=prob.name,
                                    command=self.set_menu_command(tutname,
                                                                  prob_name))

        self.sectionmenu.add_separator()
        self.sectionmenu.add_command(label="Close", command=self.close_event)
        self.sectionmenu.add_command(label="Exit", command=self.close_event)

    def choose_tutorial(self):
        tut = self.tut_choice.get()
        if self.current_tutorial != tut:
            self.logout()
            self.current_tutorial = tut
            self.tut_dir = self.config.get(tut, 'tut_dir')
            self.ans_dir = self.config.get(tut, 'ans_dir')
            self.setup_tutorial()

    def give_problem_feedback(self):
        if self.current_problem:
            tut_feedback.FeedbackDialog(self.master,
                                        ("Problem Feedback: " +
                                         self.current_problem.name),
                                        self.current_problem,
                                        self.editor.get_text())

    def give_general_feedback(self):
        tut_feedback.FeedbackDialog(self.master, 'General Feedback', '')

    def configure_tut(self):
        result = (fontChooser.FontChooser(self.master, self,
                                          (self.config.get('FONT', 'name'),
                                           self.config.get('FONT', 'size'))
                                          ).result)
        if result:
            self.config.set('FONT', 'name', result[0])
            self.config.set('FONT', 'size', result[1])
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
            self.tut.update_fonts(result[0], int(result[1]))
            self.test_output.update_font(int(result[1]))

    def configure_tut_dir(self):
        if not os.path.exists(self.tut_dir):
            self.tut_dir = HOME_DIR
        dir = tkinter.filedialog.askdirectory(title=('Choose Tutorial Folder: '
                                                     + self.current_tutorial),
                                              initialdir=self.tut_dir)
        if dir:
            self.config.set(self.current_tutorial, 'tut_dir', dir)
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
            self.tut_dir = dir
            if self.sections:
                self.sectionmenu.delete(2, self.sections+6)
            if not self.process_tutorial_file():
                tkinter.messagebox.showerror('Configuration Error',
                                             'Your Tutorial folder is incorrect. Please use the Preferences menu to choose the correct folder.')
            self.tut_interface.set_url(self.URL)
            self.make_section_menu_entries()

    def configure_answers_dir(self):
        if not os.path.exists(self.ans_dir):
            self.ans_dir = HOME_DIR
        dir = tkinter.filedialog.askdirectory(title=('Choose Answers Folder: '
                                                     + self.current_tutorial),
                                              initialdir=self.ans_dir)
        if dir:
            self.config.set(self.current_tutorial, 'ans_dir', dir)
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
            self.ans_dir = dir
            os.chdir(self.ans_dir)

    def add_new_tutorial(self):
        config = tut_configure.TutorConfigure(self.master, self)
        if config.result is None:
            return
        tut_dir, ans_dir, tut_name = config.result
        old_names = self.config.get('TUTORIALS', 'names')
        if tut_name in old_names:
            tkinter.messagebox.showerror('Add New Tutorial Error',
                                         ('The tutorial name %s already exists'
                                          % tut_name))
            return

        self.tutorial_names.append(tut_name)
        self.config.set('TUTORIALS', 'names', ','.join(self.tutorial_names))
        self.config.add_section(tut_name)
        self.config.set(tut_name, 'tut_dir', tut_dir)
        self.config.set(tut_name, 'ans_dir', ans_dir)
        fp = open(CONFIG_FILE, 'w')
        self.config.write(fp)
        fp.close()
        self.radio_menu.delete(0, END)
        for name in self.tutorial_names:
            self.radio_menu.add_radiobutton(label=name,
                                            variable=self.tut_choice,
                                            command=self.choose_tutorial)

    def font_apply(self, font_name, font_size):
        self.tut.update_fonts(font_name, int(font_size))
        if self.test_output:
            self.test_output.update_font(int(font_size))
        if self.editor is not None:
            self.editor.update_font(font_size)

    def next_tutorial(self, e=None):
        self.menu_choice(*self.tutorials.next_tutorial(self.current_tut_name,
                                                       self.current_prob_name))

    def previous_tutorial(self, e=None):
        if (self.current_tut_name is not None and
                self.current_prob_name is not None):
            self.menu_choice(*self.tutorials.previous_tutorial(self.current_tut_name,
                                                               self.current_prob_name))

    def set_menu_command(self, tut_name, prob_name):
        return lambda: self.menu_choice(tut_name, prob_name)

    def menu_choice(self, tut_name, problem_name):
        self.current_tut_name = tut_name
        self.current_prob_name = problem_name
        online = self.URL is not None
        if self.editor is None:
            ## Create a code editor window if none
            self.editor = tut_editor.TutorEditor(self, root=self.master,
                                                 online=online)
            #print "after create edit window"
            self.tut_interface.set_editor(self.editor)
            self.font_apply(self.config.get('FONT', 'name'),
                            self.config.get('FONT', 'size'))
        if self.editor.maybesave() == "cancel":
            return
        answer_file = os.path.join(self.ans_dir,
                                   '_'.join(problem_name.split()) + '.py')
        self.master.title(problem_name)
        self.current_problem = self.tutorials.get_problem(tut_name,
                                                          problem_name)
        self.tut_interface.load_data(os.path.join(self.tut_dir,
                                                  self.current_problem.tut),
                                     problem_name)
        if self.tut_interface.get_text():
            try:
                self.tut.add_text(self.tut_interface.get_text())
                self.tut_interface.reset_editor(answer_file)
                self.editor.undo.reset_undo()
                self.toolbar.set_hints(self.tut_interface.get_hints())
            except Exception as e:
                print('Exception: ' + str(e), file=sys.stderr)

        self.short_description.config(
            text=self.tut_interface.get_short_description()
        )

        # immediately run the tests; this will update the display
        self.run_tests()

    def get_tutorial_info(self):
        return tut_tutorial.TutorialInfo(self.tut_dir)

    def process_tutorial_file(self):
        info = self.get_tutorial_info()
        if info is None:
            self.tutorials = []
            return False
        self.tutorials = info
        self.URL = None
        try:
            config_file = os.path.join(self.tut_dir, 'config.txt')
            fid = open(config_file, 'U')
            text = fid.read()
            fid.close()
            lines = text.split('\n')
            self.timestamp = float(lines[0])
            self.URL = lines[1]
        except:
            return False
        return True

    ## Run the tests on the user code

    def run_tests(self):
        tester, analyser = self.tut_interface.run_tests(self.editor.get_text())

        self.test_output.set_test_results(tester.results)
        self.analysis_output.set_analyser(analyser)

    def get_preloaded(self):
        return self.tut_interface.get_preloaded()

    def showhint(self):
        hint = self.tut_interface.get_next_hint()
        if hint:
            self.tut.show_hint(hint)

    def sizes_changed(self):
        return (self.problem_len !=
                int(self.config.get('WINDOW_SIZES', 'problem')) or
                self.output_len !=
                int(self.config.get('WINDOW_SIZES', 'output')))

    def close_event(self, _e=None):
        self.logout()
        if self.sizes_changed():
            self.config.set('WINDOW_SIZES', 'problem', str(self.problem_len))
            self.config.set('WINDOW_SIZES', 'output', str(self.output_len))
            fp = open(CONFIG_FILE, 'w')
            self.config.write(fp)
            fp.close()
        if self.editor is not None:
            result = self.editor.close()
            if str(result) == 'yes':
                self.master.destroy()
        else:
            self.master.destroy()

    def quit_editor(self):
        self.editor = None

    def about(self):
        tut_dialog.TutAboutDialog(self.master, "About MyPyTutor")

    def help(self):
        tut_help.HelpDialog(self.master, "Help")
