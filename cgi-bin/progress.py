#!/usr/bin/env python2.7

import cgi
import datetime
import os

from mako.template import Template
from mako import exceptions

from admin import ADMINS, UNAUTHORISED
import uqauth
import support


DATE_FORMAT = '%d/%m/%Y %I:%M%p'
TZ_DELTA = datetime.timedelta(hours=10)


def get_submissions(user):
    """Return a list of submission statistics for the given user."""
    # get the raw data
    tutorials = support.get_tutorials()
    submissions = support.parse_submission_log(user)
    mappings = support.parse_tutorial_hashes()

    tutorial_submissions = {
        mappings[submission.hash]: submission for submission in submissions
    }
    return zip(tutorials, map(tutorial_submissions.get, tutorials))


def process_tutorial(tutorial, submission):
    if submission is None or submission.date is None:
        status = 'unsubmitted'
    elif submission.date <= tutorial.due:
        status = 'submitted'
    elif submission.allow_late:
        status = 'late_ok'
    else:
        status = 'late'

    submit = (submission and submission.date and
              (submission.date + TZ_DELTA).strftime(DATE_FORMAT))

    return {
        'hash': tutorial.hash,
        'slug': tutorial.tutorial_name,
        'title': tutorial.tutorial_name.replace('_', ' '),
        'status': status,
        'submit_time': submit,
        'has_allow_late': submission is not None and submission.allow_late,
    }

def is_submitted_on_time(tutorial, submissions):
    "Return True if the given tutorial was submitted on time"
    return any(s and s.hash==tutorial and s.date and s.date <= t.due
               for t,s in submissions)


def main():
    try:
        this_user = uqauth.get_user()
    except uqauth.Redirected:
        return

    form = cgi.FieldStorage(keep_blank_values=True)
    is_admin = (this_user in ADMINS and 'noadmin' not in form)

    user = form.getvalue('user', this_user)
    if user != this_user and not this_user in ADMINS:
        print UNAUTHORISED.format(this_user)
        return

    message = None
    if (is_admin and os.environ.get('REQUEST_METHOD') == 'POST' and
            'action' in form):
        before_submissions = get_submissions(user)
        if form.getvalue('action') == 'allow_late':
            action = (lambda tutorial: not is_submitted_on_time(tutorial, before_submissions)
                      and support.set_allow_late(user, tutorial, this_user, True))
        elif form.getvalue('action') == 'disallow_late':
            action = (lambda tutorial: not is_submitted_on_time(tutorial, before_submissions)
                      and support.set_allow_late(user, tutorial, this_user, False))
        else:
            action = None
            message = ('alert-danger', 'Action unknown or not specified.')

        problems = form.getlist('problem')
        if action and problems:
            count = sum(map(action, problems))
            if count == 0:
                message = ('alert-warning', '0 entries modified.')
            elif count < len(problems):
                message = ('alert-success', '{} entries modified, {} unchanged.'
                           .format(count, len(problems)-count))
            else:
                message = ('alert-success', '{} entries modified.'
                           .format(count))
        elif action and not problems:
            message = ('alert-warning', 'No problems specified.')

    user_info = (support.get_user(user) or
                 support.User(user, 'UNKNOWN', 'UNKNOWN', 'not_enrolled'))
    submissions = get_submissions(user)

    print "Content-Type: text/html\n"

    data = {
        'name': 'Change Me',
        'id': 'changeme',
        'user': user_info,
        'openIndex': -1,
        'is_admin': is_admin,
        'message': message,
    };

    # Count the number of on-time or accepted-late submissions the student has made.
    data['mark'] = 0
    data['late'] = 0

    data['groups'] = []
    group = None

    for tutorial, submission in submissions:
        if not group or tutorial.problem_set_name != group['slug']:
            group = {
                'slug': tutorial.problem_set_name,
                'title': tutorial.problem_set_name.replace('_', ' '),
                'due': (tutorial.due + TZ_DELTA).strftime(DATE_FORMAT),
                'problems': [],
                'mark': 0,
                'late': 0,
            }

            data['groups'].append(group)

        tut = process_tutorial(tutorial, submission)
        group['problems'].append(tut)

        if (submission is not None and submission.date is not None and
                (submission.date <= tutorial.due or submission.allow_late)):
            group['mark'] += 1
            data['mark'] += 1
        elif submission is not None and submission.date is not None:
            group['late'] += 1
            data['late'] += 1

    data['total'] = len(submissions)

    try:
        print(Template(filename="./templates/progress.html").render(**data))
    except:
        print(exceptions.html_error_template().render())

if __name__ == '__main__':
    main()
