class StudentTestError(Exception):
    """
    A generic error encountered in testing the student's code.

    Used when there is no more specific exception available.

    """
    pass


def indent(text, spaces=4):
    """
    Indent each line of the given text by the given number of spaces.

    Args:
      text (str): The text to indent.
      spaces (int, optional): The number of spaces to indent the text by.

    Returns:
      The indented text.

    """
    return '\n'.join(' '*spaces + line for line in text.splitlines())


def trim_indentation(text):
    """
    Trim an equal amount of indentation from each line in the given text.

    This is not guaranteed to work on text which contains tabs.
    It will almost certainly not work on text which mixes spaces and tabs.

    Args:
      text (str): The text to trim the indentation from.

    Returns:
      The trimmed text.
      At least one line of the result will have no leading whitespace.

    """
    lines = [line for line in text.splitlines() if line.strip()]

    ind = min(len(line) - len(line.lstrip()) for line in lines)

    unindented_text = '\n'.join(line[ind:] for line in text.splitlines())
    return unindented_text + ('\n' if text.splitlines()[-1] == '\n' else '')


def inject_to_module(module, name, value):
    """
    Inject the given value into the given module using the given name.

    Args:
      module (module): The module to inject the name into.
      name (str): The name to inject the value for.
      value (object): The value to inject.

    Raises:
      AssertionError: If the given name already exists on the given module,
          and has a different value to that given.

    """
    existing_value = getattr(module, name, None)
    assert existing_value is None or existing_value == value, \
            'Name {} already exists in module {}'.format(name, module)
    setattr(module, name, value)


def remove_from_module(module, name):
    """
    Remove the given name from the given module.

    Args:
      module (module): The module to remove the name from.
      name (str): The name to remove.

    Raises:
      AssertionError: If the given name does not exist on the given module.

    """
    assert getattr(module, name, None) is not None, \
            'Cannot remove non-existent name {} from module {}'.format(
                name, module
            )
    delattr(module, name)


def construct_header_message(inner_message):
    """
    Wrap the given message in dashes.

    Args:
      inner_message (str): The message to wrap.

    Returns:
      The given message, wrapped in dashes.

      The number of dashes used will match the length of the first line.

      Dashes will be inserted before the first and after the last line of
      the input message.

    """
    lines = inner_message.splitlines()
    if not lines:
        return ''

    first_line = lines[0]
    header = '-'*len(first_line)
    message = '{0}\n{1}\n{0}\n'.format(header, inner_message)
    return message
