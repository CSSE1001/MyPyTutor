#!/usr/bin/env python

import cgi

from mako.template import Template
from mako import exceptions

from admin import admin_init
import support


def main():
    if not admin_init():
        return

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