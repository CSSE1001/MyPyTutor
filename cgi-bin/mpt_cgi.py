#! /usr/bin/env python

import base64
import cgi
from collections import namedtuple
import datetime
import hashlib
import inspect
import json
import os
import shutil
import functools
from werkzeug.utils import secure_filename

import support
import uqauth

######## start config #################################

# the file containing the timestamp for the tutorial problems
#timestamp_file = os.path.join(base_dir, "config.txt")  # TODO: refactor

# the file containing the version number of MyPyTutor
#mpt_version_file = os.path.join(base_dir, "mpt_version.txt") # TODO: refactor

# static files (eg zipfiles)
TUTORIAL_ZIPFILE_URL = "http://csse1001.uqcloud.net/mpt3/CSSE1001Tutorials.zip"
MPT34_ZIPFILE_URL = "http://csse1001.uqcloud.net/mpt3/MyPyTutor34.zip"



######## end config   #################################

HTML_ERROR = '''Content-Type: text/html

<!DOCTYPE html>
<html>
    <head>
        <title>MyPyTutor</title>
    </head>
    <body>
        <p>{}</p>
    </body>
</html>'''

ADMINS = ['uqprobin']

ACTIONS = {}


class ActionError(Exception):
    """An exception that represents some error in the request.
    Text messages of this error will be displayed to the user in the client.
    """
    pass


def action(name, admin=False):
    """Decorator constructor to register different server actions.

    If the action requires administrator privileges

    The decorated function could raise certain errors:
    * a ActionError if the CGI form is missing a required parameter,
    * a uqauth.Redirected if a login is required,
    """
    # Create the decorator
    def wrapper(func):
        # Get the list of argument details for the function
        argspec = inspect.getargspec(func)
        num_required = len(argspec.args)
        if argspec.defaults is not None:
            num_required -= len(argspec.defaults)

        @functools.wraps(func)
        def wrapped(form):
            # Check privileges
            if admin and uqauth.get_user() not in ADMINS:
                raise ActionError("Forbidden: insufficient privileges")

            # Get the arguments out of the form
            args = {}
            for i, arg in enumerate(argspec.args):
                # If the arg doesn't have a default value and isn't given, fail
                if arg in form:
                    args[arg] = form[arg].value
                elif i < num_required:
                    raise ActionError("Required parameter {!r} not given.\n"
                                      "Report to maintainer.".format(arg))

            return func(**args)

        # Store the action in the global index
        ACTIONS[name] = wrapped
        return wrapped
    return wrapper


@action('userinfo')
def userinfo():
    user = uqauth.get_user_info()
    result = {key: str(user[key]) for key in ('user', 'name')}
    return json.dumps(result)


@action('upload')
def upload_code(code, tutorial_package_name, problem_set_name, tutorial_name):
    """
    Store the given code on the server for the student's account.

    Args:
      code (str): The student's code.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      'OK' if successful.

    Raises:
      ActionError: If the code is too large.

    """
    # authenticate the user
    user = uqauth.get_user()

    # immediately fail if the student is trying to send us too much junk
    # (so that we can't easily be DOSed)
    if len(code) > 5*1024:
        raise ActionError('Code exceeds maximum length')

    # write the answer
    support.write_answer(
        user, tutorial_package_name, problem_set_name, tutorial_name, code
    )

    return "OK"


@action('download')
def download_code(tutorial_package_name, problem_set_name, tutorial_name):
    """
    Retrieve the given code on the server for the student's account.

    Args:
      code (str): The student's code.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      The student code, as a string.

    Raises:
      ActionError: If there is no code to download.

    """
    # authenticate the user
    user = uqauth.get_user()

    # read the answer
    code = support.read_answer(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    if code is None:
        raise ActionError('No code to download')  # TODO: is this an error?

    return code


@action('answer_info')
def answer_info(tutorial_package_name, problem_set_name, tutorial_name):
    """
    Return information on the server copy of the student's answer for the
    given tutorial.

    Args:
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      A two-element tuple.

      The first element of the tuple is a base32 encoding of the sha512 hash
      of the server copy of the student's answer.

      The second element is the last-modified time of the answer, as a unix
      timestamp.

    Raises:
      ActionError: If no answer can be found to this problem.

    """
    # authenticate the user
    user = uqauth.get_user()

    # grab our data
    answer_hash = support.get_answer_hash(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    timestamp = support.get_answer_modification_time(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    if answer_hash is None or timestamp is None:
        raise ActionError('No code exists for this problem')

    # build our response
    response_dict = {
        'hash': answer_hash,
        'timestamp': timestamp,
    }

    return json.dumps(response_dict)


@action('submit')
def submit_answer(tutorial_hash, code):
    """
    Submit the student's answer for the given tutorial.

    When we store the answer, we make use of the student's own local naming
    scheme (eg, they could call the tutorial package 'Bob' if they wanted).
    This obviously won't work for submissions; we need consistency.

    Instead, what we do is we take a hash of the entire tutorial package and
    use that to uniquely identify the package.  We ignore the possiblity of
    hash collisions (come on, what are the odds...those totally aren't famous
    last words).

    First, we check that the given hash actually exists.  If it does, we can
    go ahead and add the submission.  Implementation details are hidden in the
    support file (so that we can switch backends if needed).

    Args:
      tutorial_hash (str): The sha512 hash of the tutorial folder, encoded as
          a base32 string.
      code (str): The student's code.

    Returns:
      'OK' if submitted on time.
      'LATE' if submitted late.

    Raises:
      ActionError: If tutorial hash does not match a known tutorial package,
          or if the student has already submitted this tutorial.

    """
    # authenticate the user
    user = uqauth.get_user()

    # check that the tutorial actually exists
    hashes = support.parse_tutorial_hashes()

    try:
        tutorial_info = next(ti for ti in hashes if ti.hash == tutorial_hash)
    except StopIteration:
        raise ActionError('Invalid tutorial: {}'.format(tutorial_hash))

    # check if the student has already submitted this tutorial
    submissions = support.parse_submission_log(user)

    try:
        next(si for si in submissions if si.hash == tutorial_hash)
        raise ActionError(
            'Tutorial already submitted: {}'.format(tutorial_hash)
        )
    except StopIteration:
        pass  # we want this -- no such tutorial has been submitted

    # write out the submission
    submission = support.add_submission(user, tutorial_hash, code)
    if submission is None:
        raise ActionError('Could not add submission: {}'.format(tutorial_hash))

    # return either 'OK' or 'LATE'
    return 'OK' if submission.date <= tutorial_info.due else 'LATE'


@action('get_submissions')
def show_submit():
    """
    Return the submissions for the current user.

    Returns:
      A list of two-element tuples.
      Each tuple represents a single tutorial.

      The first element in the tuple is the hash of the tutorial package (in
      the same format as usual, ie base32 encoded sha512 hash).

      The second element in the tuple is one of 'MISSING', 'OK', and 'LATE'.

    """
    # authenticate the user
    user = uqauth.get_user()

    # get our data
    hashes = support.parse_tutorial_hashes()
    submissions = {sub.hash: sub for sub in support.parse_submission_log(user)}

    # check if our submissions are late or not
    results = []

    for tutorial_info in hashes:
        status = 'MISSING'

        submission = submissions.get(tutorial_info.hash)
        if submission is not None:
            status = 'OK' if submission.date <= tutorial_info.due else 'LATE'

        results.append((tutorial_info.hash, status))

    return json.dumps(results)


@action('match', admin=True)
def match_user(match):
    users_file = os.path.join(data_dir, 'users')
    users = open(users_file, 'U')
    user_lines = users.readlines()
    users.close()
    result = ''
    for user in user_lines:
        if user.startswith('#'):
            continue
        if match in user:
            result += user
    return result


@action('unset_late', admin=True)
def unset_late(the_user, problem):
    problem_tag = "##$$%s$$##" % problem
    #if user == the_user:
    #    return False, 'Error 112'
    sub_file = os.path.join(data_dir, the_user+'.sub')
    sub_fd = open(sub_file, 'U')
    sub_text = sub_fd.readlines()
    sub_fd.close()
    found = False
    updated_text = []
    length = len(sub_text)
    i = 0
    while i < length:
        line = sub_text[i]
        i += 1
        updated_text.append(line)
        if line.startswith(problem_tag):
            found = True
            status = sub_text[i]
            if status.strip() == 'LATE':
                updated_text.append('OK\n')
                i += 1
            else:
                raise ActionError('Error 113')
    if not found:
        raise ActionError('Error 114')
    sub_file_cp = os.path.join(data_dir, 'sub_tmp')
    sub_file_cp_fd = open(sub_file_cp, 'w')
    sub_file_cp_fd.writelines(updated_text)
    sub_file_cp_fd.close()
    sub_fd = open(sub_file, 'U')
    sub_text_new = sub_fd.readlines()
    sub_fd.close()
    if sub_text == sub_text_new:
        shutil.move(sub_file_cp, sub_file)
        return 'OK'
    else:
        return unset_late(the_user, problem)


def get_problem_list():
    #admin_file = os.path.join(data_dir, 'tut_admin.txt')
    admin_fid = open(tut_info_file, 'U')
    admin_lines = admin_fid.readlines()
    admin_fid.close()
    problem_list = []
    for line in admin_lines:
        line = line.strip()
        if line.startswith('[') or line == '':
            continue
        problem_name = line.split(' ', 1)[1].strip()
        problem_list.append(problem_name)
    return problem_list


@action('results', admin=True)
def get_results():
    problem_list = get_problem_list()
    users_file = os.path.join(data_dir, 'users')
    users_fd = open(users_file, 'U')
    user_lines = users_fd.readlines()
    users_fd.close()
    results_list = list(problem_list)
    results_list.append('######')
    for user in user_lines:
        if user.startswith('#'):
            continue
        data = user.split(',')
        if len(data) == 6 and data[2] == 'student':
            student = data[0]
            sub_file = os.path.join(data_dir, student+'.sub')
            try:
                sub_fd = open(sub_file, 'U')
            except:
                continue
            sub_lines = sub_fd.readlines()
            sub_fd.close()
            length = len(sub_lines)
            i = 0
            result_dict = {}
            while i < length:
                line = sub_lines[i].strip()
                i += 1
                if line.startswith('##$$'):
                    problem = line[4:-4]
                    result = sub_lines[i].strip()
                    i += 1
                    tries = sub_lines[i].strip()
                    i += 1
                    result_dict[problem] = "%s/%s" % (result, tries)
            student_result = [student]
            for prob in problem_list:
                student_result.append(result_dict.get(prob, '-'))
            results_list.append(','.join(student_result))
    return '\n'.join(results_list)


@action('get_user_subs', admin=True)
def get_user_subs(the_user):
    the_user = form['the_user'].value
    problem_list = get_problem_list()
    sub_file = os.path.join(data_dir, the_user+'.sub')
    try:
        sub_fd = open(sub_file, 'U')
    except:
        raise ActionError('No info for user {!r}.'.format(the_user))
    sub_lines = sub_fd.readlines()
    sub_fd.close()
    length = len(sub_lines)
    i = 0
    result_dict = {}
    while i < length:
        line = sub_lines[i].strip()
        i += 1
        if line.startswith('##$$'):
            problem = line[4:-4]
            result = sub_lines[i].strip()
            i += 1
            result_dict[problem] = "%s" % result
    user_list = []
    for prob in problem_list:
        user_list.append("%s:::%s" % (prob, result_dict.get(prob, '-')))
    return '\n'.join(user_list)


@action('get_tut_zip_file')
def get_tut_zip_file():
    return TUTORIAL_ZIPFILE_URL


@action('get_mpt34')
def get_mpt34():
    return MPT34_ZIPFILE_URL


@action('get_version')
def get_version():
    with open(mpt_version_file, 'rU') as f:
        return f.read().strip()


def main():
    form = cgi.FieldStorage()

    if 'action' not in form:
        print HTML_ERROR.format("You must use MyPyTutor directly to interact with the online data.")
        return

    action = form['action'].value
    if action not in ACTIONS:
        print HTML_ERROR.format("Unknown action: " + action)
        return

    try:
        result = ACTIONS[action](form)
    except uqauth.Redirected:
        return
    except ActionError as e:
        print "Content-Type: text/plain\n"
        print "mypytutor_error>>>" + str(e)
    else:
        print "Content-Type: text/plain\n"
        print "mypytutor>>>" + result

if __name__ == '__main__':
    main()
