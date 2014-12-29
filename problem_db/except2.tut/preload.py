class InvalidCommand(Exception):
    pass


def validate_input(string):
    """
    validate_input(str) -> (str, [float])

    If string is a valid command, return its name and arguments.
    If string is not a valid command, raise InvalidCommand

    Valid commands:
      add x y
      sub x y
      mul x y
      div x y

    Arguments x and y must be convertable to float.

    """
    # your code here
