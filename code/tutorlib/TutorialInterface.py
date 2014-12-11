## A Python Tutorial System
## Copyright (C) 2009, 2010  Peter Robinson <pjr@itee.uq.edu.au>
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

# The main interface that deals both with the tutorial files and
# online material.

import os
import sys
import re
import traceback
import ast
import threading
import _thread
import time
import urllib.request
import urllib.parse
import urllib.error

from tutorlib.tester import TutorialTester, StudentTestCase

# a file for writing user code for exec'ing on
USER_CODE_FILE = 'user_code.py'


# An alarm for setting a timeout on user code execution.
class Alarm(threading.Thread):
    def __init__(self, secs):
        self.secs = secs
        self.do_interrupt = True
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(self.secs)
        if self.do_interrupt:
            _thread.interrupt_main()

    def stop_interrupt(self):
        self.do_interrupt = False


# An exception for any kind of error produced by the testing code as
# opposed to student code.

class TestError(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return repr(self._msg)


# Stop people making subclasses of TutorialInterface

class Final(type):
    def __new__(cls, name, bases, classdict):
        for b in bases:
            if isinstance(b, Final):
                raise TypeError("Cannot make a subclass of '{0}'"
                                .format(b.__name__))
        return type.__new__(cls, name, bases, dict(classdict))


class TutorialInterface(metaclass=Final):
    def __init__(self, master, parent, output, enc=True):
        self.url = None
        self.session_key = None
        self.master = master
        self.next_hint_index = 0
        self.editor = None
        self.output = output
        self.user = None
        self.enc = enc
        self.tutorial = None
        self.solved = False

    def set_url(self, url):
        self.url = url

    def set_editor(self, editor):
        self.editor = editor

    def _send_data(self, form_dict):
        if self.url:
            try:
                URL = self.url.strip()
                data = urllib.parse.urlencode(form_dict)
                response = urllib.request.urlopen(URL, data, proxies={})
                text = response.read().strip()
                #print text  # debugging
                if text.startswith('mypytutor>>>'):
                    return text[12:]
                else:
                    return '_send_data Exception: Invalid response'
            except Exception as e:
                return '_send_data Exception: '+str(e)

    def load_data(self, filename, problem_name):
        self.solved = False
        self.num_checks = 0
        self.next_hint_index = 0

        self.tutorial = Tutorial(problem_name, filename)

    def logged_on(self):
        return self.session_key is not None

    def get_tut_zipfile(self):
        values = {'action': 'get_tut_zip_file'}
        result = self._send_data(values)
        #print result
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "tutzip.zip")
            return "tutzip.zip"
        except Exception as e:
            print(str(e))
            return None

    def get_mpt27(self):
        values = {'action': 'get_mpt27'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt27.zip")
            return "mpt27.zip"
        except:
            return None

    def get_mpt26(self):
        values = {'action': 'get_mpt26'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt26.zip")
            return "mpt26.zip"
        except:
            return None

    def login(self, user, passwd):
        values = {'action': 'login',
                  'username': user,
                  'password': passwd}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return False
        if result is None:
            return False
        if result.startswith('Error'):
            return False
        else:
            parts = result.split()
            self.session_key = parts[1].strip()
            self.timestamp = float(parts[0])
            self.user = user
            return True

    def get_version(self):
        values = {'action': 'get_version'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        else:
            return result

    def logout(self):
        if self.user is None:
            return
        values = {'action': 'logout',
                  'username': self.user,
                  'session_key': self.session_key,
                  }
        result = self._send_data(values)
        self.user = None
        self.session_key = None

    def change_password(self, passwd0, passwd1):
        if passwd0 == '':
            passwd0 = '-'
        values = {'action': 'change_password',
                  'username': self.user,
                  'session_key': self.session_key,
                  'password': passwd0,
                  'password1': passwd1,
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return False
        if result is None:
            return False
        if result.startswith('Error'):
            return False
        else:
            return True

    def upload_answer(self, code):
        result = None
        if self.tutorial is not None:
            values = {'action': 'upload',
                      'username': self.user,
                      'session_key': self.session_key,
                      'problem_name': self.tutorial.name,
                      'code': code,
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return False

        if result is None:
            return False
        return result.startswith('OK')

    def download_answer(self):
        result = None
        if self.tutorial is not None:
            values = {'action': 'download',
                      'username': self.user,
                      'session_key': self.session_key,
                      'problem_name': self.tutorial.name,
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return None
        return result

    def submit_answer(self, code):
        self.run_tests(code)
        result = None
        if self.tutorial is not None:
            if self.is_solved():
                tut_id = self.data.get('ID')  # TODO: work out what ID is and then replace this
                values = {'action': 'submit',
                          'username': self.user,
                          'session_key': self.session_key,
                          'tut_id': tut_id,
                          'tut_id_crypt': simple_hash(tut_id + self.user),
                          'tut_check_num': self.num_checks,
                          'code': code,
                          }
                result = self._send_data(values)
                if '_send_data Exception' in result:
                    print("You don't appear to be connected.", file=sys.stderr)
                    return None
            else:
                result = 'Error: You can only submit when your answer is correct.'
        return result

    def show_submit(self):
        result = None
        values = {'action': 'show',
                  'username': self.user,
                  'session_key': self.session_key,
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print(result[10:], file=sys.stderr)
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        return result

    def get_next_hint(self):
        try:
            hint = self.tutorial.hints[self.next_hint_index]
            self.next_hint_index += 1
            return "<p>\n<b>Hint "+str(self.next_hint_index)+': </b>'+hint
        except:
            return None

    def reset_editor(self, answer_file):
        self.editor.reset(answer_file, self.tutorial.preload_code_text)

    def get_preloaded(self):
        return self.tutorial.preload_code_text

    def get_hints(self):
        return self.tutorial.hints

    def get_text(self):
        return self.tutorial.description

    def set_user_text(self, text):
        self.user_text = text

    def set_fail(self):
        self.correct_sofar = False

    def is_solved(self):
        return self.solved

    def print_error(self, text):
        print(text, file=sys.stderr)
        self.set_fail()

    def print_exception(self, e):
        self.print_exception_info(e)
        print('%s: %s\nTry Googling  the error type for help.' %
              (type(e).__name__, str(e)), file=sys.stderr)
        self.set_fail()

    def print_exception_info(self, e):
        line = traceback.extract_tb(sys.exc_info()[-1])[-1][1]
        traceinfo = traceback.extract_tb(sys.exc_info()[-1])[-1]
        if traceinfo[0] == USER_CODE_FILE:
            print("line %d, in %s" % (traceinfo[1], traceinfo[2]),
                  file=sys.stderr)
            print(self.user_text.split('\n')[line-1].strip(), file=sys.stderr)
            self.editor.error_line(line)

    def print_warning(self, text):
        print(text, file=sys.stderr)

    def correct(self):
        self.solved = True
        if self.url:
            print("Correct - press F6 to submit")
        else:
            print("Correct")

    # Run tests on the user code.

    def run_tests(self, text):
        alarm = Alarm(self.tutorial.timeout)
        alarm.setDaemon(True)
        alarm.start()

        try:
            return self._runtests(text)
        except KeyboardInterrupt as e:
            print('Timeout - possible infinite loop', file=sys.stderr)
            return None, None
        finally:
            alarm.stop_interrupt()

    def _runtests(self, text):
        self.num_checks += 1

        # load the support file (giving students access to functions, variables
        # etc which they may need for their solution)
        gbls, lcls = self.tutorial.exec_submodule(Tutorial.SUPPORT_MODULE)

        # load and run the tests
        tester = TutorialTester(self.tutorial.test_classes, gbls, lcls)
        tester.run(text, self.tutorial.student_function_name)

        # perform the static analysis
        analyser = self.tutorial.analyser
        analyser.analyse(text)

        ## TODO: run student code, highlight SyntaxError, NameError etc
        ## TODO: should probably do this first

        return tester, analyser


class Tutorial():
    ANALYSIS_MODULE = 'analysis.py'
    CONFIG_MODULE = 'config.py'
    PRELOAD_MODULE = 'preload.py'
    SUPPORT_MODULE = 'support.py'
    TESTS_MODULE = 'tests.py'
    SUBMODULES = [
        ANALYSIS_MODULE,
        CONFIG_MODULE,
        PRELOAD_MODULE,
        SUPPORT_MODULE,
        TESTS_MODULE,
    ]

    DESCRIPTION_FILE = 'description.html'
    FILES = [
        DESCRIPTION_FILE,
    ]

    TESTS_VARIABLE_NAME = 'TEST_CLASSES'
    ANALYSIS_VARIABLE_NAME = 'ANALYSER'

    def __init__(self, name, path):
        self.name = name
        self.path = path

        # load the description
        self._assert_valid_file(Tutorial.DESCRIPTION_FILE)
        description_path = os.path.join(self.path, Tutorial.DESCRIPTION_FILE)
        with open(description_path, 'rU') as f:
            self.description = f.read()

        # parse the config file
        _, config_lcls = self.exec_submodule(Tutorial.CONFIG_MODULE)

        self.short_description = config_lcls.get('SHORT_DESCRIPTION', '')
        self.hints = config_lcls.get('HINTS', [])
        self.student_function_name = config_lcls.get('STUDENT_FUNCTION')
        self.timeout = config_lcls.get('TIMEOUT', 1)

        # initial values for lazy properties
        self._preload_code_text = None

    def _assert_valid_file(self, file_name):
        assert file_name in os.listdir(self.path), \
            'Invalid .tut package: missing {}'.format(file_name)

    def _assert_valid_module(self, module_name):
        assert module_name in Tutorial.SUBMODULES, \
            'Unknown submodule: {}'.format(module_name)

        self._assert_valid_file(module_name)

    def exec_submodule(self, module_name, gbls=None, lcls=None):
        self._assert_valid_module(module_name)
        path = os.path.join(self.path, module_name)

        return exec_module(path, gbls=gbls, lcls=lcls)

    def read_submodule(self, module_name):
        self._assert_valid_module(module_name)
        path = os.path.join(self.path, module_name)

        with open(path, 'rU') as f:
            return f.read()

    # TODO: it's debateable whether these should be properties, as their state
    # TODO: will not persit across calls (due to the re-exec of the module)
    @property
    def test_classes(self):
        # the test module requires access to StudentTestCase, as that's what
        # it will have inherited from
        # because we imported that here, we can just pass in our globals
        # we also make use of it here, as a noop, to keep PEP8 happy and
        # prevent later coders from removing the 'unneeded' import
        # that's the only reason we use a global here
        global StudentTestCase
        StudentTestCase = StudentTestCase

        _, test_lcls = self.exec_submodule(Tutorial.TESTS_MODULE, globals())

        assert Tutorial.TESTS_VARIABLE_NAME in test_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.TESTS_MODULE, Tutorial.TESTS_VARIABLE_NAME
            )

        return test_lcls[Tutorial.TESTS_VARIABLE_NAME]

    @property
    def analyser(self):
        _, analysis_lcls = self.exec_submodule(Tutorial.ANALYSIS_MODULE)

        assert Tutorial.ANALYSIS_VARIABLE_NAME in analysis_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.ANALYSIS_MODULE, Tutorial.ANALYSIS_VARIABLE_NAME
            )

        return analysis_lcls[Tutorial.ANALYSIS_VARIABLE_NAME]

    @property
    def preload_code_text(self):
        if self._preload_code_text is None:
            self._preload_code_text = self.read_submodule(
                Tutorial.PRELOAD_MODULE
            )

        return self._preload_code_text

## Parsing and encrypting/decrypting for tutorial problem files

## The problem files use block headers followed by text.
## The block headers have the form #{header name}#
## At the top-level the 'special' headers are:
##      #{Text}#  - followed by the HTML text for the problem
##                    exactly one such block
##      #{Hint}#  - followed by a hint text (HTML) -
##                    0 or more such blocks
##      #{TestCode}# - followed by the test code blocks (Python code)
##                    exactly one such block - must be last block
##
## Any other headers are possible and will be added to the dictionary
## but unlike Hints the dictionary will contain only the last block
## with the given header.


def pos2linenum(string, pos):
    substring = string[:pos+1]
    num = substring.count('\n')
    return num+1


class ParseError(Exception):
    def __init__(self, pos):
        self.pos = pos

    def __str__(self):
        return repr(self.pos)


## The parser for the code blocks
## The block headers are:
## #{preload}# - code that is loaded into the users code edit window
##                   0 or 1 such blocks before the #{test}# blocks
## #{global}# - code that is used by all test code
##                   0 or 1 such blocks before the #{test}# blocks
## #{timeout = secs}# - max time for all tests (default 1 sec)
## #{ID = IDstring}# - ID of problem
## #{test}# - the header for a test - tests include the following headers:
##        #{start}# - code that is run before the user code but not accessable
##                    to user code
##                      0 or 1 such blocks
##        #{init}# - initialization run before user code - user has access to
##                   the results of evalating this code
##                      0 or 1 such blocks
##        #{code}# - the code that is run after the user code that carries out
##                   the tests
##                      exactly one such block



def extract_test_config(text):
    test_dict = {'repeats': 1}
    argpairs = [arg.split('=') for arg in text.split(',') if arg.strip()]
    for argpair in argpairs:
        if len(argpair) != 2:
            print("Invalid syntax for test arguments.", file=sys.stderr)
            return None
        arg1 = argpair[0].strip()
        arg2 = argpair[1].strip()
        if arg1 != 'repeats':
            print("Invalid syntax for test arguments '%s'." % arg1, file=sys.stderr)
            return None
        try:
            argnum = int(arg2)
        except:
            print("Invalid syntax for test arguments - int required - got '%s'." % arg2, file=sys.stderr)
            return None
        test_dict[arg1] = argnum
    return test_dict


# The encryption/decryption algorithm uses a simple symmetric
# single-rotor encryption for the 'printable' characters - i.e.
# those between ' ' and '~'.
# All other characters are not encrypted.

# since the hash function seems to be different on different
# machines here is a simple string hash that hashes up to the first 40
# chars
def simple_hash(text):
    hash_value = 5381
    num = 0
    for c in text:
        if num > 40:
            break
        num += 1
        hash_value = 0x00ffffff & ((hash_value << 5) + hash_value + ord(c))
    return hash_value


def exec_module(path, gbls=None, lcls=None):
    if gbls is None:
        gbls = {}
    if lcls is None:
        lcls = {}

    with open(path) as f:
        exec(compile(f.read(), path, 'exec'), gbls, lcls)

    return gbls, lcls
