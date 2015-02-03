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

import argparse
from collections import OrderedDict, namedtuple
import glob
from itertools import chain
import os
import shutil
import sys
import time
import zipfile

from hashes import update_hashes
from tutorlib.interface.tutorial import Tutorial


class TutorialCreationError(Exception):
    """
    An error encountered when creating a tutorial package.

    """
    pass


def generate_tutorial_package(config_file, destination_dir, source_dir=None,
        ignore_invalid_tutorials=False, verbose=False):
    """
    Generate a Tutorial set from the given configuration file.

    Example usage:
    generate('problem_db/CSSE1001.txt', 'CSSE1001Tutorials')

    Args:
      config_file (str): The path to the configuration file to use.
      destination_dir (str): The path to a directory to output the tutorial
          package to.
      source_dir (str, optional): The path to the source directory for the
          problem sets.  Defaults to the directory of the config file.
      ignore_invalid_tutorials (bool, optional): Whether to ignore invalid
          tutorials, and proceed anyway.  If True, exceptions encountered when
          creating tutorials will be suppressed. Defaults to False.

    """
    if source_dir is None:
        source_dir, _ = os.path.split(config_file)

    with open(config_file, 'rU') as f:
        url, problem_sets = parse_config_file(f)

    could_parse = create_tutorial_package(
        source_dir, destination_dir, url, problem_sets,
        ignore_invalid_tutorials=ignore_invalid_tutorials,
    )

    # output our results
    if verbose:
        for problem_set_name, tutorial_results in could_parse.items():
            print(problem_set_name)

            for tutorial_name, succeeded in tutorial_results.items():
                print('  ', '[x]' if succeeded else '[ ]', tutorial_name)

            print()

        successes = [succeeded for tutorial_results in could_parse.values()
                for succeeded in tutorial_results.values()]
        percent = int(sum(successes)/len(successes)*100)
        print('{}% of tutorials parsed successfully'.format(percent))


ProblemSetInfo = namedtuple('ProblemSetInfo', ['name', 'due', 'tutorials'])
TutorialInfo = namedtuple('TutorialInfo', ['name', 'directory', 'files'])


def parse_config_file(f):
    """
    Parse the given config file.

    Args:
      f (file): The configuration file to parse.

    Returns:
      A two-element tuple.
      The first element is the URL for the tutorial package, as a str.
      The second element is a list of the problem sets in the tutorial package,
      as ProblemSetInfo objects (NB: not as ProblemSet objects).

    Raises:
      TutorialCreationError: If the configuration file is invalid.

    """
    url = None
    problem_sets = []
    problem_set = None

    for line in filter(None, map(str.strip, f)):
        if line.startswith('[URL:'):
            _, url = line.strip('[]').split('URL:', 1)
        elif line.startswith('['):
            try:
                date, name = map(str.strip, line.strip('[]').split(' ', 1))
            except ValueError as e:
                raise TutorialCreationError(
                    'Invalid problem set definition: {}'.format(line)
                ) from e

            problem_set = ProblemSetInfo(name, date, [])
            problem_sets.append(problem_set)
        else:
            try:
                name, directory, *files = map(str.strip, line.split(':'))
            except ValueError as e:
                raise TutorialCreationError(
                    'Invalid tutorial definition: {}'.format(line)
                ) from e

            if problem_set is None:
                raise TutorialCreationError(
                    'Invalid configuration: tutorial definition encountered '
                    'before the first problem set definition!'
                )

            problem_set.tutorials.append(TutorialInfo(name, directory, files))

    if url is None:
        raise TutorialCreationError('Invalid configuration: no url specified!')

    if not problem_sets:
        raise TutorialCreationError('Invalid configuration: no problem sets!')

    for pset in problem_sets:
        if not pset.tutorials:
            raise TutorialCreationError(
                'Invalid configuration: problem set with name {} does not '
                'have any tutorials!'.format(pset.name)
            )

    return url, problem_sets


def write_package_tutorials_config(f, problem_sets):
    """
    Write the package tutorials configuration data to the given file.

    Args:
      f (file): The file to write the configuration information to.
      problem_sets ([ProblemSetInfo]): The problem sets to include.

    """
    lines = []
    pset_line = '[{0.due} {0.name}]'
    tutorial_line = '{0.name}:{0.directory}'

    for problem_set in problem_sets:
        lines.append(pset_line.format(problem_set))
        lines.append('')  # just to make it easier to read

        for tutorial in problem_set.tutorials:
            lines.append(tutorial_line.format(tutorial))

        lines.append('')  # just to make it easier to read

    f.write('\n'.join(lines) + '\n')


def write_package_config(f, url):
    """
    Write the package configuration data to the given file.

    Args:
      f (file): The file to write the configuration information to.
      url (str): The online URL for the package.

    """
    f.write('{}'.format(time.time()) + '\n')
    f.write(url + '\n')


def write_tutorial(tutorial, source_dir, destination_dir):
    """
    Write the given tutorial to the given directory.

    Args:
      tutorial (TutorialInfo): The tutorial to write.
      source_dir (str): The source dir of the problems database (in which the
          tutorial's .tut directory may be found).
      destination_dir (str): The destination directory for the resulting
          tutorial package.

    Raises:
      TutorialCreationError: If there is an issue with creating the tutorial,
          or if the tutorial itself is invalid.

    """
    src_dir = os.path.join(source_dir, tutorial.directory)

    # check that the package is valid
    if not os.path.exists(src_dir) or not os.path.isdir(src_dir):
        raise TutorialCreationError(
            'No valid tutorial package found at {}'.format(src_dir)
        )

    existing_files = os.listdir(src_dir)
    required_files = Tutorial.SUBMODULES + Tutorial.FILES

    for filename in required_files:
        if filename not in existing_files:
            raise TutorialCreationError(
                'Tutorial with name {} is missing one or more required files, '
                'including {}'.format(tutorial.name, filename)
            )

    for filename in tutorial.files:
        if filename not in existing_files:
            raise TutorialCreationError(
                'The tutorial {} specified that it included the file {}, '
                'but that file was not found'.format(tutorial.name, filename)
            )

    # create the output directory
    dest_dir = os.path.join(destination_dir, tutorial.directory)
    try:
        os.mkdir(dest_dir)
    except OSError as e:
        raise TutorialCreationError(
            'Could not create destination directory: {}'.format(dest_dir)
        ) from e

    # copy over the required tutorial files, along with any extra files
    for filename in chain(required_files, tutorial.files):
        src_path = os.path.join(src_dir, filename)
        dest_path = os.path.join(dest_dir, filename)

        shutil.copyfile(src_path, dest_path)




def create_zipfile(path, name):
    """
    Create a zip file from the contents of the given path.

    Args:
      path (str): The path to zip.
      name (str): The name of the resulting zip file (excluding the extension).

    """
    cwd = os.getcwd()
    os.chdir(path)

    all_files = glob.glob("*")

    with zipfile.ZipFile('{}.zip'.format(name), 'w') as zfile:
        for file in all_files:
            zfile.write(file)

    os.chdir(cwd)


def create_tutorial_package(source_dir, destination_dir, url, problem_sets,
        ignore_invalid_tutorials=False):
    """
    Create a tutorial package using the provided data.

    Args:
      source_dir (str): The location of the problems in the tutorial package.
      destination_dir (str): The directory to output the tutorial package to.
      url (str): The online URL for the tutorial package.
      problem_sets ([ProblemSetInfo]): The problem sets which make up the
          tutorial package.
      ignore_invalid_tutorials (bool, optional): Whether to ignore invalid
          tutorials, and proceed anyway.  If True, exceptions encountered when
          creating tutorials will be suppressed. Defaults to False.

    """
    # try to create the destination dir, which will fail if it already exists
    try:
        os.mkdir(destination_dir)
    except OSError as e:
        raise TutorialCreationError(
            'Destination directory exists: {}'.format(destination_dir)
        ) from e

    parent_dir, dir_name = os.path.split(destination_dir)

    # create configuration files
    package_tutorials_config = os.path.join(destination_dir, 'tutorials.txt')
    package_generic_config = os.path.join(destination_dir, 'config.txt')

    with open(package_tutorials_config, 'w') as f:
        write_package_tutorials_config(f, problem_sets)

    with open(package_generic_config, 'w') as f:
        write_package_config(f, url)

    # add the tutorial files
    # keep track of which ones succeeded and which failed (although the latter
    # will only be meaningful if we're ignoring invalid tutorials)
    # problem_set.name : {tutorial.name : successful}
    could_parse = OrderedDict()

    for problem_set in problem_sets:
        could_parse[problem_set.name] = OrderedDict()

        for tutorial in problem_set.tutorials:
            try:
                write_tutorial(tutorial, source_dir, destination_dir)
                could_parse[problem_set.name][tutorial.name] = True
            except TutorialCreationError as e:
                if not ignore_invalid_tutorials:
                    raise
                could_parse[problem_set.name][tutorial.name] = False

    # finally, write our tutorial hashes file
    update_hashes(parent_dir, destination_dir)

    # zip everything together
    create_zipfile(destination_dir, dir_name)

    return could_parse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'config_file',
        type=str,
        help='The path to the configuration file to use',
    )
    parser.add_argument(
        'destination_dir',
        type=str,
        help='The directory to output the tutorial package to',
    )
    parser.add_argument(
        'source_dir',
        type=str,
        help='The directory containing the tutorial problems',
        default=None,
        nargs='?',
    )
    parser.add_argument(
        '--ignore-invalid-tutorials',
        action='store_true',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
    )

    args = parser.parse_args()

    generate_tutorial_package(
        args.config_file,
        args.destination_dir,
        source_dir=args.source_dir,
        ignore_invalid_tutorials=args.ignore_invalid_tutorials,
        verbose=args.verbose,
    )

    return 0

if __name__ == '__main__':
    sys.exit(main())
