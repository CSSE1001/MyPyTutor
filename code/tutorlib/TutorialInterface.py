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

import ast
import os
import sys
import traceback
import threading
import _thread
import time
import urllib.request
import urllib.parse
import urllib.error

from tutorlib.analyser import CodeAnalyser, TutorialNodeVisitor
from tutorlib.online import SessionManager, RequestError, SERVER
from tutorlib.tester import TutorialTester, StudentTestCase

# keep PEP8 happy
# these imports are indirectly used in Tutorial, and must not be removed
ast = ast
CodeAnalyser = CodeAnalyser
TutorialNodeVisitor = TutorialNodeVisitor
StudentTestCase = StudentTestCase

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


class TutorialInterface():
    def __init__(self, master, parent, enc=True):
        self.url = None
        self.session_key = None
        self.master = master
        self.next_hint_index = 0
        self.editor = None
        self.user = None
        self.enc = enc
        self.tutorial = None
        self.solved = False
        self.session_manager = SessionManager(SERVER,
                # TODO replace this with a method which sets the "Logged in as X" label in the application
                # See the tutorlib.TutorialApp.Toolbar.set_login/unset_login methods.
                lambda: print("You are:", self.session_manager.user_info()))

    def set_url(self, url):
        self.url = url

    def set_editor(self, editor):
        self.editor = editor

    def load_data(self, filename, problem_name):
        self.solved = False
        self.num_checks = 0
        self.next_hint_index = 0

        self.tutorial = Tutorial(problem_name, filename)

    # TODO refactor this method away?
    def logged_on(self):
        return self.session_manager.is_logged_on()

    def get_tut_zipfile(self):
        values = {'action': 'get_tut_zip_file'}
        try:
            result = self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return

        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "tutzip.zip")
            return "tutzip.zip"
        except Exception as e:
            print(str(e))
            return None

    def get_mpt34(self):
        values = {'action': 'get_mpt34'}
        try:
            result = self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return

        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt34.zip")
            return "mpt34.zip"
        except:
            return None

    def get_version(self):
        values = {'action': 'get_version'}
        try:
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)

    def change_password(self, passwd0, passwd1):
        raise NotImplementedError("TODO: remove")

    def upload_answer(self, code):
        if self.tutorial is None:
            return False

        try:
            values = {
                      'action': 'upload',
                      'problem_name': self.tutorial.name,
                      'code': code,
                     }
            result = self.session_manager.post(values)
            return result.startswith('OK')
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return False

    def download_answer(self):
        if self.tutorial is None:
            return False

        try:
            values = {
                      'action': 'download',
                      'problem_name': self.tutorial.name,
                     }
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return False

    def submit_answer(self, code):
        self.run_tests(code)
        if self.tutorial is None:
            return None

        if not self.is_solved():
            return 'Error: You can only submit when your answer is correct.'

        try:
            tut_id = self.data.get('ID')  # TODO: work out what ID is and then replace this
            values = {
                      'action': 'submit',
                      'tut_id': tut_id,
                      'tut_id_crypt': simple_hash(tut_id + self.user),
                      'tut_check_num': self.num_checks,
                      'code': code,
                     }
            return self.session_manager.post(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return None

    def show_submit(self):
        values = {'action': 'show'}
        try:
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return None

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

    def get_short_description(self):
        return self.tutorial.short_description

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

        # perform the static analysis
        # this should only take place if there are no errors in parsing the
        # student's code (as those would interfere with ast)
        # we therefore collect those first, and only proceed if there were
        # no such errors
        # note that we may have an error with no line information (this will be
        # the case with a NameError, for example)
        analyser = self.tutorial.analyser
        tester = TutorialTester(self.tutorial.test_classes, gbls, lcls)

        error_line = analyser.check_for_errors(text)
        if error_line is not None:
            self.editor.error_line(error_line)

        if not analyser.errors:
            # there were no errors, so it's safe to perform the analysis
            analyser.analyse(text)

            # we can likewise run the tests
            tester.run(text, self.tutorial.student_function_name)

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
        _, test_lcls = self.exec_submodule(Tutorial.TESTS_MODULE, globals())

        assert Tutorial.TESTS_VARIABLE_NAME in test_lcls, \
            'Invalid .tut package: {} has no member {}'.format(
                Tutorial.TESTS_MODULE, Tutorial.TESTS_VARIABLE_NAME
            )

        return test_lcls[Tutorial.TESTS_VARIABLE_NAME]

    @property
    def analyser(self):
        # the analysis module requires access to CodeAnalyser, as that's what
        # it must inherit from
        # because we imported that class in this file, we can just pass in
        # our globals() dict
        _, analysis_lcls = self.exec_submodule(Tutorial.ANALYSIS_MODULE,
                                               globals())

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
    '''
    Execute the module at the given path using the provided globals and locals

    NB: Here be massive, fire-breathing dragons.
        The main reason for this is that the module code itself may rely on
        references within its own locals/globals dictionaries.
        It may therefore be an error to make use of specific references from
        these dictionaries without also bringing other, related references
        into the calling context.

        A simple example helps illustrate this.
        Take the following module definition:
          # module.py
          class A():
              pass
          class B():
              def f(self):
                  a = A()  ## -- mark

        When executed, that module will define A and B in locals.
        If we extract B alone, ie B = locals['B'], and then run it in a context
        where A is not defined, then we will get a NameError on the line
        marked above.

        To avoid this, we need to also extract A into a scope that B can see.
    '''
    if gbls is None:
        gbls = {}
    if lcls is None:
        lcls = {}

    with open(path) as f:
        exec(compile(f.read(), path, 'exec'), gbls, lcls)

    return gbls, lcls
