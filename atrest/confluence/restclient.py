import sys

from traitlets import (
    Integer, List, default
)

from PythonConfluenceAPI import (
    ConfluenceAPI,
    all_of,
)

from atrest.core.clientbase import (
    AtRESTClientBase,
)

from atrest.utils.decorators import (
    debug_log_call,
    logs_httperror,
)

from atrest.confluence.operation import (
    SpaceLister,
)

# TODO: Extra aliases or flags?

# max results for a query. this is a biggish number that doesn't cause
# Confluence to bug out (2**32 does for sure).
# TODO: see if there's a documented limit to this number for Confluence
MAX_RESULTS = (2**16)*2

class ConfluenceRESTClient(AtRESTClientBase):
    """
    Class wrapping the PythonConfluenceAPI.ConfluenceAPI. Provides methods for
    common operations.
    """

    # LEFTOFF - see application.py for base class method.
    # TODO: is this configurable? regardless, there needs to be a way to add
    #       them at init, like via plugin dir or configurable list.
    subcommands = {
        'spaces': (SpaceLister, "List spaces available to a user")
    }

    classes = List([SpaceLister])

    limit = Integer(MAX_RESULTS, min=1, max=MAX_RESULTS,
                    help='max number of results returned for queries'
            ).tag(config=True)

    def __init__(self, *args, **kwargs):
        """
        Init method for class. Calls the base class's constructor.
        """
        super().__init__(*args, **kwargs)
        self._api = None


    def initialize(self, *args, **kwargs):
        """
        """
        self.parse_command_line(argv=kwargs.get('argv', None))
# #        super().initialize(*args, **kwargs)
#         pass

    def initialize_api(self, username=None, apiurlbase=None):
        """
        Method to initialize the REST API. Override of base class method.

        NOTE: password is not stored. If this is called with getpass.getpass()
              in place of the password argument (and in a command line or
              Jupyter notebook setting) the user will be prompted for one.
        """
        if username:
            self.username = username
        else:
            if not self.username:
                self.log.error('Username not configured for API client')
#            sys.exit(-1)
                return False

        if apiurlbase:
            self.api_url_base = apiurlbase
        else:
            if not self.api_url_base:
                self.log.error('REST API URL base not configured for API client')
#            sys.exit(-1)
                return False

        pw = self.get_password()
        if not pw:
            # can't connect the client without a password.
            self.log.error('Could not get password for API client')
            # TODO: is this too harsh? easier way to handle?
#            sys.exit(-1)
            return False

        self._api = ConfluenceAPI(self.username, pw, self.api_url_base)
        return True

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
    def add_or_update_attachment(self, content_id, fake_arg):
        """
        """
        pass

    @logs_httperror
    @debug_log_call()
    def download_attachment(self, title, dl_dir, space_key=None):
        """
        Try to find and download an attachment specified by title in
        space space_key to the directory dl_dir. Returns a downloaded file
        path on success and None for failure.
        """
        kw = {
            'content_type': 'attachment',
            'space_key': space_key,
            'title': title,
        }

        res = self.get_content(**kw)

        if not res:
            self.log.error('Could not download attachment %s', title)
            return None
        elif not len(res):
            self.log.warn('No attachment found called %s', title)
            return None
        elif len(res) > 1:
            self.log.warn('Too many attachments found called %s. Try expanding your filtering', title)
            return None

        return self.download_attachment_by_id(res[0]['id'], dl_dir)

    @logs_httperror
    @debug_log_call()
    def download_attachment_by_id(self, attach_id, dl_dir):
        """
        Download an attachment specified by attach_id to the directory dl_dir.
        Returns a downloaded file path on success and None for failure.
        """
        attach_res = self.get_content_by_id(attach_id)

        if not attach_res:
            self.log.error('Could not download attachment with id %s', attach_id)
            return None

        title = attach_res.get('title', None)
        self.log.debug('Downloading attachment %s to dir %s', title, dl_dir)

        # use the download link minus the preceeding '/'
        l = attach_res['_links']['download'][1:]
        p = os.path.join(dl_dir, title)
        return self._download_by_link(l, p)

    @logs_httperror
    @debug_log_call()
    def _download_by_link(self, dl_link, dl_path, raw=True):
        """
        """
        cntnt = self.__api._service_get_request(sub_uri=dl_link, raw=raw)

        with open(dl_path, 'wb') as f:
            f.write(cntnt)

        self.log.debug('Download of %s completed', dl_path)
        return dl_path

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

    # def start(self):
    #     super().start()

    # def _start_normal(self):
    #     """
    #     """
    #     self.log.info('Self %s is going to start in normal mode', self)
    #
    # def _start_interactive(self):
    #     """
    #     """
    #     self.log.info('Self %s is going to start in interactive mode', self)

# TODO: this is hardcoded to test. this should be moved to a method (
#       made part of _get_subcommands?) and needs to add this class
#       to the classes list for each subcommand (so the cli args for
#       this class can be processed when calling subcommands)
SpaceLister.classes.append(ConfluenceRESTClient)
