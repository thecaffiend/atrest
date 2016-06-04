import logging
from functools import wraps

from requests import (
    HTTPError,
)

# TODO: give a way to specify different handling for each type of error. allow
#       specification of those that should be propagated as well.
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
            self.log.debug('debug_log_call: Calling %s ', wrapped_func.__name__)
            if log_args:
                self.log.debug('\targs: %s ', args)
            if log_kwargs:
                self.log.debug('\tkwargs: %s ', kwargs)
            return wrapped_func(self, *args, **kwargs)
        return wrapper
    return decorator_wrapper

def makes_kwarg_dict(ignore_keys=None, sub_keys=None):
    """
    Decorator to make a dict of explicit keyword arguments of a method or
    function. This dict wil be available in the method as method.keyword_dict.
    If ignore_keys list is given, those keys will be omitted from the result.
    If a sub_keys dict is given, it should map explicit keyword keys to ones
    that should be subsituted in the resuling dict (the value will remain what
    was) passed in.

    e.g.:

    @makes_kwarg_dict(ignore_keys=['a'], sub_keys={'c': 'c_sub'})
    def some_method(self, a, b, c=None, d=None, e=True):
        # there will be a dict self.some_method.keyword_dict containing
        # {'sub_c': c, 'd': d}.

    NOTE: This is a convenience for some wrapped api methods, and can lead to
          hard to maintain/read code. Please don't abuse.
    """
    def decorator_wrapper(wrapped_func):
        @wraps(wrapped_func)
        def wrapper(self, *args, **kwargs):
            wrapper.keyword_dict = {}
            # gets substitute keys: given a key k and dict d, return k if d is
            # None, d[k] if there, else k.
            ignore = ignore_keys or []
            get_key = lambda k, d: d.get(k, k) if d else k
            matched = [(k, v) for k, v in kwargs.items() if k not in ignore]
            wrapper.keyword_dict = {get_key(k, sub_keys): v for k, v in matched}
            return wrapped_func(self, *args, **kwargs)
        return wrapper
    return decorator_wrapper
