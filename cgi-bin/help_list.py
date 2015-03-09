#!/usr/bin/env python

import cgi
from mako import exceptions
from mako.template import Template
import os

from admin import TUTORS, UNAUTHORISED
from progress import TZ_DELTA  # hacky workaround
import support
import uqauth


def main():
    try:
        user = uqauth.get_user()
    except uqauth.Redirected:
        return

    # two sets of possibilities
    # (1) the help list (need to be a tutor)
    #       (a) viewing the list
    #       (b) submitting the form (eg, deleting an entry)
    # (2) asking for help (as a student)
    #       (a) for the first time (no message query param)
    #       (b) submitting the form
    form = cgi.FieldStorage(keep_blank_values=True)

    view_list = 'view' in form
    if view_list and user not in TUTORS:
        print UNAUTHORISED.format(user)
        return

    print "Content-Type: text/html\n"

    data = {}

    if view_list:
        template = Template(filename="./templates/help_list.html")

        # make our changes if the form was submitted
        if os.environ.get('REQUEST_METHOD') == 'POST' and 'mark_as' in form:
            user = form.getvalue('username')
            status = form.getvalue('mark_as')

            support.set_help_request_status(user, status)

        help_list = sorted(
            support.get_help_list(), key=lambda hi: hi.timestamp
        )

        data['date_offset'] = TZ_DELTA  # hacky workaround
        data['help_list'] = help_list
        data['open_index'] = -1
    else:
        template = Template(filename='./templates/help_request.html')

        data['user'] = user

        message = form.getvalue('message')
        traceback = form.getvalue('traceback')

        if os.environ.get('REQUEST_METHOD') == 'POST' \
                and 'message' is not None:
            info = uqauth.get_user_info()
            name = info.get('name', '')

            support.log_help_request(user, name, message, traceback)

            data['alert_message'] = (
                'alert-success', 'Your help request has been logged'
            )

        pending_request = support.get_pending_help_request(user)
        data['has_pending'] = pending_request is not None
        data['queue_position'] = None

        if pending_request is not None:
            message = pending_request.message
            traceback = pending_request.traceback

            data['queue_position'] = support.get_position_in_help_queue(user)

        data['message'] = message
        data['traceback'] = traceback

    try:
        print(template.render(**data))
    except:
        print(exceptions.html_error_template().render())


if __name__ == '__main__':
    main()
