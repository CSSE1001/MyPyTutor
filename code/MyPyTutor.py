#!/usr/bin/env python3

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

"""The MyPyTutor application."""

import os
import sys
import tkinter as tk

from tutorlib.gui.app.app import TutorialApp, VERSION
from tutorlib.gui.app.support import safely_extract_zipfile
from tutorlib.interface.web_api import WebAPI, WebAPIError


def bootstrap():
    """
    Update MyPyTutor if necessary.

    If an update is available, this function will not return.

    """
    try:
        _bootstrap()
    except WebAPIError:
        pass  # no internet connection


def _bootstrap():
    web_api = WebAPI()

    # grab the server version
    version = web_api.get_version()

    create_tuple = lambda v: tuple(map(int, v.split('.')))
    server_version = create_tuple(version)
    local_version = create_tuple(VERSION)

    if server_version > local_version:
        # grab our new zip file
        mpt_zip_path = web_api.get_mpt_zipfile()

        # extract over the script path
        # do NOT delete things; the user could have other stuff here
        script_dir = os.path.dirname(os.path.realpath(__file__))

        safely_extract_zipfile(mpt_zip_path, script_dir)

        # re-exec with the new version
        os.execl(sys.executable, sys.executable, *sys.argv)


def main():
    """
    The main entry point for MyPyTutor.

    If there is no internet connection, MyPyTutor will terminate.

    Otherwise, it will first check for updates, before running the app itself.

    """
    bootstrap()

    root = tk.Tk()
    TutorialApp(root)
    root.mainloop()

    
if __name__ == '__main__': 
    main()
