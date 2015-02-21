#!/usr/bin/env python3

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from getpass import getpass
import os
import sys

from tutorlib.config.namespaces import Namespace
from tutorlib.interface.problems import TutorialPackage
from tutorlib.interface.web_api import WebAPI


def parse_args():
    parser = ArgumentParser()

    parser.add_argument(
        'users',
        metavar='user',
        type=str,
        nargs='+',
        help='The usernames to return results for',
    )
    parser.add_argument(
        '--tutorial_package',
        type=str,
        help='The path to the tutorial package to return results for',
        default='../CSSE1001Tutorials',
    )

    return parser.parse_args()


def get_login_details():
    username = input('Username: ')
    password = getpass()

    return username, password


def get_session():
    api = WebAPI()
    username, password = get_login_details()

    if not api.login(username, password):
        return None

    return api


def get_tutorial_package(path):
    options = Namespace(tut_dir=path, ans_dir='/tmp/notreal')
    return TutorialPackage(os.path.basename(path), options)


def get_results(users, api, tutorial_package):
    def _results_for_user(user):
        return api.get_student_results(user, tutorial_package)

    max_workers = len(users)
    with ThreadPoolExecutor(max_workers) as executor:
        futures = {
            executor.submit(_results_for_user, user): user for user in users
        }

        results = {}

        for future in as_completed(futures):
            user = futures[future]
            results[user] = future.result()

    return results


def write_to_file(results, tutorial_package, filename='results.csv'):
    with open(filename, 'w') as f:
        writer = csv.writer(f)

        # write header row
        row = ['']
        for problem_set in tutorial_package.problem_sets:
            for tutorial in problem_set:
                header = '{} - {} - {}'.format(
                    tutorial_package.name, problem_set.name, tutorial.name
                )
                row.append(header)

        writer.writerow(row)

        # rows are per-user
        for user, user_results in results.items():
            row = [user]

            for problem_set in tutorial_package.problem_sets:
                for tutorial in problem_set:
                    status = user_results[tutorial]
                    row.append(status)

            writer.writerow(row)


def main(users, tutorial_package_path):
    # log in
    api = get_session()
    if api is None:
        sys.stderr.write('Login failed\n')
        return 1

    # load our tutorial package
    tutorial_package = get_tutorial_package(tutorial_package_path)

    # asynchronously get results
    results = get_results(users, api, tutorial_package)

    # write our results out to a file
    write_to_file(results, tutorial_package)

    return 0


# Typical usage would be using a newline-separated students file, eg:
#    cat student_list | xargs ./get_submissions.py


if __name__ == '__main__':
    # grab our arguments
    args = parse_args()

    sys.exit(main(args.users, args.tutorial_package))