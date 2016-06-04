class AtRESTException(Exception):
    """
    Base Exception class for AtREST.
    """
    def __init__(self, value, extra_info=None):
        self.value = value
        self.extra_info = extra_info

    def __str__(self):
        return ''.join([
            repr(self.value),
            (' Extra info: %s' % (self.extra) if self.extra else ''),
        ])

class ClientException(AtRESTException):
    """
    Base Exception class for API clients.
    """
    pass

class ResultsException(ClientException):
    """
    Exception to be raised when REST API results do not meeet expectations.
    E.g. too many/few results returned.
    """
    def __init__(self, value, expected=None, actual=None, extra=None):
        self.value = value
        self.expected = expected
        self.actual = actual
        self.extra = extra

    def __str__(self):
        return ''.join([
            repr(self.value),
            ('\nExpected: %s' % (self.expected) if self.expected else ''),
            ('\nActual: %s' % (self.actual) if self.actual else ''),
            ('\nExtra info: %s' % (self.extra) if self.extra else ''),
        ])
