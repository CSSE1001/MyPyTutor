import sys
import urllib.parse
import urllib.request
import webbrowser

from tutorlib.interface.support import simple_hash
from tutorlib.online.exceptions import AuthError, RequestError
from tutorlib.online.session import SessionManager


VISUALISER_URL = 'http://csse1001.uqcloud.net/opt/visualize.html#code={code}'


# TODO: this will need to wait for a proper refactor until Jackson and I have
# TODO: worked out how to structure this
class WebAPI():
    def __init__(self):
        self.url = None
        self.session_manager = SessionManager()

    @property
    def is_logged_in(self):
        return self.session_manager.is_logged_in()

    @property
    def user(self):
        if not self.is_logged_in:
            return None

        user_info = self.session_manager.user_info()
        return user_info['user']

    def login(self):
        # LoginManager raises on failure
        try:
            self.session_manager.login()
            return True
        except AuthError:
            return False

    def logout(self):
        if self.is_logged_in:
            self.session_manager.logout()

    # visualiser
    def visualise(self, code_text):
        # format is url (percent) encoded, except spaces are replaced by +
        encoded_text = urllib.parse.quote(code_text, ' ').replace(' ', '+')
        url = VISUALISER_URL.format(code=encoded_text)

        # just open it in the browser
        webbrowser.open(url)

    # general web communictions
    def get_tut_zipfile(self):
        values = {'action': 'get_tut_zip_file'}
        try:
            result = self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return

        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "tutzip.zip")
            return "tutzip.zip"
        except Exception as e:
            print(str(e))
            return None

    def get_mpt34(self):
        values = {'action': 'get_mpt34'}
        try:
            result = self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return

        try:
            urlobj = urllib.request.URLopener({})
            urlobj.retrieve(result.strip(), "mpt34.zip")
            return "mpt34.zip"
        except:
            return None

    def get_version(self):
        values = {'action': 'get_version'}
        try:
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)

    def upload_answer(self, tutorial, code):
        try:
            values = {
                      'action': 'upload',
                      'problem_name': tutorial.name,
                      'code': code,
                     }
            result = self.session_manager.post(values)
            return result.startswith('OK')
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return False

    def download_answer(self):
        try:
            values = {
                      'action': 'download',
                      'problem_name': self.tutorial.name,
                     }
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return False

    def submit_answer(self, code):
        try:
            tut_id = self.data.get('ID')  # TODO: work out what ID is and then replace this
            values = {
                      'action': 'submit',
                      'tut_id': tut_id,
                      'tut_id_crypt': simple_hash(tut_id + self.user),
                      'tut_check_num': self.num_checks,
                      'code': code,
                     }
            return self.session_manager.post(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return None

    def show_submit(self):
        values = {'action': 'show'}
        try:
            return self.session_manager.get(values)
        except RequestError as e:
            print(str(e), file=sys.stderr)
            return None
