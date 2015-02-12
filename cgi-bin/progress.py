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
    submissions = support.parse_submission_log(user)

    # create a list containing either submission date or None for each tutorial
    submit_times = []
    for tut in tutorials:
        sub = [s for s in submissions if s.hash == tut.hash]
        submit_times.append(sub[0].date + TZ_DELTA if sub else None)

    return zip(tutorials, submit_times)


def process_tutorial(tutorial, submit_time):
    if submit_time is None:
        status = 'unsubmitted'
    # TODO: also check for override-late flag
    elif submit_time <= tutorial.due:
        status = 'submitted'
    else:
        status = 'late'

    due = tutorial.due.strftime(DATE_FORMAT)
    submit = submit_time and submit_time.strftime(DATE_FORMAT)

    return {
        'slug': tutorial.tutorial_name,
        'title': tutorial.tutorial_name.replace('_', ' '),
        'due': due,
        'status': status,
        'submit_time': submit_time,
        'submit': submit
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

    for tutorial, submit_time in submissions:
        if not group or tutorial.problem_set_name != group['slug']:
            group = {
                'slug': tutorial.problem_set_name,
                'title': tutorial.problem_set_name.replace('_', ' '),
                'due': tutorial.due.strftime(DATE_FORMAT),
                'problems': []
            }

            data['groups'].append(group)

        group['problems'].append(process_tutorial(tutorial, submit_time))

        # TODO: also check if is-submitted and override-late flag is set
        if None is not submit_time <= tutorial.due:
            data['mark'] += 1
        elif submit_time is not None:
            data['late'] += 1

    data['total'] = len(submissions)

    try:
        print(Template(filename="./templates/progress.html").render(**data))
    except:
        print(exceptions.html_error_template().render())

if __name__ == '__main__':
    main()
