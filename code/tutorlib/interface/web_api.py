import sys
import urllib.parse
import urllib.request
import webbrowser

from tutorlib.interface.support import simple_hash
from tutorlib.online.exceptions import AuthError, RequestError
from tutorlib.online.session import SessionManager


VISUALISER_URL = 'http://csse1001.uqcloud.net/opt/visualize.html#code={code}'


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
        if self.is_logged_in:
            return

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
    def _request(self, f, values):
        try:
            return f(values)
        except (AuthError, RequestError) as e:
            print(e, file=sys.stderr)  # TODO: this print doesn't feel right
            return None

    def _get(self, values):
        return self._request(self.session_manager.get, values)

    def _post(self, values):
        return self._request(self.session_manager.post, values)

    def _download(self, url, filename):
        urlobj = urllib.request.URLopener({})

        try:
            filename, _ = urlobj.retrieve(url, filename=filename)
            return filename
        except Exception:  # could be lots of things; what matters is it failed
            return None

    def get_tut_zipfile(self):
        values = {
            'action': 'get_tut_zip_file',
        }

        result = self._get(values)
        if result is None:
            return None

        return self._download(result.strip(), 'tutzip.zip')

    def get_mpt34(self):
        values = {
            'action': 'get_mpt34',
        }

        result = self._get(values)
        if result is None:
            return None

        return self._download(result.strip(), 'mpt34.zip')

    def get_version(self):
        values = {
            'action': 'get_version',
        }
        return self._get(values)

    def upload_answer(self, tutorial, code):
        values = {
            'action': 'upload',
            'problem_name': tutorial.name,
            'code': code,
        }

        result = self._post(values)
        return result is not None and result.startswith('OK')

    def download_answer(self, tutorial):
        values = {
            'action': 'download',
            'problem_name': tutorial.name,
        }
        return self._get(values)

    def submit_answer(self, code):
        tut_id = self.data.get('ID')  # TODO: work out what ID is and then replace this
        values = {
            'action': 'submit',
            'tut_id': tut_id,
            'tut_id_crypt': simple_hash(tut_id + self.user),
            'tut_check_num': self.num_checks,
            'code': code,
        }
        return self._post(values)

    def show_submissions(self):
        values = {
            'action': 'show',
        }
        return self._get(values)
