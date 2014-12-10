from contextlib import redirect_stdout


redirect_stdout = redirect_stdout  # make PEP happy

# redirect_stdin and redirect_stderr are based on redirect_stdout from
# contextlib, and share almost identical code
# see the source code: https://hg.python.org/cpython/file/3.4/Lib/contextlib.py


class redirect_stdin():
    def __init__(self, input_stream):
        self._new_target = input_stream
        # Use list for re-entrancy
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(sys.stdin)
        sys.stdin = self._new_target
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        sys.stdin = self._old_targets.pop()


class redirect_stderr():
    def __init__(self, new_target):
        self._new_target = new_target
        # Use list for re-entrancy
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(sys.stderr)
        sys.stderr = self._new_target
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        sys.stderr = self._old_targets.pop()