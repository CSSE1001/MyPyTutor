#!/usr/bin/env python2.7
# A CGI script to run the administrator interface

import cgi
import csv
import os
from collections import Counter

from mako.template import Template
from mako import exceptions

import support
import uqauth

# Whitelisted users with access to the admin site
ADMINS = ['uqposhe1', 'uqbmart8', 'uqrtho17']

#################################################
# Temporary, for development/debugging purposes
#               Jackson,    Sean
ADMINS.extend(['uqjgaten', 'uqspurdo'])
#################################################

TUTORS = ADMINS[:]
TUTORS.extend([
    's4290365',                 # Josh Arnold
    's4320859', 'uqbmart8',     # Ben Martin
    's4316494', 'uqscolbr',     # Sam Colbran
    's4284683',                 # Anne Redulla
    's4289147',                 # Chelsea Edmonds
    'uqnhoy', 's4296445',       # Ned Hoy
    'uqrport1', 's4356084',     # Roy Portas
    "uqcwint3", "s4141092",     # Craig Winter
    "s4323542",                 # Rhys McCane
    "s4395960",                 # Ashleigh Richardson
    "",                         # Benjamin O'Brien
    "s4394679"                  # Steven Summers
])

UNAUTHORISED = """Status: 403 Forbidden
Content-Type: text/html

<!DOCTYPE html>
<html>
<head><title>Forbidden</title></head>
<body>
<p>I can't let you do that, {0}.</p>
<p>Do you think you're supposed to have access to this page? If so, contact
the staff and/or MyPyTutor developers.</p>
</body>"""


class StopOutput(Exception):
    """Raised to indicate that the required output has been printed, and that
    nothing else should be printed to stdout.

    There should be a better way to do things that doesn't require this class,
    but that can be fixed later.
    """


# Each action should take the CGI form as input and return a message to display
# in response. The message format is a pair ('alert-xxx', 'message text')

def _set_enrolments_factory(value):
    """Create a function to set or unset the list of selected users in a form
    (setting/unsetting is determined by the True/False value parameter)
    """
    def result(form):
        selected_users = form.getlist('selected_user')
        if not selected_users:
            return ('alert-warning', 'No users selected.')

        # Set the users' enrolment statuses, and count how many were changed.
        count = sum(support.set_user_enrolment(u, value) for u in selected_users)
        if count == 0:
            return ('alert-warning', '0 users modified.')
        elif count < len(selected_users):
            return ('alert-success', '{} users modified, {} unchanged.'
                    .format(count, len(selected_users) - count))
        else:
            return ('alert-success', '{} users modified.'
                    .format(count))
    return result


def _upload_userlist(form):
    filename = 'userlist'
    if filename not in form or not form[filename].filename:
        return ('alert-danger', 'No file given.<br/>{}'.format(form.getvalue(filename)))

    users = []
    for lineno, row in enumerate(csv.reader(form[filename].file), 1):
        try:
            _, _, _, surname, given, email, _, _ = row[:8]
            assert email.endswith('@student.uq.edu.au'), "Unexpected email address"
            name = given + surname
            userid = email.partition('@')[0]
            users.append(support.User(userid, name, email, support.ENROLLED))
        except Exception as e:
            return ('alert-danger',
                    'File format error on line {}: {}: {}'
                    .format(lineno, row, e))

    new_count = newly_enrolled_count = unchanged_count = 0
    for u in users:
        if support.add_user(u):
            new_count += 1
        elif support.set_user_enrolment(u.id, True):
            newly_enrolled_count += 1
        else:
            unchanged_count += 1

    return ('alert-success',
            '{} users added, {} existing users enrolled, {} users unchanged.'
            .format(new_count, newly_enrolled_count, unchanged_count))


def _export(form):
    """Return a list of summarised results for CSV download.
    If the export cannot be performed (e.g. no users selected), then return a
    tuple with the error message to show.

    This is kinda messy and hacky and squeezed into a place that it probably
    shouldn't be.
    """
    selected_users = form.getlist('selected_user')
    if not selected_users:
        return ('alert-warning', 'No users selected.')

    rows = []
    for user in selected_users:
        progress = summarise_progress(user)
        # Scale the mark out of 10
        mark = progress['CORRECT'] * 10.0 / progress['TOTAL']
        rows.append((user, mark))

    print "Content-Type: text/csv"
    print "Content-disposition: attachment;filename=results.csv\n"
    # Too lazy to use a CSV writer
    for line in rows:
        print ','.join(map(str, line))
    raise StopOutput()


ACTIONS = {
           'enrol': _set_enrolments_factory(True),
           'unenrol': _set_enrolments_factory(False),
           'upload': _upload_userlist,
           'export': _export,
          }


def get_sort_key(sort):
    if sort in ('id', 'id_reverse'):
        return lambda user: user.id
    if sort in ('name', 'name_reverse'):
        return lambda user: (user.name.lower(), user.id)
    if sort in ('email', 'email_reverse'):
        return lambda user: user.email
    if sort in ('marks', 'marks_reverse'):
        return lambda user: -summarise_progress(user.id)['CORRECT']
    return None


def summarise_progress(user):
    """Summarise the user's progress by returning a mapping of the form
      {'OK': #, 'LATE': #, 'LATE_OK': #, 'MISSING': #, ...}
    where the values are the number of times the user has a submission of that
    type, and where CORRECT = OK + LATE_OK; TOTAL = CORRECT + LATE + MISSING.
    """
    submissions = support.get_submissions_for_user(user)
    counter = Counter(submissions.values())
    counter['CORRECT'] = counter['OK'] + counter['LATE_OK']
    counter['TOTAL'] = len(submissions)
    return counter


def admin_init(admins=ADMINS, permitted_user=None):
    """
    Check if the user is an admin.

    If the user is not an admin, and is not a permitted user, print an
    error message.

    Args:
      admins ([str], optional): The list of admins to check against.
      permitted_user (str, optional): One additional user who is permitted to
        access the page in question.  This is intended to allow users to see
        their own data.

    Returns:
      Whether the user is authorised.

    """
    try:
        user = uqauth.get_user()

        if user not in admins and user != permitted_user:
            print UNAUTHORISED.format(user)
            return False
    except uqauth.Redirected:
        return False
    else:
        return True


def main():
    # Check the user's privileges first
    if not admin_init():
        return

    form = cgi.FieldStorage(keep_blank_values=True)

    message = None
    if os.environ.get('REQUEST_METHOD') == 'POST':
        action = form.getvalue('action')
        if action not in ACTIONS:
            message = ('alert-danger', 'Action unknown or not specified.')
        else:
            try:
                message = ACTIONS[action](form)
            except StopOutput:
                return
            except Exception as e:
                message = ('alert-danger', 'Encountered error:\n' +
                           type(e).__name__ + ': ' + str(e))

    print "Content-Type: text/html\n"
    query = form.getvalue('query', '')
    enrol_filter = form.getvalue('enrol_filter', support.ENROLLED)
    sort = form.getvalue('sort', 'id')
    reverse = sort.endswith('_reverse')
    users = support.get_users(query, enrol_filter, get_sort_key(sort), reverse)
    user_data = zip(users, [summarise_progress(u.id) for u in users])

    data = {
            'user_data': user_data,
            'query': query,
            'enrol_filter': enrol_filter,
            'sort': sort,
            'message': message,
           }

    try:
        print(Template(filename="./templates/users.html").render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()
