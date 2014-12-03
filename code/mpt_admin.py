#!/usr/bin/env python

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

## An application for carrying out admin for MyPyTutor online material.


from tkinter import * 
import os
import sys
import urllib.request, urllib.parse, urllib.error
from io import StringIO
import tkinter.messagebox

import tkinter.filedialog

import tutorlib.TutorialInterface as tut_interface
import problemlib.Configuration as tut_config
import tutorlib.passworddialogs as tut_password_dialogs
import smtplib
from email.mime.text import MIMEText

#########################################################################
#
# Start of configuration
#
# Below needs to be modified for your needs
#

# The title of this application

application_title = 'MyPyTutor Administration'

# The folder containing the tutorial to be administered

tutorial_directory = '/home/pjr/MyPyTutor/CSSE1001Problems'

# The host for sending email registration notices

smtp_host = 'smtp.uq.edu.au'

# The header for registration emails
 
email_header = "CSSE1001/CSSE7030: Registration for MyPyTutor"

# The body of the email. This string uses formating and is used in the
# code as  email_text % (username, password)

email_text = """In CSSE1001/CSSE7030 you will be using MyPyTutor for doing 
online tutorial problems. You have been automatically registered for MyPyTutor.

Username: %s
Password: %s

You need to first download and install MyPytutor and the tutorial problems
to your machine. When you have done this, start up MyPyTutor, log on using
the above username and password and change your password.

Details on how to download MyPyTutor can be found on the course web site at

http://csse1001.uqcloud.net/

"""

# The from address for the registration emails (administrators address)

from_email_address = 'pjr@itee.uq.edu.au'

# For registering of students whose information is contained in a file
# (with one student info per line), the required information needs to
# be accessed. The registation processing uses the function below
# to parse this information for a line of the student file.

def parse_student_info(line):
    """Takes a line from a student file and parses it into a tuple of
    strings of the form (username, email, familyname, givennames).
    The function should return () if the line is to be ignored and None
    if there is a parse error.
    """
    if line.strip() == '':
        return ()
    parts = line.split(',')
    if len(parts) > 5:
        first_names = parts[4].split()
        if first_names:
            givennames = first_names[0]
        else:
            givennames = ''
        familyname = parts[3].strip()
        email = parts[5].strip()
        username = email.split('@')[0]
        return (username, email, familyname, givennames)
    else:
        return None
 
#
#
# End of configuration
#
##############################################################

class AddUserDialog(Toplevel):
    def __init__(self, master, parent):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.title('Add User')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.user = StringVar()
        self.first = StringVar()
        self.last = StringVar()
        self.email = StringVar()
        self.password = StringVar()
        self.type = StringVar()
        self.CreateWidgets()
        self.transient(master)
        self.wait_visibility()
        self.grab_set()

    def CreateWidgets(self): 
        typeframe = Frame(self)
        typeframe.pack(expand=TRUE,fill=X)
        Label(typeframe, text = 'User Type: ').pack(side=LEFT,
                                                    anchor=W,expand=TRUE)

        self.type_choice = OptionMenu(typeframe, self.type, 'student','staff','admin')
        self.type_choice.pack()
        self.type.set('student')
        emailframe = Frame(self)
        emailframe.pack(expand=TRUE,fill=X)
        Label(emailframe, text = "Send Email?").pack(side=LEFT,
                                                    anchor=W,expand=TRUE)
        self.sendemail = IntVar()
        Radiobutton(emailframe, text="Yes", variable=self.sendemail, value=1).pack(side=LEFT,anchor=W)
        Radiobutton(emailframe, text="No", variable=self.sendemail, value=0).pack(side=LEFT,anchor=W)
        self.sendemail.set(1)
        userframe = Frame(self)
        userframe.pack(expand=TRUE,fill=X)
        Label(userframe, text = 'Username: ').pack(side=LEFT,
                                                   anchor=W,expand=TRUE)
        self.user_entry = Entry(userframe, textvariable=self.user, width=20)
        self.user_entry.pack(side=LEFT)
        firstframe = Frame(self)
        firstframe.pack(expand=TRUE,fill=X)
        Label(firstframe, text = 'First Name(s): ').pack(side=LEFT,
                                                         anchor=W,expand=TRUE)
        self.first_entry = Entry(firstframe, textvariable=self.first, width=20)
        self.first_entry.pack(side=LEFT)
        lastframe = Frame(self)
        lastframe.pack(expand=TRUE,fill=X)
        Label(lastframe, text = 'Family Name: ').pack(side=LEFT,
                                                      anchor=W,expand=TRUE)
        self.last_entry = Entry(lastframe, textvariable=self.last, width=20)
        self.last_entry.pack(side=LEFT)
        emailframe = Frame(self)
        emailframe.pack(expand=TRUE,fill=X)
        Label(emailframe, text = 'Email: ').pack(side=LEFT,
                                                 anchor=W,expand=TRUE)
        self.email_entry = Entry(emailframe, textvariable=self.email, width=20)
        self.email_entry.pack(side=LEFT)
        frameButtons = Frame(self)
        passframe = Frame(self)
        passframe.pack(expand=TRUE,fill=X)
        Label(passframe, text = 'Password: ').pack(side=LEFT,
                                                   anchor=W,expand=TRUE)
        self.pass_entry = Entry(passframe, textvariable=self.password, width=20, show="*")
        self.pass_entry.pack(side=LEFT)
        frameButtons = Frame(self)
        frameButtons.pack()
        self.buttonSubmit = Button(frameButtons, text='Submit',
                                   command=self.submit)
        self.buttonSubmit.pack(side=LEFT, expand=1)
        self.buttonCancel = Button(frameButtons, text='Close',
                               command=self.cancel)
        self.buttonCancel.pack(side=LEFT,expand=1)

 
    def submit(self):
        user = self.user.get().strip()
        firstname = self.first.get().strip()
        lastname = self.last.get().strip()
        email = self.email.get().strip()
        passwd = self.password.get().strip()
        type_ = self.type.get().strip()
        send_email = (self.sendemail.get() == 1)
        if user == '' or firstname == ' ' or lastname == '' or email == '':
            tkinter.messagebox.showerror('Add User Error', 
                                   'Not all fields filled.')
            return
        if passwd == '':
            passwd = '-'
        result = self.parent.add_user(user, type_, firstname, 
                                      lastname, email, passwd, send_email)
        self.password.set(result)
        self.destroy()

    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class AddUsersDialog(Toplevel):
    def __init__(self, master, parent):
        Toplevel.__init__(self, master)
        self.title('Add Users From File')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.parent = parent
        self.type = StringVar()
        self.CreateWidgets()
        self.transient(master)
        self.wait_visibility()
        self.grab_set()

    def CreateWidgets(self): 
        typeframe = Frame(self)
        typeframe.pack(expand=TRUE,fill=X)
        Label(typeframe, text = 'User Type: ').pack(side=LEFT,
                                                    anchor=W,expand=TRUE)

        self.type_choice = OptionMenu(typeframe, self.type, 'student','staff','admin')
        self.type_choice.pack()
        self.type.set('student')
        file_frame = Frame(self)
        file_frame.pack(side=TOP,expand=TRUE,fill=BOTH,pady=20)
        Label(file_frame, text='Student File: ').pack(side=LEFT)
        self.file_entry = Entry(file_frame, width=50)
        self.file_entry.pack(side=LEFT)
        Button(file_frame, text='Select', command = self.select_file).pack(side=LEFT,padx=10)
        frameButtons = Frame(self)
        frameButtons.pack()
        self.buttonSubmit = Button(frameButtons, text='Submit',
                                   command=self.submit)
        self.buttonSubmit.pack(side=LEFT, expand=1)
        self.buttonCancel = Button(frameButtons, text='Cancel',
                               command=self.cancel)
        self.buttonCancel.pack(side=LEFT,expand=1)

    def select_file(self):
        self.file_entry.delete(0,END)
        file = tkinter.filedialog.askopenfilename(title='Choose Student File')
        if file:
           self.file_entry.insert(0, file)

    def submit(self):
        type = self.type.get().strip()
        class_file = self.file_entry.get()
        self.parent.add_users_from_file(type, class_file)
        
    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class UnsetLateDialog(Toplevel):
    def __init__(self, master, parent):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.title('Unset Late Flag')
        self.protocol("WM_DELETE_WINDOW", self.close_unset)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        entry_frame = Frame(self)
        entry_frame.pack(pady=10)
        Label(entry_frame, text='User:').pack(side=LEFT)
        self.entry = Entry(entry_frame, width=20)
        self.entry.pack()
        self.entry.bind('<Return>', self.get_info)
        self.listb = Listbox(self, height=40, width=60, borderwidth=2, relief='sunken',selectmode='multiple')
        self.listb.pack()
        self.listb.config(font = ('courier',10))
        button_frame = Frame(self)
        button_frame.pack(fill=X)
        Button(button_frame, text='Clear All', command=self.clear_all).pack(side=LEFT,expand=1)
        Button(button_frame, text='Select All', command=self.select_all).pack(side=LEFT,expand=1)
        Button(button_frame, text='Update', command=self.update).pack(side=LEFT,expand=1)
        Button(button_frame, text='Close', command=self.close_unset).pack(side=LEFT,expand=1)

    def get_info(self, e=None):
        self.listb.delete(0,self.listb.size())
        self.user = self.entry.get()
        info = self.parent.get_user_subs(self.user)
        if 'Error' in info:
            print(info)
            return
        info = info.split('\n')
        self.info = info
        self.user = self.entry.get()
        formatted_info = []
        for line in info:
            line = line.split(':::')
            name = line[0]
            status = line[1]
            formatted_info.append(name + (40-len(name))*' '+status)
        self.listb.insert(0, *formatted_info)

    def select_all(self):
        self.listb.selection_set(0,self.listb.size())

    def clear_all(self):
        self.listb.selection_clear(0,self.listb.size())

    def update(self):
        for item in self.listb.curselection():
            problem_info = self.info[int(item)].split(':::', 1)
            name = problem_info[0]
            status = problem_info[1].strip()
            if status == 'LATE':
                self.parent.unset_late(self.user, name)
        self.get_info()
            

    def close_unset(self, _event = None):
        self.master.focus_set()
        self.destroy()

class MatchDialog(Toplevel):
    def __init__(self, master, parent):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.title('Match Pattern')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        entry_frame = Frame(self)
        entry_frame.pack(pady=10)
        Label(entry_frame, text='Match Pattern:').pack(side=LEFT)
        self.entry = Entry(entry_frame, width=40)
        self.entry.pack()
        self.entry.bind('<Return>', self.get_matches)
        self.textwin = Text(self, width = 100, height = 40)
        self.textwin.pack()

    def get_matches(self, e=None):
        self.textwin.delete(1.0,END)
        pattern = self.entry.get()
        result = self.parent.match(pattern)
        self.textwin.insert(END, result)

    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class ResultsDialog(Toplevel):
    def __init__(self, master, parent, results):
        Toplevel.__init__(self, master)
        self.master = master
        self.parent = parent
        self.title('Results')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.parse_results(results)
        buttons_frame = Frame(self)
        buttons_frame.pack(pady=10)
        Button(buttons_frame, text='Submit Info', 
               command=self.submit_info).pack(side=LEFT)
        Button(buttons_frame, text='Check Info', 
               command=self.check_info).pack(side=LEFT)
        Button(buttons_frame, text='View Student Results', 
               command=self.student_results).pack(side=LEFT)
        Button(buttons_frame, text='Save Student Results', 
               command=self.save_student_results).pack(side=LEFT)

        self.textwin = Text(self, width = 100, height = 40)
        self.textwin.pack()

    def submit_info(self):
        self.textwin.delete(1.0,END)
        problem_totals = {}
        num_students = self.num_students
        if num_students == 0:
            return
        for key in self.user_results:
            result = self.user_results[key]
            for i, v in enumerate(result):
                if v != '-':
                    problem = self.problem_list[i]
                    total = problem_totals.get(problem, 0) + 1
                    problem_totals[problem] = total
        for problem in self.problem_list:
            total  = problem_totals.get(problem, 0)
            self.textwin.insert(END, problem + (40-len(problem))*' ' + \
                                    ('%3d  %6.2f\n' % \
                                         (total, 100.0*total/num_students)))

    def check_info(self):
        self.textwin.delete(1.0,END)
        problem_totals = {}
        num_students = self.num_students
        for key in self.user_results:
            result = self.user_results[key]
            for i, v in enumerate(result):
                if v != '-':
                    checks = int(v.split('/')[1])
                    problem = self.problem_list[i]
                    total, num = problem_totals.get(problem, (0,0))
                    problem_totals[problem] = (total+checks, num+1)
        for problem in self.problem_list:
            total, num  = problem_totals.get(problem, (0, 0))
            if num != 0:
                self.textwin.insert(END, problem + (40-len(problem))*' ' + \
                                        ('%3d  %6.2f\n' % \
                                             (num, float(total)/num)))


    def student_results(self):
        num_problems = self.num_problems
        self.textwin.delete(1.0,END)
        for key in self.user_results:
            result = self.user_results[key]
            num = 0
            for v in result:
                if 'OK' in v:
                    num += 1
            self.textwin.insert(END, "%s,%6.2f\n" % (key, 100.0*num/num_problems))
    def save_student_results(self):
        savefile = \
            tkinter.filedialog.asksaveasfile(mode='w', 
                                       initialdir= os.path.expanduser('~'))
        if savefile:
            num_problems = self.num_problems
            self.textwin.delete(1.0,END)
            for key in self.user_results:
                result = self.user_results[key]
                num = 0
                for v in result:
                    if 'OK' in v:
                        num += 1
                savefile.write("%s,%6.2f\n" % (key, 100.0*num/num_problems))
            savefile.close()    
            

    def parse_results(self, results):
        problem_list = []
        user_results = {}
        results_list = results.split('\n')
        length = len(results_list)
        i = 0
        doing_problems = True
        while i < length:
            line = results_list[i]
            i += 1
            if line.startswith('#####'):
                doing_problems = False
                continue
            if doing_problems:
                problem_list.append(line)
            else:
                info = line.split(',')
                name = info.pop(0)
                user_results[name] = info
        self.problem_list = problem_list
        self.user_results = user_results
        self.num_problems = len(problem_list)
        self.num_students = len(list(user_results.keys()))

    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class RegistrationLog(Toplevel):
    def __init__(self, master):
        Toplevel.__init__(self, master)
        self.master = master
        self.title('Registration Log')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.textwin = Text(self, width = 100, height = 40)
        self.textwin.pack()

    def logit(self, text):
        self.textwin.insert(INSERT, text)
        self.textwin.see(END)

    def cancel(self, _event = None):
        self.master.focus_set()
        self.destroy()

class MPTAdmin():
    def __init__(self, master=None):
        master.title(application_title)
        self.master = master
        self.tut_dir = tutorial_directory
        master.protocol("WM_DELETE_WINDOW", self.close_event)
        try:
            config_file = os.path.join(self.tut_dir, 'config.txt')
            fid = open(config_file, 'U')
            text = fid.read()
            fid.close()
            lines = text.split('\n')
            self.trans = tut_interface.Trans(77213) 
            self.URL = self.trans.trans(lines[1], 'tutor key').strip()
        except Exception as e:
            print(str(e))

        Label(text=80*' ').pack()
        
        # Add User
        Button(text = 'Add User', width = 20, 
               command=self.do_add_user).pack()

        # Add Users from file
        Button(text = 'Add Users From File', width = 20, 
               command=self.do_add_users).pack()

        # Change User password
        Button(text = 'Change User Password', width = 20, 
               command=self.do_password).pack()

        # Unset Late Flag
        Button(text = 'Unset Late Flag', width = 20, 
               command=self.do_unset_late).pack()

        # Match Pattern
        Button(text = 'Match Pattern', width = 20, 
               command=self.do_match).pack()

        # Results
        Button(text = 'Results', width = 20, 
               command=self.do_results).pack()

        Label(text=80*' ').pack()


        self.key = None
        self.user = None
        self.admin_login()
        if self.key is None:
            self.master.destroy()

    def send_data(self, form_dict):
        try: 
            data = urllib.parse.urlencode(form_dict)
            response = urllib.request.urlopen("%s?%s" %(self.URL, data), 
                                      proxies = {})
            text = response.read().strip()
            print(text)
            if text.startswith('mypytutor>>>'):
                return text[12:]
            else:
                return 'Exception: Invalid response'
        except Exception as e:
            return 'Exception: '+str(e)

    
    def admin_login(self):
        tut_password_dialogs.LoginDialog(self, self.do_login)

    def close_event(self, _e = None):
        self.logout()

    def logout(self):
        values = {'action':'logout',
                  'username':self.user,
                  'session_key':self.key,
                  }
        result = self.send_data(values)
        self.master.destroy()

    def do_match(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
            return
        MatchDialog(self.master, self)

    def do_unset_late(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
            return
        UnsetLateDialog(self.master, self)

    def do_results(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
            return

        self.results()

    def do_login(self, user, passwd):
        values = {'action':'login',
                  'username' : user,
                  'password' : passwd,
                  'type': 'admin'}
        result = self.send_data(values).strip()
        if result.startswith('Error'):
            tkinter.messagebox.showerror('Login Error', 'Login Failed.')
            return
        self.user = user
        parts = result.split()
        self.key = parts[1].strip()

    def match(self, pattern):
        values = {'action':'match',
                  'username':self.user,
                  'session_key':self.key,
                  'type': 'admin',
                  'match':pattern
                  }
        result = self.send_data(values)
        return result

    def do_add_user(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
        AddUserDialog(self.master, self)

    def do_add_users(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
        AddUsersDialog(self.master, self)

    def do_password(self):
        if self.key is None:
            tkinter.messagebox.showerror('Admin Error', 'Not logged in.')
        tut_password_dialogs.LoginDialog(self, self.change_user_password,
                                         title='Change User Password.')

    def change_user_password(self, the_user, passwd):
        values = {'action':'change_user_password',
                  'username':self.user,
                  'session_key':self.key,
                  'type': 'admin',
                  'the_user':the_user,
                  'password':passwd
                  }
        result = self.send_data(values).strip()
        if result.startswith('Error'):
            tkinter.messagebox.showerror('Admin Error', result)

    def unset_late(self, the_user, problem):
        print('unset_late', the_user, problem)
        values = {'action':'unset_late',
                  'username':self.user,
                  'session_key':self.key,
                  'type': 'admin',
                  'the_user':the_user,
                  'problem':problem
                  }
        result = self.send_data(values)
        print(result)

    def results(self):
        values = {'action':'results',
                  'username':self.user,
                  'session_key':self.key              
                  }
        result = self.send_data(values)
        ResultsDialog(self.master, self, result)

    def get_user_subs(self, user):
        values = {'action':'get_user_subs',
                  'username':self.user,
                  'session_key':self.key,
                  'the_user':user
                  }
        result = self.send_data(values)
        return result

    def add_user(self, user, type_, firstname, lastname, email, passwd, send_email):
        values = {'action':'add_user',
                  'username':self.user,
                  'session_key':self.key,
                  'the_user':user,
                  'type':type_,
                  'firstname':firstname,
                  'lastname':lastname,
                  'email':email,
                  'password':passwd
                  }
        result = self.send_data(values).strip()
        if result.startswith('Error'):
            tkinter.messagebox.showerror('Add User Error', 'Add User Failed.')
            return None
        passwd = result.strip()
        if send_email:
            try:
                smpt = smtplib.SMTP()
                smpt.connect(smtp_host)
                msg = MIMEText(email_text % (user, passwd))
                msg['Subject'] = email_header
                msg['From'] = from_email_address
                msg['To'] = email
                smpt.sendmail(from_email_address, [email], msg.as_string())
                smpt.close()
            except:
                return None
 
        return result

    def add_users_from_file(self, type_, class_file):
        registration_log = RegistrationLog(self.master)
        try:
            f = open(class_file, 'U')
            lines = f.readlines()
            f.close()
            smpt = smtplib.SMTP()
            smpt.connect(smtp_host)
        except Exception as e:
            registration_log.logit("****** Error %s\n" % str(e))
            return
        for line in lines:
            parsed_line = parse_student_info(line)
            if parsed_line == ():
                continue
            if parsed_line is None:
                registration_log.logit('****** Parse error for %s\n' % line)
                continue
            username, email, familyname, givennames = parsed_line
            registration_log.logit("%s, %s, %s, %s" % parsed_line)
            values = {'action':'add_user',
                      'username':self.user,
                      'session_key':self.key,
                      'the_user':username,
                      'type':type_,
                      'firstname':givennames,
                      'lastname':familyname,
                      'email':email,
                      'password':'-'
                      }
            result = self.send_data(values).strip()
            if 'Error' in result:
                registration_log.logit('   *** %s\n' % result) 
                continue
            password = result.strip()
            try:
                msg = MIMEText(email_text % (username, password))
                msg['Subject'] = email_header
                msg['From'] = from_email_address
                msg['To'] = email
                smpt.sendmail(from_email_address, [email], msg.as_string())
                registration_log.logit('\n')
            except Exception as e:
                registration_log.logit("   *** Error %s\n" % str(e))
            self.master.update()
        smpt.close()
        registration_log.logit('++++++ Registration Complete ++++++')
        self.master.update()
   

def main():
    root = Tk()
    MPTAdmin(root)
    root.mainloop()
    
if __name__ == '__main__': 
    main()
