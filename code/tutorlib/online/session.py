## A Python Tutorial System
## Copyright (C) 2009,2010  Peter Robinson <pjr@itee.uq.edu.au>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.


# Functionality and dialog windows for logging in and communicating with
# the online interface.

# Interface:
#   >>> manager = SessionManager(SERVER, callback)
#   >>> manager.post(data)
#   >>> manager.get(data)
# These methods return a string with the response, or raise a RequestError if
# there was something wrong with the request.

import http.cookiejar
import http.client
import json
import urllib.parse
import urllib.request

from tutorlib.gui.dialogs.login import LoginDialog
import tutorlib.utils.messagebox as tkmessagebox
from tutorlib.online.exceptions import AuthError, BadResponse, RequestError
from tutorlib.online.parser import FormParser, strip_header


LOGIN_DOMAIN = 'auth.uq.edu.au'
LOGOUT_URL = 'http://api.uqcloud.net/logout'
SERVER = 'http://csse1001.uqcloud.net/cgi-bin/mpt3/mpt_cgi.py'


def make_opener():
    """Make a URL opener with cookies enabled, and proxies disabled."""
    cookiejar = http.cookiejar.CookieJar()
    proxy_handler = urllib.request.ProxyHandler(proxies={})
    cookie_processor = urllib.request.HTTPCookieProcessor(cookiejar=cookiejar)
    opener = urllib.request.build_opener(cookie_processor, proxy_handler)
    return opener


class SessionManager:
    """A class to manage login sessions, as well as sending/receiving data from
    the web server."""

    def __init__(self, url=SERVER, listener=None):
        """Constructor.
        `url` is the location of the MyPyTutor server.
        `listener` is a callback method. This method will get called when the
        user logs in or out, so that the view can update accordingly.
        """
        if listener is None:
            listener = lambda: None

        self._url = url
        self._callback = listener
        self._user = None
        self._opener = make_opener()

    def user_info(self):
        return self._user

    def is_logged_in(self):
        return self._user is not None

    def login(self, username=None, password=None):
        """Log in to the MyPyTutor server.

        If the credentials are valid, a cookie will be set automatically.
        If the credentials are invalid, prompt the user to retry.
        If the user cancels the login attempt, raise an AuthError.

        Optionally, a username and password may be provided to this method.
        In this case, no GUI elements will be displayed.

        Precondition: the form is the standard auth.uq.edu.au login form.
        """
        assert (username is None) + (password is None) in (0, 2)

        # Ask for the user's information.
        data = {'action': 'userinfo'}
        url = self._url + '?' + urllib.parse.urlencode(data)
        response = self._open(url)
        text = response.read().decode('utf8')

        def set_details(text):
            # Get the user's details out of the server's response.
            self._user = json.loads(strip_header(text))
            self._callback()

        # If we didn't get redirected to the login form, we're already in.
        if urllib.parse.urlsplit(response.geturl()).netloc != LOGIN_DOMAIN:
            set_details(text)

            if username is None:
                tkmessagebox.showerror(
                    'Login Error',
                    "You are already logged in as {}.".format(
                        self._user['user']
                    )
                )
            return True

        # Construct a callback for the login dialog box.
        def submit_login(username, password):
            """Given a username and password, attempt to submit the login
            form. Return True if it succeeded.
            """
            # Extract the login form.
            action, form_data = FormParser.get_auth_form(text)

            # Put the user's credentials into the form
            form_data['username'] = username
            form_data['password'] = password

            # Submit the form.
            form_url = urllib.parse.urljoin(response.geturl(), action)
            form_data = urllib.parse.urlencode(form_data).encode('ascii')
            response2 = self._open(form_url, form_data)

            # Get the HTML text in the response.
            text2 = response2.read().decode('utf8')

            # If there is a login form in the response, the user's credentials are invalid.
            if any(f[0].get('name') == 'f' for f in FormParser.forms(text2)):
                return False

            # There is one more form to automatically submit.
            action, form_data = FormParser.get_consume_form(text2)
            form_url = urllib.parse.urljoin(response2.geturl(), action)
            form_data = urllib.parse.urlencode(form_data).encode('ascii')

            # The next response should contain the information originally requested.
            response3 = self._open(form_url, form_data)
            text3 = response3.read().decode('utf8')
            set_details(text3)

            return self.is_logged_in()

        if username is None:
            LoginDialog(None, submit_login)
        else:
            submit_login(username, password)

        # regardless of whether the user cancelled or was successful, what we
        # want to return is whether they are logged in right now
        return self.is_logged_in()

    def logout(self):
        """Log out of the system."""
        self._open(LOGOUT_URL)
        self._user = None
        self._callback()

    def _open(self, url, data=None):
        try:
            return self._opener.open(url, data)
        except AuthError as e:
            raise  # just to indicate that this is a possible error
        except (http.client.HTTPException, urllib.request.URLError) as e:
            raise RequestError(
                'Connection Error.  '
                'Check your network connection and try again.'
            ) from e
        except BadResponse as e:
            raise RequestError(
                'Unexpected Error.  '
                'Please report to maintainer.'
            ) from e

    def _request(self, url, data):
        """Send an HTTP request to the given url with the given data.
        If data is None, send a GET request, otherwise a POST request.

        Return the text of the response, with the MyPyTutor header stripped,
        or raise a RequestError if the server doesn't like your request, or
        an AuthError if the user is not logged on.

        If the user is not logged in, prompt them to log in. If they fail to
        log in, show an error message box.
        """
        response = self._open(url, data)
        if urllib.parse.urlsplit(response.geturl()).netloc == LOGIN_DOMAIN:
            # The user needs to log in
            self.login()
            response = self._open(url, data)
        text = response.read().decode('utf8')
        return strip_header(text)

    def post(self, data):
        """Send an HTTP POST request to the server."""
        data = urllib.parse.urlencode(data).encode('ascii')
        return self._request(self._url, data)

    def get(self, data):
        """Send an HTTP GET request to the server."""
        url = self._url + '?' + urllib.parse.urlencode(data)
        return self._request(url, None)
