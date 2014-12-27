class StudentTestError(Exception):
    pass


def indent(text, spaces=4):
    return '\n'.join(' '*spaces + line for line in text.splitlines())


def trim_indentation(text):
    lines = [line for line in text.splitlines() if line.strip()]

    # TODO hacky atm, dunno if it'll work with tabs
    indents = [len(line) - len(line.lstrip()) for line in lines]
    ind = min(indents)

    unindented_text = '\n'.join(line[ind:] for line in text.splitlines())
    return unindented_text + ('\n' if text.splitlines()[-1] == '\n' else '')


def inject_to_module(module, name, value):
    existing_value = getattr(module, name, None)
    assert existing_value is None or existing_value == value, \
            'Name {} already exists in module {}'.format(name, module)
    setattr(module, name, value)


def remove_from_module(module, name):
    assert getattr(module, name, None) is not None, \
            'Cannot remove non-existent name {} from module {}'.format(
                name, module
            )
    delattr(module, name)


def construct_header_message(inner_message):
    lines = inner_message.splitlines()
    if not lines:
        return ''

    first_line = lines[0]
    header = '-'*len(first_line)
    message = '{0}\n{1}\n{0}\n'.format(header, inner_message)
    return message
