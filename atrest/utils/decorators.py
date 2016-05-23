import logging
from functools import wraps

from requests import (
    HTTPError,
)


def logs_httperror(wrapped_func):
    """
    Decorator for generic handling of HTTPErrors for methods that can throw
    them. Many of the PythonConfluenceAPI methods can for example.

    NOTE: This just logs the error and arguments to the function. This could be
          extended to having an error handler passed in as well, or avoided
          all together for snazzy custom handling, but for now this is
          sufficient. During usage/implementation, this may change. Many of the
          HTTPErrors that may occur are ok to just be printed (e.g. a 404
          because a space doesn't exist when using get_content to check for the
          existence of the space), but some will possibly need better handling
          (e.g. a 401 due to bad credentials).
    """
    @wraps(wrapped_func)
    def wrapper(self, *args, **kwargs):
        try:
            return wrapped_func(self, *args, **kwargs)
        except HTTPError as e:
            # TODO: log status code specific stuff like not found vs no
            #       permission to view/perform operation
            logging.error(
                'HTTPError %s caught when calling %s',
                e, wrapped_func
            )
            logging.error(
                '\t arguments (self, *args, **kwargs): %s, %s, %s',
                self, args, kwargs
            )
    return wrapper

def debug_log_call(log_args=False, log_kwargs=False):
    """
    Decorator to log calls to a method/function, logging the callable and the
    arguments passed to it.
    """
    def decorator_wrapper(wrapped_func):
        @wraps(wrapped_func)
        def wrapper(self, *args, **kwargs):
            logging.debug('debug_log_call: Calling %s ', wrapped_func.__name__)
            if log_args:
                logging.debug('\targs: %s ', args)
            if log_kwargs:
                logging.debug('\tkwargs: %s ', kwargs)
            return wrapped_func(self, *args, **kwargs)
        return wrapper
    return decorator_wrapper
