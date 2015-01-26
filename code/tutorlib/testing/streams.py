from contextlib import redirect_stdout
import builtins
import sys
import functools


redirect_stdout = redirect_stdout  # make PEP happy

# redirect_stdin and redirect_stderr are based on redirect_stdout from
# contextlib, and share almost identical code
# see the source code: https://hg.python.org/cpython/file/3.4/Lib/contextlib.py


class redirect_stdin():
    """
    Context manager which redirects stdin.

    Based on the contextlib implementation of redirect_stdout.

    """
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
    """
    Context manager which redirects stderr.

    Based on the contextlib implementation of redirect_stdout.

    """
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


class redirect_input_prompt():
    """
    Context manager which redirects input() prompts away from stdout.
    """
    # This is lots of really bad hacks, because the testing framework gets
    # given a *globals* dict, not a locals dict (despite the name `lcls`)

    def __init__(self, gbls, target=None):
        # get __builtins__.input from gbls, if it exists
        self._real_input = gbls.get('__builtins__', {}).get('input', None)

        self._gbls = gbls
        self._target = target

    def __enter__(self):
        # define a new input function which doesn't use the prompt
        @functools.wraps(builtins.input)
        def _input(prompt=None):
            if prompt is not None and self._target is not None:
                self._target.write(prompt + '\n')
            return builtins.input()

        # set either `__builtins__.input` or `input`
        self._gbls.get('__builtins__', self._gbls)['input'] = _input

    def __exit__(self, exctype, excinst, exctb):
        # if __builtins__.input didn't exist before, then remove it.
        if self._real_input is None:
            self._gbls.get('__builtins__', {'input': None}).pop('input')

        # if it did exist before, then reset it to the original value
        else:
            self._gbls['__builtins__']['input'] = self._real_input
