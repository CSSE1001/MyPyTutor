#!/usr/bin/env python
# A CGI script to run the administrator interface

import cgi

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


def get_users(form):
    query = form['query'].value if 'query' in form else ''
    enrol_filter = (form['enrol_filter'].value
                    if 'enrol_filter' in form else None)
    sort_key = None
    if 'sort' in form:
        sort = form['sort'].value
        if sort == 'id':
            sort_key = lambda u: u.id
        elif sort == 'name':
            sort_key = lambda u: u.name
        elif sort == 'email':
            sort_key = lambda u: u.email

    return support.get_users(query, enrol_filter, sort_key)


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
    users = get_users(form)

    data = {'users': users,}

    try:
        print(Template(filename="./templates/users.html").render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()
