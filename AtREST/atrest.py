import logging

from PythonConfluenceAPI import (
    ConfluenceAPI,
    all_of,
)

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
# TODO: look at neobunch package (evolution of bunchify). changes a dict to an
#       object that can be accessed via dot notation (instead of with string
#       keys)
# TODO: Make configurable from config file
# TODO: can we configure the api to always return all (or set a pagination
#       limit that does the same thing...)? currently, if limit is an allowed
#       value in a query and it is not set, confluence defaults to 25. If
#       all_of (from the PythonConfluenceAPI package) is used, it does requests
#       (using the default limit per query if not set), which means a bunch
#       of requests potentially.


# TODO: move this to init of APIManager?
# TODO: this may not work in a notebook. see how to configure logging correctly
#       for use there.
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

    # "constants"

    # max results for a query. this is a biggish number that doesn't cause
    # Confluence to bug out (2**32 does for sure).
    # TODO: see if there's a documented limit to this number for Confluence
    MAX_RESULTS = (2**16)*2

    def __init__(self, *args, **kwargs):
        """
        """
        self.__api = None
        self.__query_params = None

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
    def query_params(self):
        """
        Property getter for query parameters.
        """
        # TODO: do we want a setter?
        if self.__query_params is None:
            # TODO: add more as they are found to  be useful
            self.__query_params = {
                'limit': self.MAX_RESULTS,
            }
        return self.__query_params

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
    def recent_content(self, *args, **kwargs):
        """
        Returns the recent Confluence content available to the user set in the
        REST API object. Used mostly for testing connection worked right now.
        """
        # TODO: support all the params the api's get_content method allows
        return self.__api.get_content()

    @requires_api
    def list_space_names(self, *args, **kwargs):
        """
        Returns the info about Confluence spaces available to the user set
        in the REST API object.
        """
        # TODO: support all the params the api's get_spaces method allows
        # TODO: figure out what else about spaces we should return (e.g. id's)
        # TODO: should this be more a "space_info" method that allows filtering
        #       of fields (e.g. only return the names and ids, or just names,
        #       or names and ids and key, etc)?

        # all_of used here to get all the results rather than a paginated set.
        # all_of returns a generator. see the PythonConfluenceAPI code.
        return [
            i['name'] for i in
            all_of(self.__api.get_spaces, **self.query_params)
        ]
