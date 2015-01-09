import html.parser

from tutorlib.online.exceptions import BadResponse, RequestError, NullResponse


def strip_header(text):
    MPT_HEADER = 'mypytutor>>>'
    ERROR_HEADER = 'mypytutor_error>>>'
    NULL_RESPONSE_HEEADER = 'mypytutor_nullresponse>>>'
    if text.startswith(MPT_HEADER):
        return text[len(MPT_HEADER):]
    elif text.startswith(ERROR_HEADER):
        raise RequestError(text[len(ERROR_HEADER):])
    elif text.startswith(NULL_RESPONSE_HEEADER):
        raise NullResponse(text[len(NULL_RESPONSE_HEEADER):])
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
