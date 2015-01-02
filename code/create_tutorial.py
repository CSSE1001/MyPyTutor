#!/usr/bin/env python3

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


## An application for creating tutorials by collecting together
## individual problems.

import os
import sys
import shutil
from tutorlib.interface.tutorial import Tutorial
import problemlib.Configuration as Configuration
import uuid
import time
import zipfile
import glob
import logging
import py_compile

def generate(config_file, destination_dir, source_dir=None):
    """Generate a Tutorial set from the given configuration file.
    Example usage:
    generate('problem_db/CSSE1001.txt', 'CSSE1001Tutorials')
    """
    if source_dir is None:
        source_dir = os.path.split(config_file)[0]

    with open(config_file, 'rU') as f:
        tutorial_text = f.read()

    return generate_text(tutorial_text, destination_dir, source_dir)


def generate_text(tutorial_text, destination_dir, source_dir):
    # Fail if the destination already exists
    if os.access(destination_dir, os.F_OK):
        logging.error(destination_dir+' already exists')
        return 1
    else:
        os.mkdir(destination_dir)

    parent_dir, dir_name = os.path.split(destination_dir)
    tutorials, extra_files = parse_tutorial(tutorial_text)

    # Create index files
    # TODO: change tut_admin.txt to tutorial_hashes, in correct format
    admin_fid = open(os.path.join(parent_dir, 'tut_admin.txt'), 'w')
    tut_fid = open(os.path.join(destination_dir, 'tutorials.txt'), 'w')
    with admin_fid, tut_fid:
        logging.info('Adding tutorials.txt')
        id_list = []
        url = ''
        for line in tutorial_text.strip('\n').split('\n'):
            if line.startswith('[URL:'):
                url = line[5:-1]
            elif ':' in line:
                id = uuid.uuid4().hex
                id_list.append(id)
                title, fname, *rest = map(str.strip, line.split(':'))
                print(title + ':' + fname, file=tut_fid)
                print(str(id) + ' ' + title, file=admin_fid)
            else:
                print(line, file=tut_fid)
                print(line, file=admin_fid)

    if url:
        with open(os.path.join(destination_dir, 'config.txt'), 'w') as fid:
            now = time.localtime()
            print(time.mktime(now), file=fid)
            print(url, file=fid)

    # Add auxiliary files
    for ofile in extra_files:
        logging.info('Adding ' + ofile)
        filename = os.path.join(source_dir, ofile)
        newfilename = os.path.join(destination_dir, ofile)
        shutil.copyfile(filename, newfilename)

    # Encode and add tutorial files
    for tutorial_name in tutorials:
        logging.info('Adding ' + tutorial_name)
        directory = os.path.join(source_dir, tutorial_name)

        # check the directory exists
        if not os.path.exists(directory):
            logging.error('Failed - no such tutorial {}'.format(tutorial_name))
            continue
        if not os.path.isdir(directory):
            logging.error('Failed - .tut should be a directory: {}'.format(
                tutorial_name
            ))
            continue

        # check that all tutorial files are present
        files = os.listdir(directory)
        tutorial_valid = True
        required_files = Tutorial.SUBMODULES + Tutorial.FILES

        for file in required_files:
            if file not in files:
                logging.error('Failed - {} is missing {}'.format(
                    tutorial_name, file
                ))
                tutorial_valid = False

        if not tutorial_valid:
            continue

        # create the directory
        destination_tutorial_dir = os.path.join(destination_dir, tutorial_name)
        os.mkdir(destination_tutorial_dir)

        # copy over the files, compiling as necessary
        for file in files:
            _, extension = os.path.splitext(file)

            if extension == '.py':
                pass  # TODO: compilation (including for different versions)

            src_path = os.path.join(directory, file)
            dest_path = os.path.join(destination_tutorial_dir, file)

            shutil.copyfile(src_path, dest_path)

    # Zip everything together
    cwd=os.getcwd()
    os.chdir(destination_dir)
    all_files = glob.glob("*")
    zfile = zipfile.ZipFile(dir_name+'.zip', 'w')
    for file in all_files:
        zfile.write(file)
    zfile.close()
    os.chdir(cwd)
    return 0

def parse_tutorial(text):
    logging.info('Checking syntax')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    files = []
    extra_files = []
    if not lines:
        logging.error('No data')
        return (files, extra_files)

    if lines[0][0] != '[':
        logging.error('First line should be [...]')
        return (files, extra_files)

    okay = True
    for num, line in enumerate(lines):
        if line[0] == '[':
            if line[-1] != ']':
                okay = False
                logging.error('Unmatched [] on line '+str(num))
        else:
            parts = line.split(':')
            if len(parts) < 2:
                okay = False
                logging.error('Invalid Syntax on line '+str(num))
            else:
                files.append(parts[1].strip())
                for f in parts[2:]:
                    f = f.strip()
                    if f not in extra_files:
                        extra_files.append(f)
    if okay:
        logging.info('Syntax OK')
    return (files, extra_files)


def main():
    # TODO use argparse
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: {} config_file destination_dir".format(sys.argv[0]),
              file=sys.stderr)
        return 2
    else:
        return generate(*args)

if __name__ == '__main__':
    sys.exit(main())
