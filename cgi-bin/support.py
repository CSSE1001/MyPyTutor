"""
At the moment, we're storing all our data on the filesystem, presumably so that
we don't have to bother with a database.

In order to make any later transition easier, the filesystem-specific code (ie,
all the code which access files or is otherwise aware that we're using the
filesystem like this) has been extracted into this file.

The cgi code should remain unaware of the underlying storage mechanisms.

File structure:
  base_dir/
    data/
      answers/
        <username>/
          <tutorial_package_name>/
            <problem_set_name>/
              <tutorial_name>        <- answer file, with python code
      submissions/
        tutorial_hashes              <- tutorial hashes / info file
        <username>/
          submission_log             <- student submission log
          <tutorial_problem_hash>    <- the student's answer, as submitted

"""
import base64
from collections import namedtuple
from datetime import datetime
import dateutil.parser
import hashlib
import os
from werkzeug.utils import secure_filename


# base directory for server file storage
BASE_DIR = "/opt/local/share/MyPyTutor/MPT3_CSSE1001"

# where student data is to be put/found
DATA_DIR = os.path.join(BASE_DIR, "data")
ANSWERS_DIR = os.path.join(DATA_DIR, "answers")
SUBMISSIONS_DIR = os.path.join(DATA_DIR, "submissions")

# submission specific constants
TUTORIAL_HASHES_FILE = os.path.join(SUBMISSIONS_DIR, "tutorial_hashes")
SUBMISSION_LOG_NAME = "submission_log"
DUE_DATE_FORMAT = "%H_%d/%m/%y"


def _get_answer_path(user, tutorial_package_name, problem_set_name,
        tutorial_name, create_dir=False):
    """
    Get a path indicating where the server copy of the student's answer to the
    given tutorial problem should be stored.

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
        ANSWERS_DIR,
        user,
        tutorial_package_name,
        problem_set_name,
    )
    if not os.path.exists(problem_set_dir):
        if not create_dir:
            return None

        os.makedirs(problem_set_dir)  # TODO: set mode

    return os.path.join(problem_set_dir, tutorial_name)


def read_answer(user, tutorial_package_name, problem_set_name, tutorial_name):
    """
    Read the relevant answer for the given user.

    Args:
      user (str): The username of the current user.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      None if there exists no such answer on the server.
      The text contents of the answer file otherwise.

    """
    path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
        create_dir=True,
    )
    if path is None or not os.path.exists(path):
        return None

    with open(path) as f:
        return f.read()


def write_answer(user, tutorial_package_name, problem_set_name, tutorial_name,
        code):
    """
    Write the relevant answer for the given user using the given code.

    Args:
      user (str): The username of the current user.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').
      code (str): The code to write to the answer file.

    """
    path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
        create_dir=True,
    )

    with open(path, 'w') as f:
        f.write(code)


def get_answer_hash(user, tutorial_package_name, problem_set_name,
        tutorial_name):
    """
    Get the hash of the student's current answer to the relevant question.

    Args:
      user (str): The username of the current user.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      None if the answer does not exist on the server.
      A base32 encoding of the sha512 hash of the server copy of the student's
      answer to the relevant question, otherwise.

    """
    code = read_answer(
        user, tutorial_package_name, problem_set_name, tutorial_name
    )
    if code is None:
        return None

    data = code.encode('utf8')
    answer_hash = hashlib.sha512(data).digest()

    b32_bytes = base64.b32encode(answer_hash)
    b32_str = b32_bytes.decode('ascii')

    return b32_str


def get_answer_modification_time(user, tutorial_package_name, problem_set_name,
        tutorial_name):
    """
    Get the last modification time of the student's current answer to the
    relevant question.

    Args:
      user (str): The username of the current user.
      tutorial_package_name (str): The name of the tutorial package (eg, for
          UQ students, this will be something like 'CSSE1001Tutorials').
      problem_set_name (str): The name of the problem set (eg, 'Introduction').
      tutorial_name (str): The name of the tutorial problem (note that this
          will be, eg, 'Using Functions', not 'fun1.tut').

    Returns:
      None if the answer does not exist on the server.
      The last-modified time of the answer, as a unix timestamp, otherwise.

    """
    path = _get_answer_path(
        user, tutorial_package_name, problem_set_name, tutorial_name,
        create_dir=True,
    )
    if path is None:
        return None

    return os.path.getmtime(path)


TutorialInfo = namedtuple(
    'TutorialInfo',
    ['hash', 'due', 'package_name', 'problem_set_name', 'tutorial_name']
)


def parse_tutorial_hashes():
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

    with open(TUTORIAL_HASHES_FILE) as f:
        for line in filter(None, map(str.strip, f)):
            hash_str, due_date_str, pkg_name, pset_name, tut_name \
                = line.split()

            due_date = datetime.strptime(due_date_str, DUE_DATE_FORMAT)

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
    submissions_path = os.path.join(SUBMISSIONS_DIR, user)

    if not os.path.exists(submissions_path):
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
        user_submissions_dir, SUBMISSION_LOG_NAME
    )

    # create the file if it does not exist
    if not os.path.exists(submission_log_path):
        with open(submission_log_path, 'w') as f:
            pass

    return submission_log_path


TutorialSubmission = namedtuple('TutorialSubmission', ['hash', 'submitted'])


def parse_submission_log(user):
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

            submitted_date = dateutil.parser.parse(submitted_date_str)

            submission_info = TutorialSubmission(hash_str, submitted_date)
            data.append(submission_info)

    return data


def add_submission(user, tutorial_hash, code):
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
      None if the submission could not be added.

    """
    # build our data
    submitted_date = datetime.now()
    submitted_date_str = submitted_date.isoformat()

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
        return None

    # write the student's code to file
    # this file should not exist, but if it does, overwrite it
    user_submissions_dir = _get_or_create_user_submissions_dir(user)
    answer_path = os.path.join(user_submissions_dir, stripped_b32_hash)

    with open(answer_path, 'w') as f:
        f.write(code)

    # return the TutorialSubmission object
    return submission
