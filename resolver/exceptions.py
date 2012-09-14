"""
Exceptions for what can go wrong with a client.
"""


class ClientException(Exception):
    """An exception signalling that the client did something wrong.

    The message is sent to the client.
    """
    pass


class InvalidAction(ClientException):
    def __init__(self):
        super(InvalidAction, self).__init__('invalid action')


class InvalidKey(ClientException):
    def __init__(self):
        super(InvalidKey, self).__init__('invalid key')


class InvalidValue(ClientException):
    def __init__(self):
        super(InvalidValue, self).__init__('invalid value')


class MalformedPub(ClientException):
    def __init__(self):
        super(MalformedPub, self).__init__("malfomred '[key] [value]'")


class KeyNotFound(ClientException):
    def __init__(self):
        super(KeyNotFound, self).__init__('key not found')


class KeyInUse(ClientException):
    def __init__(self):
        super(KeyInUse, self).__init__('key in use')
