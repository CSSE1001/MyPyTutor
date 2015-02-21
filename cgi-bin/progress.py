#!/usr/bin/env python

import uqauth
import support

import datetime


from mako.template import Template
from mako import exceptions

DATE_FORMAT = '%d/%m/%Y %I:%M%p'
TZ_DELTA = datetime.timedelta(hours=10)


def get_submissions():
    """Return a list of submission statistics for the given user."""
    # authenticate the user
    user = uqauth.get_user()

    # get the raw data
    tutorials = support.get_tutorials()
    all_submissions = support.parse_submission_log(user)

    # create a list containing either submission date or None for each tutorial
    submissions = []
    for tut in tutorials:
        sub = [s for s in all_submissions if s.hash == tut.hash]
        submissions.append(sub[0] if sub else None)

    return zip(tutorials, submissions)


def process_tutorial(tutorial, submission):
    if submission is None:
        status = 'unsubmitted'
    elif submission.date <= tutorial.due:
        status = 'submitted'
    elif submission.allow_late:
        status = 'late_ok'
    else:
        status = 'late'

    submit = submission and (submission.date + TZ_DELTA).strftime(DATE_FORMAT)

    return {
        'slug': tutorial.tutorial_name,
        'title': tutorial.tutorial_name.replace('_', ' '),
        'status': status,
        'submit_time': submit,
    }


def main():
    try:
        submissions = get_submissions()
    except uqauth.Redirected:
        return

    print "Content-Type: text/html\n"

    data = {
        'name': 'Change Me',
        'id': 'changeme',
        'user': uqauth.get_user_info(),
        'openIndex': 0
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
                'problems': []
            }

            data['groups'].append(group)

        group['problems'].append(process_tutorial(tutorial, submission))

        if (submission is not None and
                (submission.date <= tutorial.due or submission.allow_late)):
            data['mark'] += 1
        elif submission is not None:
            data['late'] += 1

    data['total'] = len(submissions)

    try:
        print(Template(filename="./templates/progress.html").render(**data))
    except:
        print(exceptions.html_error_template().render())

if __name__ == '__main__':
    main()
