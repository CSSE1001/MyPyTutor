#!/usr/bin/env python

## A Python Tutorial System
## Copyright (C) 2011  Peter Robinson <pjr@itee.uq.edu.au>
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

"""MyPyTutor installer:

Installs MyPyTutor and lib
Creates a problems and answers folder
Installs the tutorial problems into the problems folder
Creates and initializes the configuration file
For Mac users creates a MyPyTutor.command file
"""

from Tkinter import *
import tkFileDialog
import tkMessageBox
import sys
import os
import urllib
import zipfile
from ConfigParser import *
from StringIO import StringIO

# Configuration information
DEFAULT_CONFIG = StringIO("""
[FONT]
name=helvetica
size=10
[WINDOW_SIZES]
problem=20
output=5
[TUTORIALS]
names=CSSE1001Problems
default=CSSE1001Problems
[CSSE1001Problems]
tut_dir =
ans_dir =
""")


def unzipfile(zf, path):
    """Unzip the zip file zf in the folder path."""

    z = zipfile.ZipFile(zf)
    info = z.namelist()
    if not os.path.exists(path):
        os.mkdir(path)
    for item in info:
        if item.endswith('/') or item.endswith('\\'):
            fulldir = os.path.join(path,item)
            if not os.path.exists(fulldir):
                os.mkdir(fulldir)
        else:
            flags = (z.getinfo(item).external_attr >> 16) & 0777
            text = z.read(item)
            fullpath = os.path.join(path,item)
            fd = open(fullpath, 'wb')
            fd.write(text)
            fd.close()
            os.chmod(fullpath, flags)
    z.close()
   
class InstallDirDialog(Toplevel):
    """Dialog for choosing installation folder."""

    def __init__(self, master, parent, default_folder, is_windows):
        Toplevel.__init__( self, master)
        self.master = master
        self.parent = parent
        self.result = None
        self.default_folder = default_folder
        self.title('Install Folder')
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()
        if is_windows:
            label_text = "Folder in which to install MyPyTutor.\n\nDo not install on a memory stick.\nIf you are installing on a lab machine you should install MyPyTutor in the H: drive."
        else:
            label_text = "Folder in which to install MyPyTutor."
        info = Label(self, text=label_text, wraplength = 600, justify = LEFT)
        info.pack()
        dir_frame=Frame(self, relief=SUNKEN,border=3)
        dir_frame.pack(side=TOP,expand=TRUE,fill=BOTH,pady=20)
        Label(dir_frame, text='Installation Folder: ').pack(side=LEFT)
        self.dir_entry = Entry(dir_frame, width=50)
        self.dir_entry.pack(side=LEFT)
        self.dir_entry.insert(0, default_folder)
        Button(dir_frame, text='Select', command = self.select_dir).pack(side=LEFT,padx=10)

        buttonFrame = Frame(self)
        buttonFrame.pack(side=TOP,expand=TRUE,fill=BOTH)
        okButton = Button(buttonFrame, text="OK", command=self.ok)
        cancelButton = Button(buttonFrame, text="Cancel", command=self.cancel)
        okButton.pack(side=LEFT,expand=TRUE)
        cancelButton.pack(side=LEFT,expand=TRUE)
        self.wait_window(self)

    def select_dir(self, e = None):
        self.dir_entry.delete(0,END)
        mpt_dir = tkFileDialog.askdirectory(title='Choose MyPyTutor Installation Folder')
        if mpt_dir:
            self.dir_entry.insert(0, mpt_dir)
        else:
            self.dir_entry.insert(0, self.default_folder)

    def ok(self, e = None):
        self.result = self.dir_entry.get()
        self.withdraw()
        self.update_idletasks()
        self.cancel()

    def cancel(self, e = None):
        self.master.focus_set()
        self.destroy()

class Installer():
    """GUI application for MyPyTutor installer."""

    def __init__(self, master=None):
        self.master = master
        master.title("MyPyTutor Installer")
        top_frame = Frame(master)
        top_frame.pack(fill=BOTH,expand=1)
        self.textwin = Text(top_frame, wrap=WORD, relief=SUNKEN)
        self.textwin.pack()
        button_frame = Frame(master)
        button_frame.pack()
        Button(button_frame, text="Exit", command = self.quit).pack(side=LEFT, expand=1)
        if self.python_version() is None:
            return
        if self.platform() is None:
            return
        self.run_installer()

    def quit(self):
        self.master.destroy()

    def add_text(self, text):
        """Add text to the end of the text widget."""
        self.textwin.insert(END, text)

    def python_version(self):
        """Check if the version is Python is suitable - set self.version.""" 
        self.version = sys.version_info[:2]
        if self.version not in [(2,7)]:
            self.add_text("\nYou are running Python version %d.%d. You need to install Python 2.7\n" % self.version) 
            return None
        else:
            #print "Python version: ", self.version
            return self.version

    def platform(self):
        """Check if the platform is suitable - set self.os"""
        platfrm = sys.platform
        if platfrm.startswith('linux'):
            self.os = 'linux'
        elif platfrm in ['win32', 'darwin']:
            self.os = platfrm
        else:
            self.add_text("\nYour operating system is %s, this installer is for Windows, Mac OSX and Linux.\n\nYou will need to do a manual install.\n" % platfrm)
            return None
        return self.os

    def run_installer(self):
        """Run the installer"""
        self.add_text('\nChoosing folder in which to install MyPyTutor...')
        if self.os == 'win32':
            self.add_text('\nDo not install on a memory stick.\n')
            self.add_text('\nIf you are installing on a lab machine you should install MyPyTutor in the H: drive.\n')
        # Choose the installation folder
        home = os.path.expanduser('~')
        default_mpt_folder = os.path.join(home, 'MyPyTutor')
        install_dialog = InstallDirDialog(self.master, self, default_mpt_folder, self.os == 'win32')
        mpt_folder = install_dialog.result
        self.add_text('\n')
        if mpt_folder is None:
            self.add_text('\nYou did not choose a folder. Please re-run the installer\n')
            return
        # Check if folder is already present - if not create required folders
        if os.path.isfile(mpt_folder):
            tkMessageBox.showerror("Installation folder.", "%s is not a folder", mpt_folder)
            self.add_text('\nPlease re-run the installer and choose an installation folder.')
            return 
        folder_exists = False
        if os.path.isdir(mpt_folder):
            exists_answer = tkMessageBox.askquestion("Folder Exists",
                                                     "The folder you have chosen already exists - continue?")
            folder_exists = True
            if exists_answer != 'yes':
                self.add_text('\nPlease re-run the installer and choose a different installation folder\n')
                return
        if not folder_exists and not self.create_folders(mpt_folder):
            return
        self.add_text('\nMyPyTutor will be installed in %s\n' % mpt_folder)
        self.master.update_idletasks()
        # Create problems and answers folders
        tutorial_dir = os.path.join(mpt_folder, 'CSSE1001Problems')
        answer_dir = os.path.join(mpt_folder, 'CSSE1001Answers')
        if os.path.isdir(tutorial_dir):
            self.add_text('Using %s as problems folder\n' % tutorial_dir)
        else:
            try:
                os.mkdir(tutorial_dir)
                self.add_text('Creating problems folder: %s\n' % tutorial_dir)
            except:
                tkMessageBox.showerror("Problems folder.", "Cannot create the problems folder: %s", tutorial_dir)
                return
        if os.path.isdir(answer_dir):
            self.add_text('Using %s as answers folder\n' % answer_dir)
        else:
            try:
                os.mkdir(answer_dir)
                self.add_text('Creating answers folder: %s\n' % answer_dir)
            except:
                tkMessageBox.showerror("Answers folder.", "Cannot create the answers folder: %s", answer_dir)
                return
        # Download and unzip MyPyTutor
        self.add_text('Downloading MyPyTutor...\n')
        self.master.update_idletasks()
        urlobj = urllib.URLopener({})
        urlobj.retrieve('http://csse1001.uqcloud.net/mpt/MyPyTutor%d%d.zip' % self.version, 'mpt.zip')
        unzipfile('mpt.zip', mpt_folder)
        os.remove('mpt.zip')
        self.add_text('MyPyTutor.py is located in %s\n' % mpt_folder)
        # Download and unzip the problems
        self.add_text('Downloading tutorial problems...\n')
        self.master.update_idletasks()
        urlobj = urllib.URLopener({})
        urlobj.retrieve('http://csse1001.uqcloud.net/mpt/CSSE1001Tutorials.zip', 'CSSE1001Tutorials.zip')
        unzipfile('CSSE1001Tutorials.zip', tutorial_dir)
        os.remove('CSSE1001Tutorials.zip')
        # set up config file
        self.add_text('Creating configuration file...\n')
        self.master.update_idletasks()
        config = ConfigParser()
        config.readfp(DEFAULT_CONFIG)
        config.set('CSSE1001Problems', 'tut_dir', tutorial_dir)
        config.set('CSSE1001Problems', 'ans_dir', answer_dir)
        config_file = os.path.join(home, 'mypytutor.cfg')
        fp = open(config_file, 'w')
        config.write(fp)
        fp.close()
        self.add_text('Configuration file: %s\n' % config_file) 
        # for Mac users create a MyPyTutor.command file
        if self.os == 'darwin':
            command_file = os.path.join(mpt_folder, 'MyPyTutor.command')
            exec_file = os.path.join(mpt_folder, 'MyPyTutor.py').replace(" ", "\ ")  # escape spaces in path
            fd = open(command_file, 'w')
            fd.write('%s\n' % exec_file)
            fd.close()
            os.system('chmod +x %s' % command_file)
            self.add_text('Run MyPyTutor by double clicking on %s\n' % command_file)
        self.add_text('Installation complete!')

    def create_folders(self, path):
        """Go through path and add folders as required to make path a 'valid'
        path to a folder. Return True iff successful"""

        dirs = []
        while True:
            path, folder = os.path.split(path)
            if folder == '':
                break
            #print path, folder
            dirs.append(folder)
        dirs.reverse()
        #print dirs, path
        for d in dirs:
            path = os.path.join(path, d)
            #print path
            if os.path.isfile(path):
                tkMessageBox.showerror("Installation folder.", "%s is not a folder", path)
                return False
            if not os.path.isdir(path):
                try:
                    os.mkdir(path)
                    self.add_text('Creating folder %s\n' % path)
                except:
                    tkMessageBox.showerror("Installation folder.", "Cannot create folder %s", path)
                    return False
        return True

def main():
    root = Tk()
    Installer(root)
    root.mainloop()
    
if __name__ == '__main__': 
    main()
