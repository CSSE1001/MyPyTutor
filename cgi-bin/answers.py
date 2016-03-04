#!/usr/bin/env python2.7

import cgi
from mako.template import Template
from mako import exceptions

from admin import admin_init
import support


def main():
    form = cgi.FieldStorage(keep_blank_values=True)

    user = form.getvalue('user')

    if not admin_init(permitted_user=user):
        return

    print "Content-Type: text/html\n"
    if not all(val in form for val in ('user', 'pset', 'tutorial')):
        print 'Invalid query params'
        return

    problem_set_name = form.getvalue('pset')
    tutorial_name = form.getvalue('tutorial')

    code = support.read_answer(
        user, 'CSSE1001Tutorials', problem_set_name, tutorial_name
    )

    data = {
        'user': user,
        'pset': problem_set_name,
        'tutorial': tutorial_name,
        'code': code,
    }

    try:
        print(Template(
            filename="./templates/answers.html",
            output_encoding='utf-8',
            encoding_errors='ignore',
        ).render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()
