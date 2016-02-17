import base64
from collections import namedtuple
from datetime import datetime, timedelta
import json
import os


from tutorlib.config.namespaces import Namespace
from tutorlib.interface.problems import TutorialPackage


DUE_DATE_HOUR = 18
INPUT_DATE_FORMAT = "%d/%m/%y"
DATE_FORMAT = "%H_%d/%m/%y"
TIMEZONE_OFFSET = timedelta(hours=10)  # UTC+10


# NB: A lot of this is a direct copy of code from cgi-bin/support.py
#     I don't know a nice way to link them atm (maybe simlink in the working
#     directory might do it?)
TutorialHashInfo = namedtuple(
    'TutorialInfo',
    ['hash', 'due', 'package_name', 'problem_set_name', 'tutorial_name']
)


def write_tutorial_hashes(f, path):
    """
    Create the tutorial hashes file for the tutorial package in the given
    destination directory.

    It is assumed that destination_dir contains a valid tutorial package.
    As a result, this function must only be called after the package itself
    has been created.

    Args:
      f (file): The file to write the tutorial hashes data to.
      path (str): The path to the tutorial package.

    """
    options = Namespace(tut_dir=path, ans_dir='/tmp/notreal')
    tutorial_package = TutorialPackage(path, options)

    tutorial_package_name = tutorial_package.name.replace(' ', '_')

    for problem_set in tutorial_package.problem_sets:
        date_obj = datetime.strptime(problem_set.date, INPUT_DATE_FORMAT)
        date_obj = date_obj.replace(hour=DUE_DATE_HOUR)

        date_obj -= TIMEZONE_OFFSET  # reverse timezone offset

        due_date_str = date_obj.strftime(DATE_FORMAT)

        problem_set_name = problem_set.name.replace(' ', '_')

        for tutorial in problem_set:
            b32hash = base64.b32encode(tutorial.hash).decode('utf8')
            tutorial_name = tutorial.name.replace(' ', '_')

            data = [
                b32hash,
                due_date_str,
                tutorial_package_name,
                problem_set_name,
                tutorial_name,
            ]
            f.write(' '.join(data) + '\n')


def parse_tutorial_hashes(f):
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

    Args:
      f (file): The file to read the tutorial hashes data from.

    Returns:
      A list of TutorialInfo objects, corresponding to the tutorials in
      the tutorial_hashes file.

    """
    data = []

    for line in filter(None, map(str.strip, f)):
        hash_str, due_date_str, pkg_name, pset_name, tut_name \
            = line.split()

        due_date = datetime.strptime(due_date_str, DATE_FORMAT)

        tutorial_info = TutorialHashInfo(
            hash_str, due_date, pkg_name, pset_name, tut_name
        )
        data.append(tutorial_info)

    return data


def parse_hash_mappings(f):
    """
    Get a dictionary mapping old hash keys to new ones.

    It is a precondition that there are no duplicate old_hash entries.

    Args:
      f (file): The tutorial hash mappings file to read from.

    Returns:
      A dictionary mapping old hash keys to new ones.

    """
    return json.loads(f.read())


def write_hash_mappings(f, hash_mappings):
    """
    Write the given hash mappings to file.

    Args:
      f (file): The tutorial hash mappings file to write to.
      hash_mappings ({str:str?}): The hash mappings.

    """
    f.write(json.dumps(hash_mappings, indent=4))


def generate_hash_mappings(old_hashes, new_hashes):
    """
    Generate the hash mappings for the given sets of tutorial hashes.

    Possible changes:
      * addition of tutorial (new key in new_hashes)
        -> no need to do anything; this is the assumed default
      * removal of tutorial (key in old_hashes is not in new_hashes)
        -> map to None
      * change of tutorial hash (same key in both old_hashes and new_hashes)
        -> map to new hash

    Args:
      old_hashes ([TutorialHashInfo]): The old tutorial hashes.
      new_hashes ([TutorialHashInfo]): The new tutorial hashes.

    Returns:
      A dictionary mapping old hash keys to new ones.

    """
    # transform TutorialHashInfo objects to dict
    to_key_value_pair = lambda thi: \
        ((thi.package_name, thi.problem_set_name, thi.tutorial_name), thi.hash)
    old_hashes_dict = dict(map(to_key_value_pair, old_hashes))
    new_hashes_dict = dict(map(to_key_value_pair, new_hashes))

    hash_mappings = {}

    for name, tutorial_hash in old_hashes_dict.items():
        if name not in new_hashes_dict:
            hash_mappings[tutorial_hash] = None
        elif new_hashes_dict[name] != tutorial_hash:
            hash_mappings[tutorial_hash] = new_hashes_dict[name]

    return hash_mappings


def update_hashes(parent_dir, tutorial_package_path):
    tutorial_hashes_path = os.path.join(parent_dir, 'tutorial_hashes')
    hash_mappings_path = os.path.join(parent_dir, 'tutorial_hash_mappings')

    # handle first-time run
    if not os.path.exists(tutorial_hashes_path):
        with open(tutorial_hashes_path, 'w') as f:
            pass

    if not os.path.exists(hash_mappings_path):
        with open(hash_mappings_path, 'w') as f:
            write_hash_mappings(f, {})

    # load the old hashes
    with open(tutorial_hashes_path) as f:
        old_hashes = parse_tutorial_hashes(f)

    # write out the new hashes
    with open(tutorial_hashes_path, 'w') as f:
        write_tutorial_hashes(f, tutorial_package_path)

    # load the new hashes
    # yes, this method of writing and then re-reading is lazy; sue me
    with open(tutorial_hashes_path) as f:
        new_hashes = parse_tutorial_hashes(f)

    # load the old mappings
    with open(hash_mappings_path) as f:
        old_mappings = parse_hash_mappings(f)

    # check that we don't have any unexpected collisions
    for thi in new_hashes:
        if thi.hash in old_mappings:
            raise AssertionError('''Tutorial hash collision!
{} is the hash of a current tutorial, but this hash already has a forward
mapping.  If a new tutorial was added with this hash, no submissions could be
recorded for this tutorial, as they would map forward using the existing
mapping.  This error is unrecoverable.

Note that reverting to a previous version of a tutorial is not supported.

If you have not pushed your changes to the server, replace the local
tutorial_hash_mappings file with a fresh copy from the server, and remake.

If you have pushed your changes to the server, you will need to make some
change to the local file so as to alter its hash.
'''.format(thi.hash)
            )

    # generate the new mappings
    new_mappings = generate_hash_mappings(old_hashes, new_hashes)
    new_mappings.update(old_mappings)

    # write the new mappings
    with open(hash_mappings_path, 'w') as f:
        write_hash_mappings(f, new_mappings)

