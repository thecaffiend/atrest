import logging

from functools import wraps

from requests import (
    HTTPError,
)

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
# TODO: provide a set of supported operations (check content existence, copy
#       content, etc), and a mechanism to add extension operations for users.
#       these should either be composed of supported operations (with some kind
#       of DSL to compose), or via a user plugin/script that extends some kind
#       of ExtensionOperationBase class. Experiment.
# TODO: decorator for checking required keys for a call (like a call that
#       creates new content having the PythonConfluenceAPI's
#       NEW_CONTENT_REQUIRED_KEYS defined)?
# TODO: look at neobunch package (evolution of bunchify). changes a dict to an
#       object that can be accessed via dot notation (instead of with string
#       keys)
# TODO: Make configurable from config file
# TODO: This is getting unrully. Start breaking up file.
# TODO: kwargs being abused in method definitions. move to explicit named
#       better so you know the expected args
# TODO: start using the HTTPError handling decorator.
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
    @wraps(wrapped_func)
    def wrapper(self, *args, **kwargs):
        # TODO: check to make sure the status property exists on the object
        #       first? (i.e. are we decorating a method of the APIManager)
        is_initialized, status_msg = self.status
        if is_initialized:
            logging.info('Calling %s from requires_api decorator', wrapped_func)
            res = wrapped_func(self, *args, **kwargs)
            logging.info('\tFunction returned %s', res)
            if res is not None:
                return res
        else:
            logging.error(
                'Cannot execute %s. REST API has not been initialized.',
                wrapped_func
            )
    return wrapper

def handles_httperror(wrapped_func):
    """
    Decorator for generic handling of HTTPErrors for methods that can throw
    them. Many of the PythonConfluenceAPI methods can for example.

    TODO: unless custom handlers are added to the mix (passed as args and
          called when an exception is raised), this should perhaps be renamed
          to logs_httperror or something similar (since handling isn't actually
          done)

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
            logging.error(
                'HTTPError %s caught when calling %s',
                e, wrapped_func
            )
            logging.error(
                '\t arguments (self, *args, **kwargs): %s, %s, %s',
                self, args, kwargs
            )
    return wrapper

def requires_kw_vals(req_keys=None):
    """
    Decorator for checking if a function/method has the keys required and
    non-None vals before calling. Example use case, keys are required for calls
    to the PythonConfluenceAPI.

    req_keys is a list or tuple of required key names.
    returns None if required keys aren't provided. Otherwise it returns the
            result of the decorated function call.
    """
    def decorator_wrapper(wrapped_func):
        @wraps(wrapped_func)
        def wrapper(self, *args, **kwargs):
            # TODO: set notation here (seta <= setb) is python3 only. problem?
            if set(req_keys) <= set(kwargs.keys()):
                if(all([kwargs[k] for k in req_keys])):
                    return wrapped_func(self, *args, **kwargs)
                else:
                    logging.error(
                        'Call to %s has at least one required value as None.',
                        wrapped_func
                    )
                    logging.error('\tNone value found, keys: (%s)', req_keys)
            else:
                logging.error(
                    'Call to %s does not include the required kwargs.',
                    wrapped_func
                )
                logging.error('\tRequires (%s), got (%s)', req_keys, set(kwargs.keys()))
        return wrapper
    return decorator_wrapper


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
        Init method for class. Nothing special.
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

    @requires_kw_vals(['username', 'password', 'url_base'])
    def init_api(self, username=None, password=None, url_base=None):
        """
        Initialize the confluence REST API interface using the credentials
        passed in. This *does not* actually connect, just creates the object.
        """
        # TODO: Error check the values before initializing
        self.__api = ConfluenceAPI(username, password, url_base)

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

    @requires_kw_vals(['space_key'])
    @requires_api
    @handles_httperror
    def space_exists(self, space_key=None):
        """
        Checks if a space exists based on the space's key.
        """
        sinfo = None
        return self.__api.get_space_information(space_key=space_key)

    @requires_kw_vals(['space_key', 'title'])
    @requires_api
    @handles_httperror
    def content_exists(self, space_key=None, title=None, content_type=None):
        """
        Checks if content exists in the specified space with the specified
        title (and specified content_type if given).
        """
        # TODO: support other args supported by the api
        res = False
        logging.debug(
            'Checking space %s for content %s with type %s',
            space_key, title, content_type
        )
        cntnt = self.__api.get_content(
            space_key=space_key,
            title=title,
            content_type=content_type
        )
        if len(cntnt['results']) > 0:
            # matching content found..
            res = True

        return res

    @requires_api
    def copy_content(self, from_spec, to_spec):
        """
        Copy a content from one place to a new place. Copies an existing page
        to a new page in an existing space right now.

        NOTE: Does not allow specification of new page name yet.

        : param from_spec (dict) : the specification of the from location.
        """
        # TODO: add to/from spec format and requirements documentation to the
        #       docstring
        # TODO: Clean up the get bool, check val, print error, exit madness
        #       below
        # TODO: support the following:
        #    - copy existing page in existing space to new page in existing space
        #    - copy existing page in existing space to new page in new space
        #    - copy existing space to new space
        #    - copy existing space to new page in existing space
        #    - other copy operations the API will allow...TBD
        #    - filtering of type of content copied (coments, attachments, children, etc)

        res = False

        from_params = from_spec.copy()
        to_params = to_spec.copy()
        # TODO: to and from may have different required keys eventually...

        # values in from_spec (may be used a bunch if nothing fails, so assign
        # to variables)
#        from_params.setdefault('space_key', 'space_key', None)
        fs_key = from_spec.get('space_key', None)
        fs_title = from_spec.get('title', None)
        fs_type = from_spec.get('content_type', None)

        # values in to_spec (may be used a bunch if nothing fails, so assign
        # to variables)
#        to_params.setdefault('space_key', 'space_key', None)
        ts_key = to_spec.get('space_key', None)
        ts_title = to_spec.get('title', None)
        ts_type = to_spec.get('content_type', None)

        # TODO: throw errors as appropriate...

        # check that the spaces exist
        # TODO: can this be done in one call using an call and a space filter
        #       list?
        space_err = 'Space %s to copy %s DNE or an error occurred!'
        if not self.space_exists(space_key=fs_key):
            logging.error(space_err, fs_key, 'from')
            return res
        elif not self.space_exists(space_key=ts_key):
            # TODO: when allowing creation of space when copying, the to space
            #       can be allowed to not exist yet.
            logging.error(space_err, ts_key, 'to')
            return res

        # check that the from content exists and that the to content does not
        content_err = 'Content %s to copy %s DNE or an error occurred!'
        if not self.content_exists(
            space_key=fs_key, title=fs_title, content_type=fs_type):
            logging.error(content_err, fs_title, 'from')
            return res
        elif not self.content_exists(
            space_key=ts_key, title=ts_title, content_type=ts_type):
            # Content to copy to exists already
            # TODO: should this fail or allow somehow to rename copy?
            logging.error(content_err, ts_title, 'to')
            return res

        # TODO: Get the expand parameter correct for copying...
        expstr=self.build_expand_str()

        fcontent = self.__api.get_content(
            space_key=fs_key,
            title= fs_title,
            content_type=fs_type,
            expand=expstr
        )

        tcontent = self.__api.get_content(
            space_key=ts_key,
            title= ts_title,
            content_type=ts_type,
            expand=expstr
        )

        # TODO: make a class for doing this.
        cpy = self.get_new_content_stub()
        cpy['type'] = fcontent['results'][0]['type']
        cpy['title'] = fcontent['results'][0]['title']
        cpy['ancestors'][0]['id'] = tcontent['results'][0]['id']
        cpy['space']['key'] = tcontent['results'][0]['space']['key']
        cpy['body']['storage'] = fcontent['results'][0]['body']['storage']

        logging.debug('Copying content to new location.')
        logging.debug('Content to copy: %s', cpy)

        self.__api.create_new_content(cpy)
        res = True
        return res

    def build_expand_str(self):
        """
        Returns the string of properties to expand for results fom the API.
        These properties will be filled in in the the response from the server
        (otherwise, they would just be listed in the _expandable object in the
        result as being able to be expanded, but no values would be given).
        """
        # TODO: build this intelligently. This value is ok for testing copying
        #       of a page (no sub-pages, attachments, etc)
        return 'history,space,version,body.storage,ancestors'

    def get_new_content_stub(self):
        """
        Gets a stub for new content. Just useful for copying content right this
        second.
        """
        stub = {
            'type': '',
            'title': '',
            'ancestors': [
                {
                    'id': '',
                },
            ],
            'space': {
                'key': '',
            },
            'body': {
                'storage': '',
            },
        }
        return stub
