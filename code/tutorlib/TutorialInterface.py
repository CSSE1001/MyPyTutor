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
import compiler
import threading
import _thread
import time
import urllib.request, urllib.parse, urllib.error


# a file for writing user code for exec'ing on
USER_CODE_FILE = 'user_code.py'

# An alarm for setting a timeout on user code execution.

class Alarm(threading.Thread):

    def __init__( self, secs):
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

# In order to make it difficult to determine what this code does
# we make the init check if this object is created as a member of
# this class or as a member of an inherited class.
        
class TutorialInterface:
    
    def __init__(self, master, parent, output, enc=True):
        self.bad = \
            str(self.__class__) != \
            'tutorlib.TutorialInterface.TutorialInterface'
        self.url = None
        self.session_key = None
        self.master = master
        self.data = {}
        self.next_hint_index = 0
        self.editor = None
        self.output = output
        self.user = None
        self.enc = enc
        self.solved = False
        if self.bad:
            self.trans = None
            self.parser = None
        else:
            self.trans = Trans(77213)       #  a 'secret key'
            self.parser = TutParser(self.trans)

    def set_url(self, url):
        if self.bad:
            return None
        self.url = url

    def set_editor(self, editor):
        self.editor = editor

    def _send_data(self, form_dict):
        if self.bad:
            return None
        if self.url:
            try: 
                # The URL is encrypted to make it hard to 'spoof' the
                # CGI script so as to gain information.
                URL = self.trans.trans(self.url, 'tutor key').strip()
                data = urllib.parse.urlencode(form_dict)
                response = urllib.request.urlopen(URL, data, proxies = {})
                text = response.read().strip()
                #print text  # debugging
                if text.startswith('mypytutor>>>'):
                    return text[12:]
                else:
                    return '_send_data Exception: Invalid response'
            except Exception as e:
                return '_send_data Exception: '+str(e)

    def _parse_text(self, text):
        self.data = self.parser.parse(text, True, self.enc)
        if not self.data:
            print('Tutorial file has incorrect format', file=sys.stderr)

    def load_data(self, file, problem_name):
        if self.bad:
            return None
        self.solved = False
        self.num_checks = 0
        self.data = {}
        self.next_hint_index = 0
        try:
            f = open(file, 'U')
            text = f.read()
            self._parse_text(text)
            f.close()
        except:
            print('Cannot open '+file, file=sys.stderr)
        self.problem_name = problem_name

    def logged_on(self):
        return self.session_key != None

    def get_tut_zipfile(self):
        values = {'action':'get_tut_zip_file'}
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
        values = {'action':'get_mpt27'}
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
        values = {'action':'get_mpt26'}
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
        if self.bad:
            return None
        values = {'action':'login',
                  'username' : user,
                  'password' : passwd}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return False
        if result == None:
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
        values = {'action':'get_version'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        else:
            return result

    def logout(self):
        if self.bad:
            return
        if self.user is None:
            return
        values = {'action':'logout',
                  'username':self.user,
                  'session_key':self.session_key,
                  }
        result = self._send_data(values)
        self.user = None
        self.session_key = None

    def change_password(self, passwd0, passwd1):
        if self.bad:
            return None
        if passwd0 == '':
            passwd0 = '-'
        values = {'action':'change_password',
                  'username':self.user,
                  'session_key':self.session_key,
                  'password' : passwd0,
                  'password1': passwd1
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return False
        if result == None:
            return False
        if result.startswith('Error'):
            return False
        else:
            return True

    def upload_answer(self, code):
        if self.bad:
            return None
        result = None
        if self.data:
            values = {'action':'upload',
                      'username':self.user,
                      'session_key':self.session_key,
                      'problem_name': self.problem_name,
                      'code':code
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return False

        if result == None:
            return False
        return result.startswith('OK')
 
    def download_answer(self):
        if self.bad:
            return None
        result = None
        if self.data:
            values = {'action':'download',
                      'username':self.user,
                      'session_key':self.session_key,
                      'problem_name': self.problem_name
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return None
        return result

    def submit_answer(self, code):
        if self.bad:
            return None
        self.run_tests(code)
        result = None
        if self.data:
            if self.is_solved():
                tut_id = self.data.get('ID')
                values = {'action':'submit',
                          'username':self.user,
                          'session_key':self.session_key,
                          'tut_id': tut_id,
                          'tut_id_crypt': self.trans._sh(tut_id + self.user),
                          'tut_check_num': self.num_checks,
                          'code':code
                          }
                result = self._send_data(values)
                if '_send_data Exception' in result:
                    print("You don't appear to be connected.", file=sys.stderr)
                    return None
            else:
                result = 'Error: You can only submit when your answer is correct.'
        return result

    def show_submit(self):
        if self.bad:
            return None
        result = None
        values = {'action':'show',
                  'username':self.user,
                  'session_key':self.session_key,
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print(result[10:], file=sys.stderr)
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        return result

    def get_next_hint(self):
        try:
            hint = self.data['Hint'][self.next_hint_index]
            self.next_hint_index += 1
            return "<p>\n<b>Hint "+str(self.next_hint_index)+': </b>'+hint
        except:
            return None

    def reset_editor(self, answer_file):
        if self.bad:
            return None
        self.editor.reset(answer_file, self.data.get('Preloaded'))

    def get_preloaded(self):
        if self.bad:
            return None
        return self.data.get('Preloaded')

    def get_hints(self):
        return self.data['Hint']

    def get_text(self):
        return self.data.get('Text')

    def set_user_text(self, text):
        if self.bad:
            return None
        self.user_text = text

    def set_fail(self):
        self.correct_sofar = False

    def is_solved(self):
        if self.bad:
            return None
        return self.solved

    def print_error(self, text):
        print(text, file=sys.stderr)
        self.set_fail()

    def print_exception(self, e):
        self.print_exception_info(e)
        print('%s: %s\nTry Googling  the error type for help.' %  (type(e).__name__, str(e)), file=sys.stderr)
        self.set_fail()


    def print_exception_info(self, e):
        line = traceback.extract_tb(sys.exc_info()[-1])[-1][1]
        traceinfo = traceback.extract_tb(sys.exc_info()[-1])[-1]
        if traceinfo[0] == USER_CODE_FILE:
            print("line %d, in %s" % (traceinfo[1], traceinfo[2]), file=sys.stderr)
            print(self.user_text.split('\n')[line-1].strip(), file=sys.stderr)
            self.editor.error_line(line)

    def print_warning(self, text):
        print(text, file=sys.stderr)

    def correct(self):
        if self.bad:
            return None
        self.solved = True
        if self.url:
            print("Correct - press F6 to submit")
        else:
            print("Correct")

    # Run tests on the user code.

    def run_tests(self, text):
        if self.bad:
            return None
        self.user_text = text
        # save user code to a file ready for exec
        fp = open(USER_CODE_FILE, 'w')
        fp.write(text)
        fp.close()
        alarm = Alarm(self.data.get('timeout'))
        alarm.setDaemon(True)
        alarm.start()
        try:
            self._runtests()
            alarm.stop_interrupt()
        except KeyboardInterrupt as e:
            alarm.stop_interrupt()
            print('Timeout - possible infinite loop', file=sys.stderr)
        os.remove(USER_CODE_FILE)

    def _runtests(self):
        self.num_checks += 1
        if self.get_text():
            self.output.clear_text()
            try:
                ## give access to the problem test code to:
                ## user_text -   the contents of the code edit window
                ##               including preload
                ## print_error - a simple wrapper for printing to stderr
                ##               that causes the tests to be exited
                ## print_exception - takes an exception e and prints
                ##               str(e) to stderr with a hint about Googling
                ##               for help. Causes the tests to be exited.
                ## print_warning - like print_error but does not stop tests
                ## correct - set solved and print 'Correct'
                ## master - the 'master' of the app - for GUI problems
                global_env = {'user_text': self.user_text, 
                              'print_warning':self.print_warning, 
                              'print_error':self.print_error,
                              'print_exception':self.print_exception,
                              'correct':self.correct,
                              'master':self.master}
                ## update the global env with the execution of the global code
                try:
                    exec(self.data.get('GlobalCode', ''), global_env)
                except Exception as e:
                    raise TestError(e)
                tests = self.data.get('TestCode')
                self.correct_sofar = True

                for test in tests:
                    for _ in range(test['repeats']):
                        if not self.correct_sofar:
                            return
                        # test_globals is used to test user code - it
                        # is initialized with global_env that contains
                        # the results of exec global code
                        test_globals = global_env.copy()
                        # first exec setup code in the test_globals env
                        # this env stores both globals and locals
                        try:
                            exec(test.get('start', ''), test_globals)
                        except Exception as e:
                            raise TestError(e)
                        save_globals = test_globals.copy()
                        locs = {}
                        # now exec the initialization code using an
                        # empty local env - updated by the code - this
                        # sets up values that is accessed by user code
                        try:
                            exec(test.get('init', ''), test_globals,locs)
                        except Exception as e:
                            raise TestError(str(e))
                        # now exec the user code where locs is used as 
                        # both global and local env
                        # with open(USER_CODE_FILE) as fp:
                        #      exec fp in locs
                        exec(compile(open(USER_CODE_FILE).read(), USER_CODE_FILE, 'exec'), locs)
                        #print locs
                        # now test the results of the user code - update 
                        # test_globals to include locs
                        test_globals.update(locs)
                        # just in case the user defines one of the things in global_env
                        # or things created by the start code
                        test_globals.update(save_globals)
                        try:
                            # we manage errors (such as undefined vars)
                            # differently for the test code than from
                            # user code
                            exec(test.get('code', ''), test_globals)
                        except NameError as e:
                            raise NameError
                        except Exception as e:
                            raise TestError(str(e))
            except SyntaxError as e:
                ## For a syntax error in the user code highlight the line
                ## of user code with the problem
                self.output.add_text('Syntax Error: %s\n' % e.msg, "red")
                self.editor.error_line(e.lineno)
            except NameError as e:
                ## For the remaining exceptions extract the line number
                ## from the traceback stack and highlight line of code
                self.print_exception_info(e)
                self.output.add_text('Name Error: ' + str(e), "red")
            except TypeError as e:
                self.print_exception_info(e)
                self.output.add_text('Type Error: ' + str(e), "red")
            except TestError as e:
                if self.enc:
                    self.output.add_text('Test Error: please report error to maintainer', "red")
                else:
                    self.output.add_text('Test Error: ' + str(e), "red")
            except Exception as e:
                self.print_exception_info(e)
                print('%s: %s\nTry Googling  the error type for help.' %  (type(e).__name__, str(e)), file=sys.stderr)




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
 



_tut_retable = (
    (   # text block
    re.compile(r"""
    \#{[Tt]ext}\#\s*
    """, re.VERBOSE),
    lambda x: ('header', 'Text')
    ),
    (   # code block
    re.compile(r"""
    \#{[Tt]est[Cc]ode}\#\s*
    """, re.VERBOSE),
    lambda x: ('header', 'TestCode')
    ),
    (   # hint block
    re.compile(r"""
    \#{[Hh]int}\#\s*
    """, re.VERBOSE),
    lambda x: ('header', 'Hint')
    ),
    (   # other tags
    re.compile(r"""
    \#{[^}]*}\#\s
    """, re.VERBOSE | re.DOTALL),
    lambda x: ('header', x[2:-3].lower())
    ),

    (   # catchall
    re.compile(r"""
    [^#]*(?!\#{)(\#[^#]*(?!\#{))*\s*
    """, re.VERBOSE | re.DOTALL),
    lambda x: ('body', x)
    )
)

def pos2linenum(string, pos):
    substring = string[:pos+1]
    num = substring.count('\n')
    return num+1

class ParseError(Exception):
    
    def __init__(self, pos):
        self.pos = pos

    def __str__(self):
        return repr(self.pos)

## Parse the top-level of the input

class TutParser:
    def __init__(self, trans):
        self.string = ''
        self.pos = 0
        self.code_parser = CodeParser()
        self.trans = trans

    def _next_token(self):
        found = False
        for (regexp, fun) in _tut_retable:
            m = regexp.match(self.string, self.pos)
            if m:
                found = True
                self.curr_token = fun(m.group())
                self.pos = m.end()
                break
        return found

    def _parse_it(self, parse_code, enc):
        while True:
            tok_type, tok = self.curr_token
            if tok_type == 'header':
                header = tok
                if header == 'TestCode':
                    ## We are in the test code block
                    ## first decrypt if required
                    code = self.string[self.pos:]
                    if enc:
                        code = self.trans.trans(code, self.data['Text'])
                    try:
                        ## test to see if legal Python code
                        compiler.parse(code)
                    except SyntaxError as e:
                        print(str(e), file=sys.stderr)
                        return False
                    except Exception as e:
                        print(str(e), file=sys.stderr)
                        return False
                    if parse_code:
                        ## if the code  is to be parsed into blocks
                        ## then use the code parser
                        ## preload is the code to be loaded
                        ## into the users code edit window
                        ## global_code is code that is global to
                        ## all tests but not accessable to user code
                        ## timeout is the max total time for all the tests
                        ## tests is a list of test dictionaries
                        ## each storing the test blocks
                        preload, global_code, timeout, ID, tests = \
                            self.code_parser.parse(code)
                        self.data['timeout'] = timeout
                        if ID:
                            self.data['ID'] = ID
                        if preload:
                            self.data['Preloaded'] = preload
                        if global_code:
                            self.data['GlobalCode'] = global_code
                        if tests:
                            self.data['TestCode'] = tests
                        else:
                            print("No tests", file=sys.stderr)
                            return False
                    else:
                        self.data['TestCode'] = code
                    break
                if not self._next_token():
                    print("Nothing after header", file=sys.stderr)
                    raise ParseError(pos2linenum(self.string, self.pos))
                tok_type, tok = self.curr_token
                if tok_type != 'body':
                    raise ParseError(pos2linenum(self.string, self.pos))
                if header == 'Hint':
                    self.data['Hint'].append(tok.strip())
                else:
                    self.data[header] = tok.strip()
            else:
                print("Expecting header", file=sys.stderr)
                raise ParseError(pos2linenum(self.string, self.pos))
            if not self._next_token():
                break
        return True

    def parse(self, string, parse_code, enc = True):
        self.data = {}
        self.string = string
        self.pos = 0
        if not self._next_token():
            print("Empty string", file=sys.stderr)
            return None
        while self.curr_token[0] != 'header':
            if not self._next_token():
                print("No headers found", file=sys.stderr)
                return None
        ## data is the dictionary that stores the top-level blocks
        ## hints are stored in a list
        self.data = {'Hint':[]}
        try:
            if self._parse_it(parse_code, enc):
                return self.data
            else:
                return None
        except ParseError as e:
            print("Parse error in text at line", e.pos, file=sys.stderr)
            return None
        except Exception as e:
            print(str(e))

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

class CodeParser:
    def __init__(self):
        self.string = ''
        self.pos = 0
        self.preload = None
        self.global_code = None
        self.timeout = 1
        self.ID = None

    def _next_token(self):
        found = False
        for (regexp, fun) in _tut_retable:
            m = regexp.match(self.string, self.pos)
            if m:
                found = True
                self.curr_token = fun(m.group())
                self.pos = m.end()
                if self.curr_token[1] == '':
                    return False
                break
        return found

    def parse(self, string):
        tests = []
        try:
            self.string = string
            self.pos = 0
            tokens = []
            self.preload = None
            self.global_code = None
            self.timeout = 1
            self.ID = None
            while self._next_token():
                tokens.append(self.curr_token)
            while True:
                first_token = tokens.pop(0)
                if first_token[0] != 'header':
                    print("Must start with header", file=sys.stderr)
                    return (None,None,None,None,None)
                if first_token[1] in ['preload','global']:
                    next_token = tokens.pop(0)
                    if next_token[0] != 'body':
                        print("Header must be followed by body", file=sys.stderr)
                        return (None,None,None,None,None)
                    if first_token[1] == 'preload':
                        self.preload = next_token[1]
                    else:
                        self.global_code = next_token[1]
                elif 'id' in first_token[1]:
                    args = first_token[1].split('=')
                    if len(args) != 2 or 'id' != args[0].strip():
                        print("Invalid syntax '%s'" %\
                            first_token[1], file=sys.stderr)
                        return (None,None,None,None,None)
                    else:
                        self.ID = args[1].strip()
                elif 'timeout' in first_token[1]:
                    args = first_token[1].split('=')
                    if len(args) != 2 or 'timeout' != args[0].strip():
                        print("Invalid syntax '%s'" %\
                            first_token[1], file=sys.stderr)
                        return (None,None,None,None,None)
                    else:
                        try:
                            timeout = int(args[1].strip())
                        except:
                            print("Invalid syntax '%s'" %\
                                first_token[1], file=sys.stderr)
                            return (None,None,None,None,None)
                        self.timeout = timeout
                elif 'test' not in first_token[1]:
                    print("Must be 'test' header", file=sys.stderr)
                    return (None,None,None,None,None)
                else:
                    break
            # now first_token == 'test ...'
            test_dict = extract_test_config(first_token[1][4:])
            if not test_dict:
                return (None,None,None,None,None)
            at_test = True
            while tokens:
                next_token = tokens.pop(0)
                if at_test and next_token[0] == 'body' \
                        and not next_token[1].strip():
                    continue
                
                if next_token[0] != 'header':
                    print("Must be header", file=sys.stderr)
                    return (None,None,None,None,None)
                header = next_token[1]

                if 'test' in header:
                    at_test = True
                    if test_dict:
                        tests.append(test_dict)
                        test_dict = extract_test_config(header[4:])
                        if not test_dict:
                            return (None,None,None,None,None)
                        continue
                    else:
                        print("test must contain data", file=sys.stderr)
                        return (None,None,None,None,None)

                at_test = False
                if header not in ['start', 'init', 'code']:
                    print("unknown header: "+header, file=sys.stderr)
                    return (None,None,None,None,None)
                next_token = tokens.pop(0)
                if next_token[0] != 'body':
                    print("Header must be followed by body", file=sys.stderr)
                    return (None,None,None,None,None)
                test_dict[header] = next_token[1]
            tests.append(test_dict)
        except ParseError as e:
            print("Parse error in code", file=sys.stderr)
            return (None,None,None,None,None)
        return (self.preload,self.global_code,self.timeout,self.ID,tests)


def extract_test_config(text):
    test_dict = {'repeats':1}
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

# The  encryption/decryption algorithm uses a simple symmetric 
# single-rotor encryption for the 'printable' characters - i.e. 
# those between ' ' and '~'.
# All other characters are not encrypted.

import random

class Trans:
    def __init__(self, x=0):
        # Test the 'secret key' 
        if x % 5381 == 1879 and x / 5381 == 14:
            n0 = 2
            n1 = 7
            n2 = n1 - n0
            self.n3 = n0**n2
            self.n4 = self.n3*4-1
            self.n5 = list(range(self.n3, self.n4-1))
            self.n6 = self.n4-self.n3-1
            self.n7 = self.n6-1
            self.lost = False
        else:
            self.lost = True
            self.n3 = 0
            self.n4 = 0
            self.n5 = []
            self.n6 = 0
            self.n7 = 0

    def _trans1(self):
        lst1 = list(self.n5)
        random.shuffle(lst1)
        n2 = self.n6/2
        lst3 = lst1[:n2]
        lst4 = lst1[n2:]
        return dict(list(zip(lst3,lst4))+list(zip(lst4,lst3)))

    def trans(self, a1, a2):
        random.seed(self._sh(a2))
        lst1 = self._trans1()
        lst2 = []
        for ch in a1:
            v = ord(ch)
            if v < self.n3 or v >= self.n4:
                lst2.append(ch)
            else:
                r = random.randint(0,self.n7)
                v1 = (v - self.n3 + r) % self.n6 + self.n3
                v2 = lst1.get(v1)
                try:
                    v3 = (v2 - self.n3 - r) % self.n6 + self.n3
                except:
                    print("Trans Error", file=sys.stderr)
                lst2.append(chr(v3))
        return ''.join(lst2)


    # since the hash function seems to be different on different
    # machines here is a simple string hash that hashes up to the first 40
    # chars

    
    def _sh(self, text):
        if self.lost:
            return 0
        hash_value = 5381
        num = 0
        for c in text:
            if num > 40:
                break
            num += 1
            hash_value = 0x00ffffff & ((hash_value << 5) + hash_value + ord(c))
        return hash_value


