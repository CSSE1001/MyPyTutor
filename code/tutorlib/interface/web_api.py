import base64
import json
import urllib.parse
import urllib.request
import webbrowser

from tutorlib.online.exceptions import AuthError, RequestError, NullResponse
from tutorlib.online.session import SessionManager


VISUALISER_URL = 'http://csse1001.uqcloud.net/opt/visualize.html#code={code}'


class WebAPIError(Exception):
    def __init__(self, message, details=None):
        self.message = message
        self.details = details


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
            return True

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
        # must be logged in to make a request
        if not self.login():
            raise WebAPIError(
                message='Authentication Error',
                details='You must be logged in to use this feature',
            )

        try:
            return f(values)
        except AuthError as e:
            raise WebAPIError(
                message='Authentication Failure',
                details=str(e),
            ) from e
        except RequestError as e:
            raise WebAPIError(
                message='Could Not Complete Request',
                details=str(e),
            ) from e
        except NullResponse as e:
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
        except Exception as e:
            raise WebAPIError(
                message='Could Not Download File',
                details=str(e),
            ) from e

    def get_tut_zipfile(self):
        values = {
            'action': 'get_tut_zip_file',
        }

        result = self._get(values)
        return self._download(result.strip(), 'tutzip.zip')

    def get_mpt34(self):
        values = {
            'action': 'get_mpt34',
        }

        result = self._get(values)
        return self._download(result.strip(), 'mpt34.zip')

    def get_version(self):
        values = {
            'action': 'get_version',
        }
        return self._get(values)

    def upload_answer(self, tutorial, problem_set, tutorial_package, code):
        values = {
            'action': 'upload',
            'code': code,
            'tutorial_package_name': tutorial_package.name,
            'problem_set_name': problem_set.name,
            'tutorial_name': tutorial.name,
        }

        result = self._post(values)
        return result.startswith('OK')

    def download_answer(self, tutorial, problem_set, tutorial_package):
        values = {
            'action': 'download',
            'tutorial_package_name': tutorial_package.name,
            'problem_set_name': problem_set.name,
            'tutorial_name': tutorial.name,
        }
        return self._get(values)

    def answer_info(self, tutorial, problem_set, tutorial_package):
        values = {
            'action': 'answer_info',
            'tutorial_package_name': tutorial_package.name,
            'problem_set_name': problem_set.name,
            'tutorial_name': tutorial.name,
        }
        response = self._get(values)
        if response is None:
            return None, None

        try:
            d = json.loads(response)
        except ValueError:
            raise WebAPIError(
                message='Invalid Response',
                details='Could not decode response: {}'.format(response),
            )  # do not explicitly chain -- not independently useful to caller

        if 'hash' not in d or 'timestamp' not in d:
            raise WebAPIError(
                message='Invalid Response',
                details='Missing keys on response: {}'.format(response),
            )  # do not explicitly chain -- not independently useful to caller

        answer_hash = base64.b32decode(d['hash'])
        timestamp = d['timestamp']

        return answer_hash, timestamp

    def submit_answer(self, tutorial, code):
        tutorial_hash = base64.b32encode(tutorial.hash)

        values = {
            'action': 'submit',
            'tutorial_hash': tutorial_hash,
            'code': code,
        }
        response = self._post(values)
        if response is None:
            return None

        response = response.strip()
        if response not in ('OK', 'LATE'):
            raise WebAPIError(
                message='Invalid Response',
                details='Unexpected response: {}'.format(response),
            )

        return response == 'OK'

    def get_submissions(self):
        values = {
            'action': 'get_submissions',
        }
        response = self._get(values)

        # parse our response
        try:
            results = json.loads(response)
        except ValueError:
            raise WebAPIError(
                message='Invalid Response',
                details='Could not decode response: {}'.format(response),
            )  # do not explicitly chain -- not independently useful to caller

        # convert from literal strings to builtins
        # TODO: alternative is to have, eg WebAPI.{OK,LATE,MISSING}
        mappings = {
            'OK': True,
            'LATE': False,
            'MISSING': None,
        }

        # TODO: convert mappings
        # TODO: convert hashes to tutorials

