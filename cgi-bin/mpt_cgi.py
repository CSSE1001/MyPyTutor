#! /usr/bin/env python

import cgi
import inspect
import json
import os
import shutil
import functools

import support
import uqauth

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

ADMINS = ['uqprobin', 'uqspurdo']

ACTIONS = {}


# A wrapper for the uqauth.get_user() interface
def get_user_and_add():
    """Returns the result of uqauth.get_user(), and also permanently records
       the user's information (name, email) for administration purposes."""
    info = uqauth.get_user_info()
    userid, name, email = map(str, [info['user'], info.get('name', 'NO_NAME'),
                                    info.get('email', 'NO_EMAIL')])
    support.add_user(support.User(userid, name, email, support.NOT_ENROLLED))
    return str(info['user'])


class ActionError(Exception):
    """An exception that represents some error in the request.
    Text messages of this error will be displayed to the user in the client.
    """
    pass


class NullResponse(Exception):
    """
    An exception that represents a null response.

    This is used for error-like conditions which are nevertheless possible in
    the course of normal operation (ie, are not exceptional).
    For example, an attempt to get information on an answer that doesn't exist
    should raise a NullResponse.

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
    user = get_user_and_add()

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
      NullResponse: If there is no code to download.

    """
    # authenticate the user
    user = get_user_and_add()

    # read the answer
    code = support.read_answer(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    if code is None:
        raise NullResponse('No code to download')

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
      NullResponse: If no answer can be found to this problem.

    """
    # authenticate the user
    user = get_user_and_add()

    # grab our data
    answer_hash = support.get_answer_hash(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    timestamp = support.get_answer_modification_time(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    if answer_hash is None or timestamp is None:
        raise NullResponse('No code exists for this problem')

    # build our response
    response_dict = {
        'hash': answer_hash,
        'timestamp': timestamp,
    }

    return json.dumps(response_dict)


@action('submit')
def submit_answer(tutorial_hash, code, num_attempts):
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

    If the tutorial does exist on the server, but has since been updated (such
    that the given hash is not the latest for the particular tutorial problem),
    then submission is not possible.

    Args:
      tutorial_hash (str): The sha512 hash of the tutorial folder, encoded as
          a base32 string.
      code (str): The student's code.
      num_attmepts (int): The number of attempts that the student mde before
        the current submission.

    Returns:
      'OK' if submitted on time.
      'LATE' if submitted late.
      'LATE_OK' if submitted late without penalty.

    Raises:
      ActionError: If tutorial hash does not match a known tutorial package,
          or if the tutorial hash matches a package but is out of date,
          or if attempting to add the submission fails.
      NullResponse: If the student has already submitted this tutorial.

    """
    # authenticate the user
    user = get_user_and_add()

    # check that the tutorial actually exists
    hashes = support.parse_tutorial_hashes()

    if tutorial_hash not in hashes:
        raise ActionError('Invalid tutorial: {}'.format(tutorial_hash))
    if hashes[tutorial_hash].hash != tutorial_hash:
        raise ActionError(
            'Invalid tutorial: {}\nThis hash is not the latest for the '
            'tutorial in question.  Please update the local tutorials package '
            'before submitting this tutorial.'.format(tutorial_hash)
        )

    tutorial_info = hashes[tutorial_hash]

    # check if the student has already submitted this tutorial
    # we need to see if this has been submitted *at all*, which includes under
    # any previous hash that the problem may have had
    submissions = support.parse_submission_log(user)

    valid_hashes = [h for h, ti in hashes.items() if ti == tutorial_info]

    try:
        next(si for si in submissions if si.hash in valid_hashes
             and si.date is not None)
        raise NullResponse(
            'Tutorial already submitted: {}'.format(tutorial_hash)
        )
    except StopIteration:
        pass  # we want this -- no such tutorial has been submitted

    # write out the submission
    submission = support.add_submission(user, tutorial_hash, code)
    if submission is None:
        raise ActionError('Could not add submission: {}'.format(tutorial_hash))

    # record the number of attempts
    support.record_attempts(user, tutorial_hash, num_attempts)

    # return either 'OK' or 'LATE'
    if submission.date <= tutorial_info.due:
        return 'OK'
    elif support.has_allow_late(user, tutorial_hash):
        return 'LATE_OK'
    else:
        return 'LATE'


@action('get_submissions')
def show_submit():
    """
    Return the submissions for the current user.

    Returns:
      A list of two-element tuples.
      Each tuple represents a single tutorial.

      The first element in the tuple is the hash of the tutorial package (in
      the same format as usual, ie base32 encoded sha512 hash).

      The second element in the tuple is one of the strings
      {'MISSING', 'OK', 'LATE', 'LATE_OK'}.

    """
    # authenticate the user
    user = get_user_and_add()
    return json.dumps(support.get_submissions_for_user(user).items())


@action('provide_feedback')
def provide_feedback(subject, feedback, code=''):
    """
    Register the given feedback for the given user.

    """
    # authenticate the user
    user = uqauth.get_user()

    # delegate adding the feedback to the support file
    support.add_feedback(user, subject, feedback, code)

    return 'OK'  # this can't fail


@action('get_feedback', admin=True)
def get_feedback():
    """
    Return a JSON list of feedback, with each item of feedback represented
    as a JSON dictionary.

    """
    feedback = support.get_all_feedback()

    return json.dumps(feedback)


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


@action('get_student_results', admin=True)
def get_results(user):
    """
    Return results for the given student.

    Args:
      user (str): The user to return the submissions for.

    Returns:
      A list of two-element tuples.
      Each tuple represents a single tutorial.

      The first element in the tuple is the hash of the tutorial package (in
      the same format as usual, ie base32 encoded sha512 hash).

      The second element in the tuple is one of the strings
      {'MISSING', 'OK', 'LATE', 'LATE_OK'}.

    """
    return json.dumps(support.get_submissions_for_user(user).items())


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
    """
    Return the URL of a zip file containing up-to-date tutorial problems.

    This assumes that the client is requesting CSSE1001Tutorials. Other
    implementations of MyPyTutor could support additional tutorial packages
    through additional calls, or through adding arguments to this call.

    """
    return TUTORIAL_ZIPFILE_URL


@action('get_mpt')
def get_mpt():
    """
    Return the URL of a zip file containing the latest version of MyPyTutor.

    """
    return MPT34_ZIPFILE_URL


@action('get_version')
def get_version():
    """
    Return the current MyPyTutor version, as a string.

    """
    return support.get_mypytutor_version()


@action('get_tutorials_timestamp')
def get_tutorials_timestamp():
    """
    Return the timestamp of the current tutorial package, as a string.

    """
    return support.get_tutorials_timestamp()


def main():
    form = cgi.FieldStorage(keep_blank_values=True)

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
    except NullResponse as e:
        print "Content-Type: text/plain\n"
        print "mypytutor_nullresponse>>>" + str(e)
    else:
        print "Content-Type: text/plain\n"
        print "mypytutor>>>" + result

if __name__ == '__main__':
    main()
