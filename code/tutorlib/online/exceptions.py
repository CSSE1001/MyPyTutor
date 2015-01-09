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


class NullResponse(Exception):
    """
    An exception that represents a null response.

    This is used for error-like conditions which are nevertheless possible in
    the course of normal operation (ie, are not exceptional).
    For example, an attempt to get information on an answer that doesn't exist
    will raise a NullResponse.

    """
    pass
