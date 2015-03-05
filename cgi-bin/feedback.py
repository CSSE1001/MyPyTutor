#!/usr/bin/env python

import cgi

from mako.template import Template
from mako import exceptions

from admin import ADMINS, UNAUTHORISED
import support
import uqauth


def main():
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

    feedback = support.get_all_feedback()
    feedback.sort(key=lambda f: f.date)

    data = {
        'feedback': feedback,
        'openIndex': -1,
    }

    try:
        print(Template(filename="./templates/feedback.html").render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()