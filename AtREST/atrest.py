# Only import if we use this class to get password. Creds should probably come
# from elsewhere though.
# from getpass import (
#      getpass,
# )
import logging

from PythonConfluenceAPI import ConfluenceAPI

# TODO: security on password. even if getpass is used to get the password (so
#       it isn't echoed when entered), when used to initialize the REST API,
#       it is stored in that object (and is accessible in plain text via
#       APIManager.__api.password). This could theoretically cause problems in
#       a notebook or other interactive environment where objects are
#       inspectable when running. Additionally, the interface uses
#       HTTPBasicAuth (in requests library), so if not used over https,
#       everything is sent in plaintext over the wire...
# TODO: Any method that results in a call to the REST API via the  __api object
#       will cause HTTP Errors of various types when params are bad (e.g. if
#       the password is not right, a 401 Unauthorized will be returned). These
#       should be handled gracefully (decorator for httperror handling?)
# TODO: Move this out to a file/package
# TODO: Make configurable from config file

# TODO: move this to init of APIManager?
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

def requires_api(wrapped_func):
    """
    Decorator for checking api initialization status before allowing a
    decorated method to be called.
    """
    from functools import wraps
    @wraps(wrapped_func)
    def wrapper(self, *args, **kwargs):
        # TODO: check to make sure the status property exists on the object
        #       first? (i.e. are we decorating a method of the APIManager)
        is_initialized, status_msg = self.status
        if is_initialized:
            res = wrapped_func(self, *args, **kwargs)
            if res is not None:
                return res
        else:
            logging.error(
                'Cannot execute %s. REST API has not been initialized.',
                wrapped_func
            )
    return wrapper

class APIManager():
    """
    Class wrapping the PythonConfluenceAPI.ConfluenceAPI. Provides methods for
    common operations.
    """

    # Connection param keys
    USERNAME = 'username'
    PASSWORD = 'password'
    APIURL = 'apiurl'

    def __init__(self, *args, **kwargs):
        self.__api = None

    @property
    def api(self):
        """
        Wrapped API property getter
        """
        #TODO: THIS IS JUST FOR TESTING. REMOVE IT. TOO MUCH INFO IS AVAILABLE
        #      TO INTERACTIVE ENVIRONMENTS WHEN THIS IS EXPOSED (E.G.
        #      PASSWORDS)
        return self.__api

    @property
    def status(self):
        """
        status property getter. return tuple of (bool, msg) where bool is True
        if the api is initialized and False otherwise, and msg is a string
        status message.
        """
        # TODO: rename property to reflect a tuple is returned?
        status = (False, 'API Not Initialized')
        if self.__api is not None:
            # initialization must have succeeded, so set status as good
            status = (True, 'API Initialized!')
        return status

    def init_api(self, **kwargs):
        """
        Initialize the confluence REST API interface using the credentials
        passed in. This *does not* actually connect, just creates the object.
        """
        # TODO: Error check the values before initializing
        if self.__check_api_params(**kwargs):
            # NOTE: Initialization can succeed with values that don't work (
            #       e.g. a bad password).
            self.__api = ConfluenceAPI(
                kwargs[self.USERNAME],
                kwargs[self.PASSWORD],
                kwargs[self.APIURL]
            )
        else:
            # TODO: better info. what parameter is missing?
            logging.error(
                'Cannot initialize REST API object. A required parameter is ' \
                'missing'
            )

    def __check_api_params(self, **kwargs):
        """
        Check the connection params for validity. At a minimum, make sure they
        exist as expected.
        """
        # TODO: python3 only below, is problem?
        # TODO: better error checks than existance of keys?
        return set((
            self.USERNAME,
            self.PASSWORD,
            self.APIURL
        )) <= kwargs.keys()

    @requires_api
    def recent_content(self):
        """
        Returns the recent Confluence content available to the user set in the
        REST API object. Used mostly for testing connection worked right now.
        """
        # TODO: support all the params the api's get_content method allows
        logging.info('Calling get_content')
        cntnt = self.__api.get_content()
        logging.info('Got %s', cntnt)
        return cntnt
