#! /usr/bin/env python

import base64
import cgi
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
tut_info_file = os.path.join(base_dir, "tut_admin.txt")

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
date_format = "%d/%m/%y"

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

      The first element of the tuple is a base64 encoding of the sha512 hash
      of the server copy of the student's answer.

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

    # encode hash as base64
    answer_hash = base64.b64encode(answer_hash)

    response_dict = {
        'hash': answer_hash,
        'timestamp': timestamp,
    }

    return json.dumps(response_dict)


@action('submit')
def submit_answer(tut_id, tut_id_crypt, tut_check_num, code):
    user = uqauth.get_user()
    if tut_id_crypt != str(_sh(tut_id + user)):
        raise ActionError("Error 901. Report this error to a maintainer.")
    #admin_file = os.path.join(data_dir, 'tut_admin.txt')
    admin_fid = open(tut_info_file, 'U')
    admin_lines = admin_fid.readlines()
    admin_fid.close()
    found = False
    section = ''
    tut_name = ''
    for line in admin_lines:
        if line.startswith('['):
            section = line.strip()[:-1]
        elif line.startswith(tut_id):
            found = True
            tut_name = line.split(' ', 1)[1].strip()
            break
    if tut_name == '' or section == '':
        raise ActionError("Tutorial not found")
    first_word = section.split(' ', 1)[0][1:]
    try:
        due_date = datetime.datetime.strptime(first_word, date_format)
        due_time = due_date.replace(hour=due_hour)
    except Exception as e:
        #print e
        due_time = None
    today = datetime.datetime.today()
    sub_file = os.path.join(data_dir, user+'.sub')
    header = '\n##$$%s$$##\n' % tut_name
    if due_time and today > due_time:
        msg = "LATE"
        sub_text = header + 'LATE\n' + tut_check_num + '\n' + code
    else:
        msg = "OK"
        sub_text = header + 'OK\n' + tut_check_num + '\n' + code
    if os.path.exists(sub_file):
        fd = open(sub_file, 'U')
        file_text = fd.read()
        fd.close()
        if header in file_text:
            raise ActionError("Already submitted")
        fd = open(sub_file, 'a')
        fd.write(sub_text)
        fd.close()
        return msg
    else:
        fd = open(sub_file, 'w')
        fd.write(sub_text)
        fd.close()
        return msg


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


def _sh(text):
    hash_value = 5381
    num = 0
    for c in text:
        if num > 40:
            break
        num += 1
        hash_value = 0x00ffffff & ((hash_value << 5) + hash_value + ord(c))
    return hash_value


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
