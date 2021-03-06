#!/usr/bin/env python

import cgi
import os

from mako.template import Template
from mako import exceptions

from admin import admin_init
from progress import TZ_DELTA  # hacky workaround
import support


def main():
    if not admin_init():
        return

    print "Content-Type: text/html\n"
    form = cgi.FieldStorage(keep_blank_values=True)

    if os.environ.get('REQUEST_METHOD') == 'POST' and 'mark_as' in form:
        # work out which submit button was used
        feedback_user = form.getvalue('feedback_user')
        feedback_id = form.getvalue('feedback_id')
        feedback = support.get_feedback(feedback_user, feedback_id)

        # grab the changed status
        status = form.getvalue('mark_as')

        support.set_feedback_status(feedback, status)

    feedback = support.get_all_feedback()
    feedback.sort(key=lambda f: f.date, reverse=True)

    data = {
        'dateOffset': TZ_DELTA,  # hacky workaround
        'feedback': feedback,
        'openIndex': -1,
    }

    try:
        print(Template(
            filename="./templates/feedback.html",
            output_encoding='utf-8',
            encoding_errors='ignore',
        ).render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()
