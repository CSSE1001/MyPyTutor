#!/usr/bin/env python
# A CGI script to run the administrator interface

import cgi
import os

from mako.template import Template
from mako import exceptions

import support
import uqauth

# Whitelisted users with access to the admin site
ADMINS = ['uqprobin']

# Temporary, for development/debugging purposes
ADMINS.extend(['uqspurdo', 'uqjgaten'])

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

# Each action should take a username as input and return one of {0, 1} or
# {False, True} depending on whether the action was successful.
ACTIONS = {
           'enrol': lambda username: support.set_user_enrolment(username, True),
           'unenrol': lambda username: support.set_user_enrolment(username, False),
          }


def get_sort_key(sort):
    if sort in ('id', 'id_reverse'):
        return lambda user: user.id
    if sort in ('name', 'name_reverse'):
        return lambda user: (user.name.lower(), user.id)
    if sort in ('email', 'email_reverse'):
        return lambda user: user.email
    return None


def main():
    # Check the user's privileges first
    try:
        user = uqauth.get_user()
        if user not in ADMINS:
            print UNAUTHORISED.format(user)
            return
    except uqauth.Redirected:
        return
    else:
        print "Content-Type: text/html\n"

    form = cgi.FieldStorage(keep_blank_values=True)

    message = None
    if os.environ.get('REQUEST_METHOD') == 'POST':
        action = form.getvalue('action')
        selected_users = form.getlist('selected_user')
        if action not in ACTIONS:
            message = ('alert-danger', 'Action unknown or not specified.')
        elif selected_users:
            count = sum(ACTIONS[action](u) for u in selected_users)
            if count == 0:
                message = ('alert-warning', '0 users modified.')
            elif count < len(selected_users):
                message = ('alert-success', '{} users modified, {} unchanged.'
                           .format(count, len(selected_users) - count))
            else:
                message = ('alert-success', '{} users modified.'
                           .format(count))
        else:
            message = ('alert-warning', 'No users selected.')


    query = form.getvalue('query', '')
    enrol_filter = form.getvalue('enrol_filter', support.ALL)  # TODO: change to support.ENROLLED later
    sort = form.getvalue('sort', 'id')
    reverse = sort.endswith('_reverse')
    users = support.get_users(query, enrol_filter, get_sort_key(sort), reverse)

    data = {
            'users': users,
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
