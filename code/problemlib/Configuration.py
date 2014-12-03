
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

import ConfigParser 
from StringIO import StringIO
import os


DEFAULT_TUTOR_CONFIG = StringIO("""
[FONT]
name=helvetica
size=10
[DIRECTORY]
name=
""")

DEFAULT_CONFIG = StringIO("""
[DB_DIRECTORY]
name=
""")

HOME_DIR = os.path.expanduser('~')
CONFIG_FILE = os.path.join(HOME_DIR, 'mypytutor.cfg')
PROBLEMS_CONFIG_FILE = os.path.join(HOME_DIR, '.problems.cfg')

class Configuration:
    def __init__(self):
        self.tutor_config = ConfigParser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            fid = open(CONFIG_FILE)
            self.tutor_config.readfp(fid)
            fid.close()
        else:
            self.tutor_config.readfp(DEFAULT_TUTOR_CONFIG)

        self.config = ConfigParser.ConfigParser()
        if os.path.exists(PROBLEMS_CONFIG_FILE):
            fid = open(PROBLEMS_CONFIG_FILE)
            self.config.readfp(fid)
            fid.close()
        else:
            self.config.readfp(DEFAULT_CONFIG)


    def get_fontsize(self):
        return self.tutor_config.get('FONT', 'size')

    def get_fontname(self):
        return self.tutor_config.get('FONT', 'name')

    def set_font(self, name, size):
        self.tutor_config.set('FONT', 'name', name)
        self.tutor_config.set('FONT', 'size', size)
        fid = open(CONFIG_FILE, 'w')
        self.tutor_config.write(fid)
        fid.close()

    def get_db_dir(self):
        return self.config.get('DB_DIRECTORY', 'name')

    def set_db_dir(self, db_dir):
        self.config.set('DB_DIRECTORY', 'name', db_dir)
        fid = open(PROBLEMS_CONFIG_FILE, 'w')
        self.config.write(fid)
        fid.close()
