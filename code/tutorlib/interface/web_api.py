import urllib.parse
import urllib.request
import webbrowser

from tutorlib.online import AuthError, LoginManager


LOGIN_URL = 'http://csse1001.uqcloud.net/cgi-bin/mpt3/mpt_cgi.py'
VISUALISER_URL = 'http://csse1001.uqcloud.net/opt/visualize.html#code={code}'


# TODO: this will need to wait for a proper refactor until Jackson and I have
# TODO: worked out how to structure this
class WebAPI():
    def __init__(self):
        self.url = None
        self.login_manager = LoginManager(LOGIN_URL, self._manager_callback)

    # user management (login, logout etc) methods
    def _manager_callback(self):
        pass

    @property
    def is_logged_in(self):
        return self.login_manager.is_logged_in()

    @property
    def user(self):
        if not self.is_logged_in:
            return None

        user_info = self.login_manager.user_info()
        return user_info['user']

    def login(self):
        # LoginManager raises on failure
        try:
            self.login_manager.login()
            return True
        except AuthError:
            return False

    def logout(self):
        if self.is_logged_in:
            self.login_manager.logout()

    # visualiser
    def visualise(self, code_text):
        # format is url (percent) encoded, except spaces are replaced by +
        encoded_text = urllib.parse.quote(code_text, ' ').replace(' ', '+')
        url = VISUALISER_URL.format(code=encoded_text)

        # just open it in the browser
        webbrowser.open(url)

    # general web communictions
    def _send_data(self, form_dict):
        if self.url is not None:
            try:
                URL = self.url.strip()
                data = urllib.parse.urlencode(form_dict)
                proxy_handler = urllib.request.ProxyHandler(proxies={})
                request = urllib.request.build_opener(proxy_handler)
                response = request.open(URL, data.encode('ascii'))
                text = response.read().decode('ascii').strip()
                #print text  # debugging
                if text.startswith('mypytutor>>>'):
                    return text[12:]
                else:
                    return '_send_data Exception: Invalid response'
            except Exception as e:
                return '_send_data Exception: '+str(e)

    def get_tut_zipfile(self):
        values = {'action': 'get_tut_zip_file'}
        result = self._send_data(values)
        #print result
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "tutzip.zip")
            return "tutzip.zip"
        except Exception as e:
            print(str(e))
            return None

    def get_mpt27(self):
        values = {'action': 'get_mpt27'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt27.zip")
            return "mpt27.zip"
        except:
            return None

    def get_mpt26(self):
        values = {'action': 'get_mpt26'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt26.zip")
            return "mpt26.zip"
        except:
            return None

    def get_version(self):
        values = {'action': 'get_version'}
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        else:
            return result

    def change_password(self, passwd0, passwd1):
        if passwd0 == '':
            passwd0 = '-'
        values = {'action': 'change_password',
                  'username': self.user,
                  'session_key': self.session_key,
                  'password': passwd0,
                  'password1': passwd1,
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print("You don't appear to be connected.", file=sys.stderr)
            return False
        if result is None:
            return False
        if result.startswith('Error'):
            return False
        else:
            return True

    def upload_answer(self, code):
        result = None
        if self.tutorial is not None:
            values = {'action': 'upload',
                      'username': self.user,
                      'session_key': self.session_key,
                      'problem_name': self.tutorial.name,
                      'code': code,
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return False

        if result is None:
            return False
        return result.startswith('OK')

    def download_answer(self):
        result = None
        if self.tutorial is not None:
            values = {'action': 'download',
                      'username': self.user,
                      'session_key': self.session_key,
                      'problem_name': self.tutorial.name,
                      }
            result = self._send_data(values)
            if '_send_data Exception' in result:
                print("You don't appear to be connected.", file=sys.stderr)
                return None
        return result

    def submit_answer(self, code):
        self.run_tests(code)
        result = None
        if self.tutorial is not None:
            if self.is_solved():
                tut_id = self.data.get('ID')  # TODO: work out what ID is and then replace this
                values = {'action': 'submit',
                          'username': self.user,
                          'session_key': self.session_key,
                          'tut_id': tut_id,
                          'tut_id_crypt': simple_hash(tut_id + self.user),
                          'tut_check_num': self.num_checks,
                          'code': code,
                          }
                result = self._send_data(values)
                if '_send_data Exception' in result:
                    print("You don't appear to be connected.", file=sys.stderr)
                    return None
            else:
                result = 'Error: You can only submit when your answer is correct.'
        return result

    def show_submit(self):
        result = None
        values = {'action': 'show',
                  'username': self.user,
                  'session_key': self.session_key,
                  }
        result = self._send_data(values)
        if '_send_data Exception' in result:
            print(result[10:], file=sys.stderr)
            print("You don't appear to be connected.", file=sys.stderr)
            return None
        return result
