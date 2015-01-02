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

import uqauth

######## start config #################################

# Base directory for server file storage
base_dir = "/opt/local/share/MyPyTutor/MPT3_CSSE1001"

# where student data is to be put/found
data_dir = os.path.join(base_dir, "data")
answers_dir = os.path.join(data_dir, "answers")
submissions_dir = os.path.join(data_dir, "submissions")

# the file containing the timestamp for the tutorial problems
timestamp_file = os.path.join(base_dir, "config.txt")

# the file containing the version number of MyPyTutor
mpt_version_file = os.path.join(base_dir, "mpt_version.txt")

# the file containing the tutorial information
tutorial_hashes_file = os.path.join(submissions_dir, "tutorial_hashes")

submission_log_name = "submission_log"

# the zip file containing the tutorial info
tut_zipfile_url = "http://csse1001.uqcloud.net/mpt3/CSSE1001Tutorials.zip"

# the zip file containing MyPyTutor2.5
#mpt25_url = "https://student.eait.uq.edu.au/mypytutor/MyPyTutor/CSSE1001/MyPyTutor25.zip"
# the zip file containing MyPyTutor2.6
#mpt26_url = "http://mypytutor.cloud.itee.uq.edu.au/MyPyTutor/CSSE1001/MyPyTutor26.zip"
# the zip file containing MyPyTutor2.7
#mpt27_url = "http://csse1001.uqcloud.net/mpt/MyPyTutor27.zip"
# the zip file containing MyPyTutor3.4
mpt34_url = "http://csse1001.uqcloud.net/mpt3/MyPyTutor34.zip"

# datetime format used in due dates
date_format = "%H_%d/%m/%y"

# hour of day (24hr clock) for due time
due_hour = 17

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


def _get_answer_path(user, tutorial_package_name, problem_set_name,
        tutorial_name, create_dir=False):
    """
    Get a path indicating where the server copy of the student's answer to the
    given tutorial problem should be stored.

    File structure:
      base_dir/
        data/
          answers/
            <username>/
              <tutorial_package_name>/
                <problem_set_name>/
                  <tutorial_name>

    Note that it's possible for students to rename the tutorial package (and
    theoretically also the problem sets, but with a lot more work).  This
    function will make use of whatever name the student has chosen to assign
    to the tutorial package.
    Because we just store copies of the answer, and don't do any checking off
    this directly, that's not an issue.  (After all, we're just looking to
    mirror, in a sense, the local filesystem.)

    The only way we could end up with issues is if the student creates two
    installations of MyPyTutor, with different names for the same package, and
    then syncs both of them with the server.

    Args:
      user (str): The username of the current user.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').
      create_dir (bool, optional): Whether to create the problem set directory
          if it does not already exist.  Defaults to False.

    Returns:
      The path to the answer file for the given tutorial details.
      None if the problem_set does not exist, and create_dir is False.

    """
    # sanitise the path components
    # this is essential to avoid, eg, tutorial_name='hi/../../passwords.uhoh'
    tutorial_package_name = secure_filename(tutorial_package_name)
    problem_set_name = secure_filename(problem_set_name)
    tutorial_name = secure_filename(tutorial_name)

    # create/get our directory structure
    problem_set_dir = os.path.join(
        answers_dir,
        user,
        tutorial_package_name,
        problem_set_name,
    )
    if not os.path.exists(problem_set_dir):
        if not create_dir:
            return None

        os.makedirs(problem_set_dir)  # TODO: set mode

    return os.path.join(problem_set_dir, tutorial_name)


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

    # grab our path
    tutorial_path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
        create_dir=True,
    )

    with open(tutorial_path, 'w') as f:
        f.write(code)

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

    # grab our path
    tutorial_path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
    )
    if tutorial_path is None:
        raise ActionError('No code to download')  # TODO: is this an error?

    # read the file
    with open(tutorial_path) as f:
        code = f.read()

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
      We use base32 strings through for consistency (as they are required for
      submission filenames, given that basee64 contains invalid chars).

      The second element is the last-modified time of the answer, as a unix
      timestamp.

    Raises:
      ActionError: If no answer can be found to this problem.

    """
    # authenticate the user
    user = uqauth.get_user()

    # grab our path
    tutorial_path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
    )
    if not os.path.exists(tutorial_path):
        raise ActionError('No code exists for this problem')

    # get our information
    with open(tutorial_path) as f:
        data = f.read().encode('utf8')
        answer_hash = hashlib.sha512(data).digest()

    timestamp = os.path.getmtime(tutorial_path)

    # encode hash as base32
    answer_hash = base64.b32encode(answer_hash)

    response_dict = {
        'hash': answer_hash,
        'timestamp': timestamp,
    }

    return json.dumps(response_dict)


TutorialInfo = namedtuple(
    'TutorialInfo',
    ['hash', 'due', 'package_name', 'problem_set_name', 'tutorial_name']
)


def _parse_tutorial_hashes():
    """
    Get all valid tutorial hashes, as TutorialInfo objects.

    Format of tutorial_hashes file:
      hash due_hh_dd_mm_yy package_name problem_set_name tutorial_name

    It is assumed that there will be no hash collisions.  If there are, this
    can be fixed by editing one of the package files ;)

    Hashes are sha512, encoded as base32 strings.

    This function assumes that the tutorial_hashes file is in the correct
    format, and so does not handle errors which would result from a
    badly-formatted file.

    Returns:
      A list of TutorialInfo objects, corresponding to the tutorials in
      the tutorial_hashes file.

    """
    data = []

    with open(tutorial_hashes_file) as f:
        for line in filter(None, map(str.strip, f)):
            hash_str, due_date_str, pkg_name, pset_name, tut_name \
                    = line.split()

            due_date = datetime.datetime.strptime(due_date_str, date_format)

            tutorial_info = TutorialInfo(
                hash_str, due_date, pkg_name, pset_name, tut_name
            )
            data.append(tutorial_info)

    return data


def _get_or_create_user_submissions_dir(user):
    """
    Get the submissions directory for the user.

    If the directory does not exist, create it.

    Assumes that the username cannot be spoofed (and so does not need to be
    sanitised prior to use).

    Args:
      user (str): The username to get the submissions directory for.

    Returns:
      The path to the submissions directory for the given user.

    """
    submissions_path = os.path.join(submissions_dir, user)

    if not os.path.exists(submissions_dir):
        os.mkdir(submissions_path)  # TODO: mode

    return submissions_path


def _get_or_create_user_submissions_file(user):
    """
    Get the path to the submissions log file for the given user.

    The file will be created if it does not exist.

    Args:
      user (str): The username to get the submissions file for.

    Returns:
      The path to the submissions file for the given user.

    """
    # we assume that the username does not need sanitisation
    user_submissions_dir = _get_or_create_user_submissions_dir(user)
    submission_log_path = os.path.join(
        user_submissions_dir, submission_log_name
    )

    # create the file if it does not exist
    if not os.path.exists(submission_log_path):
        with open(submission_log_path, 'w') as f:
            pass

    return submission_log_path


TutorialSubmission = namedtuple('TutorialSubmission', ['hash', 'submitted'])


def _parse_submission_log(user):
    """
    Get the submission log for the given user.

    Format of submission_log file:
      hash submitted_dd_mm_yy

    Hashes are sha512, encoded as base32 strings.

    We don't store information in the submission_log about whether or not the
    tutorial was submittted on time, as that would be redundant.

    Args:
      user (str): The username to get the submissions log for.

    Returns:
      A list of TutorialSubmission objects representing the user's submissions.

    """
    data = []

    submission_log_path = _get_or_create_user_submissions_file(user)

    # parse the file itself
    with open(submission_log_path) as f:
        for line in filter(None, map(str.strip, f)):
            hash_str, submitted_date_str = line.split()

            submitted_date = datetime.datetime.strptime(
                submitted_date_str, date_format
            )

            submission_info = TutorialSubmission(hash_str, submitted_date)
            data.append(submission_info)

    return data


def _add_submission(user, tutorial_hash, code):
    """
    Submit the tutorial with the given hash for the given user.

    This involves updating the user's submission log, as well as saving the
    actual code to disk.

    Args:
      user (str): The user who submitted the tutorial problem answer.
      tutorial_hash (str): The tutorial hash, as a base32 string.
      code (str): The user's code.

    Returns:
      A TutorialSubmission object corresponding to the submission.

    """
    # build our data
    submitted_date = datetime.datetime.now()
    submitted_date_str = submitted_date.strftime(date_format)

    submission = TutorialSubmission(tutorial_hash, submitted_date)

    # write to the log
    submission_log_path = _get_or_create_user_submissions_file(user)

    with open(submission_log_path, 'a') as f:
        f.write(' '.join([tutorial_hash, submitted_date_str]))

    # a base32 hash should NEVER need to be sanitised, with the exception of
    # removing the padding characters
    # if it does, something is VERY wrong
    stripped_b32_hash = tutorial_hash.strip('=')
    if stripped_b32_hash != secure_filename(stripped_b32_hash):
        raise ActionError('Invalid hash: {}'.format(stripped_b32_hash))

    # write the student's code to file
    # this file should not exist, but if it does, overwrite it
    user_submissions_dir = _get_or_create_user_submissions_dir(user)
    answer_path = os.path.join(user_submissions_dir, stripped_b32_hash)

    with open(answer_path, 'w') as f:
        f.write(code)

    # return the TutorialSubmission object
    return submission


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

    As far as storing results, we're currently putting them on the filesystem,
    rather than worrying about a database.  (Wouldn't be too hard to change.)

    Our file structure looks something like this:
      base_dir/
        answers/  <- we DO NOT update this when an answer is submitted
        submissions/
          tutorial_hashes <- static var, pointing to text file
          <username>/
            submission_log <- see below
            <submitted_answer_hash> <- file containing answer code

    First, we check that the given hash actually exists, by looking in our
    configuration file (tutorial_hashes).

    If the file does exist, we update the submission_log for the given user,
    and then store the answer in a file named after the tutorial hash.

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
    hashes = _parse_tutorial_hashes()

    try:
        tutorial_info = next(ti for ti in hashes if ti.hash == tutorial_hash)
    except StopIteration:
        raise ActionError('Invalid tutorial: {}'.format(tutorial_hash))

    # check if the student has already submitted this tutorial
    submissions = _parse_submission_log(user)

    try:
        next(si for si in submissions if si.hash == tutorial_hash)
        raise ActionError(
            'Tutorial already submitted: {}'.format(tutorial_hash)
        )
    except StopIteration:
        pass  # we want this -- no such tutorial has been submitted

    # write out the submission
    submission = _add_submission(user, tutorial_hash, code)

    # return either 'OK' or 'LATE'
    return 'OK' if submission.submitted <= tutorial_info.due else 'LATE'


@action('show')
def show_submit():
    user = uqauth.get_user()
    sub_file = os.path.join(data_dir, user+'.sub')
    if os.path.exists(sub_file):
        fd = open(sub_file, 'U')
        file_text = fd.read()
        fd.close()
        return file_text
    else:
        return ''


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
    return tut_zipfile_url


@action('get_mpt34')
def get_mpt34():
    return mpt34_url


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
