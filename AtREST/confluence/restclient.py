from traitlets import (
    Integer,
)

from PythonConfluenceAPI import (
    ConfluenceAPI,
    all_of,
)

from AtREST.clientbase import (
    ClientRunMode,
    AtRESTClientBase,
)

from AtREST.utils.decorators import (
    debug_log_call,
    logs_httperror,
)

# max results for a query. this is a biggish number that doesn't cause
# Confluence to bug out (2**32 does for sure).
# TODO: see if there's a documented limit to this number for Confluence
MAX_RESULTS = (2**16)*2

class ConfluenceRESTClient(AtRESTClientBase):
    """
    Class wrapping the PythonConfluenceAPI.ConfluenceAPI. Provides methods for
    common operations.
    """

    limit = Integer(MAX_RESULTS, min=1, max=MAX_RESULTS,
                    help='max number of results returned for queries'
            ).tag(config=True)

    # TODO: Once tested, the mode should default to real_run.
    def __init__(self, *args, **kwargs):
        """
        Init method for class. Calls the base class's constructor.
        """
        self._api = None
        super(ConfluenceRESTClient, self).__init__(*args, **kwargs)

    def initialize_api(self, username, password, api_url_base, mode=None, *args, **kwargs):
        """
        Method to initialize the REST API. Override of base class method.

        NOTE: password is not stored. If this is called with getpass.getpass()
              in place of the password argument (and in a command line or
              Jupyter notebook setting) the user will be prompted for one.
        """
        if mode:
            self.mode = mode
        self.username = username
        self.api_url_base = api_url_base

        self._api = ConfluenceAPI(self.username, password, self.api_url_base)

    # TODO: operations to add/change
    #   content_exists -> get_content
    #   get_content_by_id
    #   get_content_id
    # DONE:
    #   list_space_names -> get_space_names
    #   space_exists -> get_space
    #   get_space_info

    # TODO: Smarter kw dict in the below methods...
    # TODO: none of these methods respect limit (they all use all_of). FIX

    @logs_httperror
    @debug_log_call()
    def get_space_names(self, space_filter=None, expand=None, start=None, limit=None, callback=None, fetch_all=True):
        """
        Returns the names Confluence spaces available. space_filter should be
        a list of space name/key strings to filter with if provided
        """
        kw = {
            'space_key': space_filter,
            'expand': expand,
            'start': start,
            'limit': limit,
            'callback': callback
        }
        res = []
        if fetch_all:
            res = all_of(self._api.get_spaces, **kw)
        else:
            res = self._api.get_spaces(**kw)['results']

        return [s['name'] for s in res]

    @logs_httperror
    @debug_log_call()
    def get_space_content(self, space_key, content_type=None, depth=None, expand=None, start=None, limit=None, callback=None, fetch_all=True):
        """
        Get space contents if the space exists. If content_type
        is given and valid, the content of just that type will be returned.
        """
        kw = {
            'depth': depth,
            'expand':expand,
            'start':start,
            'limit':limit,
            'callback':callback,
        }

        res = []
        a = []
        meth = None
        # TODO: do the content_type checks and other checks of the same type
        #       smarter. use traitlets and validate methods
        if content_type and content_type in ['page', 'bogpost']:
            a = [space_key, content_type]
            meth = self._api.get_space_content_by_type
        else:
            a = [space_key]
            meth = self._api.get_space_content

        if fetch_all:
            res = all_of(meth, *a, **kw)
        else:
            res = meth(*a, **kw)['results']

        return [c for c in res] if res else []

    @logs_httperror
    @debug_log_call()
    def get_space_info(self, space_key=None, expand=None, callback=None):
        """
        Get info for the space with a given key if it exists. None otherwise.
        """
        return self._api.get_space_information(space_key=space_key, expand=expand, callback=callback)


    @logs_httperror
    @debug_log_call()
    def get_content(self, content_type=None, space_key=None, title=None, status=None, posting_day=None,
                    expand=None, start=None, limit=None, callback=None, fetch_all=True):
        """
        Gets content (in the specified space with the specified kw values) if
        it exists. If found it returns the content (shoud be the only element
        in the results object if space and title filters are given).
        """
        kw = {
            'content_type': content_type,
            'space_key': space_key,
            'title': title,
            'status': status,
            'posting_day': posting_day,
            'expand': expand,
            'start': start,
            'limit': limit,
            'callback': callback,
        }

        res = []
        if fetch_all:
            res = all_of(self._api.get_content, **kw)
        else:
            res = self._api.get_content(**kw)['results']

        return [c for c in res] if res else []

    @logs_httperror
    @debug_log_call()
    def get_content_id(self, space_key, title):
        """
        Gets the id for a piece of content. This should only ever get one or
        zero items, so if nothing is found (or an error occurs) None will be
        returned, otherwise the content dict will be.
        """
        res = self.get_content(space_key=space_key, title=title)
        if len(res) > 1:
            # TODO: this should be an error condition. there can be only one
            #       raise an error eventually
            logging.error(
                'Too many results (%s) returned to get an id for content [%s] in space [%s]',
                len(res),
                title,
                space_key
            )
            return None
        else:
            return res[0]['id'] if len(res) else None


    @logs_httperror
    @debug_log_call()
    def get_content_by_id(self, content_id, status=None, version=None, expand=None, callback=None):
        """
        Gets a piece of content by it's id. This should only ever get one or
        zero items, so if nothing is found (or an error occurs) None will be
        returned, otherwise the content dict will be.
        """
        return self._api.get_content_by_id(content_id, status=status, version=version, expand=expand, callback=callback)


    @logs_httperror
    @debug_log_call()
    def get_attachments_for_id(self, content_id, expand=None, start=None, limit=None, filename=None, media_type=None,
                                callback=None, fetch_all=True):
        """
        Get attachments for content with id content_id.
        """
        res = []
        kw = {
            'content_id': content_id,
            'expand': expand,
            'start': start,
            'limit': limit,
            'filename': filename,
            'media_type': media_type,
            'callback': callback,
        }

        if fetch_all:
            res = all_of(self._api.get_content_attachments, **kw)
        else:
            res = self._api.get_content_attachments(**kw)['results']

        return [attach for attach in res]


    @logs_httperror
    @debug_log_call()
    def get_comments_for_id(self, content_id, expand=None, parent_version=None, start=None, limit=None,
                             location=None, depth=None, callback=None, fetch_all=True):
        """
        Get comments for content with id content_id.
        """
        res = []
        kw = {
            'content_id': content_id,
            'expand': expand,
            'parent_version': parent_version,
            'start': start,
            'limit': limit,
            'location': location,
            'depth': depth,
            'callback': callback,
        }

        if fetch_all:
            res = all_of(self._api.get_content_comments, **kw)
        else:
            res = self._api.get_content_comments(**kw)['results']

        return [cmt for cmt in res]


    @logs_httperror
    @debug_log_call()
    def get_labels_for_id(self, content_id, prefix=None, start=None, limit=None, callback=None, fetch_all=True):
        """
        Get labels for content with id content_id.
        """
        res = []
        kw = {
            'content_id': content_id,
            'prefix': prefix,
            'start': start,
            'limit': limit,
            'callback': callback,
        }

        if fetch_all:
            res = all_of(self._api.get_content_labels, **kw)
        else:
            res = self._api.get_content_labels(**kw)['results']

        return [lab for lab in res]
