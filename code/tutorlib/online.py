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

import urllib.request
import urllib.parse
import html.parser
import http.client
import http.cookiejar
import json
import sys
import tkinter as tk
import tkinter.messagebox

LOGIN_DOMAIN = 'auth.uq.edu.au'
LOGOUT_URL = 'http://api.uqcloud.net/logout'
SERVER = 'http://csse1001.uqcloud.net/cgi-bin/mpt3/mpt_cgi.py'


class AuthError(Exception):
    """An exception representing login failures.
    This usually means that the user has cancelled a login attempt.
    """
    pass


class BadResponse(Exception):
    """An exception representing invalid responses from the web server.
    These errors should not normally occur, and should be reported to the
    maintainer as a bug.
    """
    pass


class RequestError(Exception):
    """An exception representing errors returned by the web server.
    These errors occur when the request could not be satisfied for some reason.
    """
    pass


def strip_header(text):
    MPT_HEADER = 'mypytutor>>>'
    ERROR_HEADER = 'mypytutor_error>>>'
    if text.startswith(MPT_HEADER):
        return text[len(MPT_HEADER):]
    elif text.startswith(ERROR_HEADER):
        raise RequestError(text[len(ERROR_HEADER):])
    else:
        raise BadResponse("Invalid response from server: {!r}"
                          .format(text[:len(MPT_HEADER)] + '...'
                                  if len(text) > len(MPT_HEADER)+3 else text))


class FormParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._forms = []
        self._this_form = None

    def handle_starttag(self, tag, attrs):
        if tag == 'form':
            self._this_form = []
            self._forms.append((dict(attrs), self._this_form))

        if tag == 'input' and self._this_form is not None:
            self._this_form.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag == 'form':
            self._this_form = None

    def get_forms(self):
        return self._forms

    @classmethod
    def forms(cls, text):
        """Return a list of all forms in the given HTML text.

        Each entry in the list is a pair (form, inputs), where `form` is a
        dictionary of attributes on the <form> tag, and `inputs` is a list of
        attribute dictionaries on the <input> tags.
        """
        parser = cls()
        parser.feed(text)
        return parser.get_forms()

    @classmethod
    def get_auth_form(cls, text):
        """Extract details of a login form from auth.uq.edu.au, given the HTML
        text.

        Return a pair (action, data), where `action` is the action attribute
        of the <form> tag, and `data` is a dictionary of existing name/value
        attributes for each <input> tag.

        If the form doesn't look as expected, a BadResponse will be raised.
        """
        # Find the login form, if there is one
        forms = [f for f in cls.forms(text) if f[0].get('name') == 'f']
        if len(forms) != 1:
            raise BadResponse("Error parsing login form: no login form found")
        form = forms[0]

        # Get the 'name' and 'value' attributes already in the form
        data = {attrs['name']: attrs.get('value', '')
                for attrs in form[1] if 'name' in attrs}
        if 'username' not in data or 'password' not in data:
            raise BadResponse("Error parsing login form: form has no username/password field")
        return (form[0]['action'], data)

    @classmethod
    def get_consume_form(cls, text):
        """Extract details of the form to redirect to api.uqcloud.net/saml/consume.

        Return a pair (action, data) as with the get_auth_form method.
        If the form doesn't look as expected, a BadResponse will be raised.
        """
        # Find the form, if there is one
        forms = [f for f in cls.forms(text)
                 if f[0].get('action') == 'https://api.uqcloud.net/saml/consume']
        if len(forms) != 1:
            raise BadResponse("Error parsing login form: no form to /saml/consume")
        form = forms[0]

        # Get the name/values out of the response.
        data = {attrs['name']: attrs.get('value', '')
                for attrs in form[1] if 'name' in attrs}
        return (form[0]['action'], data)


class LoginDialog(tk.Toplevel):
    """Tkinter dialog box for a log in form.
    """
    def __init__(self, callback, title="Login"):
        """Constructor.
        The callback should accept two parameters, a username and a password,
        and should return True if they are valid, and False otherwise.
        """
        super().__init__(bd=5)
        self.callback = callback

        # Set window properties
        self.title(title)
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        self.geometry("+%d+%d" % (x+20, y+20))
        self.resizable(height=False, width=False)
        self.transient(self.master)

        # Set bindings
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.bind('<Escape>', lambda e: self.cancel())
        self.bind('<Return>', lambda e: self.submit())

        # Create widgets
        userframe = tk.Frame(self)
        userframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        tk.Label(userframe, text='Username: ') \
            .pack(side=tk.LEFT, anchor=tk.W, expand=True)
        self.user = tk.Entry(userframe, width=20)
        self.user.pack(side=tk.LEFT)

        passframe = tk.Frame(self)
        passframe.pack(side=tk.TOP, expand=True, fill=tk.X)
        tk.Label(passframe, text='Password: ') \
            .pack(side=tk.LEFT, anchor=tk.W, expand=True)
        self.password = tk.Entry(passframe, width=20, show="*")
        self.password.pack(side=tk.LEFT)

        frameButtons = tk.Frame(self)
        frameButtons.pack(side=tk.TOP)
        tk.Button(frameButtons, text='Submit', command=self.submit) \
            .pack(side=tk.LEFT, expand=True)
        tk.Button(frameButtons, text='Cancel', command=self.cancel) \
            .pack(side=tk.LEFT, expand=True)

        self.user.focus_set()
        self.grab_set()
        self.wait_visibility()
        self.wait_window()

    def cancel(self):
        self.destroy()

    def submit(self):
        user = self.user.get().strip()
        password = self.password.get()
        success = self.callback(user, password)
        if success:
            self.destroy()
        else:
            tkinter.messagebox.showerror('Login Error',
                                         'Incorrect user name or password')
            self.password.delete(0, tk.END)


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

    def __init__(self, url, listener):
        """Constructor.
        `url` is the location of the MyPyTutor server.
        `listener` is a callback method. This method will get called when the
        user logs in or out, so that the view can update accordingly.
        """
        self._url = url
        self._callback = listener
        self._user = None
        self._opener = make_opener()

    def user_info(self):
        return self._user

    def is_logged_in(self):
        return self._user is not None

    def login(self):
        """Log in to the MyPyTutor server.

        If the credentials are valid, a cookie will be set automatically.
        If the credentials are invalid, prompt the user to retry.
        If the user cancels the login attempt, raise an AuthError.

        Precondition: the form is the standard auth.uq.edu.au login form.
        """
        # Ask for the user's information.
        data = {'action': 'userinfo'}
        url = self._url + '?' + urllib.parse.urlencode(data)
        response = self._opener.open(url)
        text = response.read().decode('utf8')

        def set_details(text):
            # Get the user's details out of the server's response.
            self._user = json.loads(strip_header(text))
            self._callback()

        # If we didn't get redirected to the login form, we're already in.
        if urllib.parse.urlsplit(response.geturl()).netloc != LOGIN_DOMAIN:
            set_details(text)
            tkinter.messagebox.showerror('Login Error',
                "You are already logged in as {}.".format(self._user['user']))
            return

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
            response2 = self._opener.open(form_url, form_data)

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
            response3 = self._opener.open(form_url, form_data)
            text3 = response3.read().decode('utf8')
            set_details(text3)

            # The login was successful
            return True

        LoginDialog(submit_login)
        if not self.is_logged_in():
            raise AuthError("Not logged in.")

    def logout(self):
        """Log out of the system."""
        self._opener.open(LOGOUT_URL)
        self._user = None
        self._callback()

    def _request(self, url, data):
        """Send an HTTP request to the given url with the given data.
        If data is None, send a GET request, otherwise a POST request.

        Return the text of the response, with the MyPyTutor header stripped,
        or raise a RequestError if the server doesn't like your request.

        If the user is not logged in, prompt them to log in. If they fail to
        log in, show an error message box.
        """
        try:
            response = self._opener.open(url, data)
            if urllib.parse.urlsplit(response.geturl()).netloc == LOGIN_DOMAIN:
                # The user needs to log in
                self.login()
                response = self._opener.open(url, data)
            text = response.read().decode('utf8')
            return strip_header(text)

        except AuthError as e:
            print("You need to be logged in to do that.", file=sys.stderr)
        except http.client.HTTPException as e:
            print("Connection Error. Check your network connection and try "
                  "again.\n({})".format(type(e).__name__), file=sys.stderr)
        except BadResponse as e:
            print("Unexpected error: please report to maintainer.\n"
                  "Details: {}".format(type(e).__name__, e), file=sys.stderr)

    def post(self, data):
        """Send an HTTP POST request to the server."""
        data = urllib.parse.urlencode(data).encode('ascii')
        return self._request(self._url, data)

    def get(self, data):
        """Send an HTTP GET request to the server."""
        url = self._url + '?' + urllib.parse.urlencode(data)
        return self._request(url, None)


if __name__ == '__main__':
    mgr = SessionManager(SERVER, lambda: print("Listen!"))
    print(mgr.get({'action': 'userinfo'}))
