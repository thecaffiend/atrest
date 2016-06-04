import os.path

from traitlets import (
    Integer, List,
)

# TODO: separate the client app from the api wrapper stuff.
# TODO: wrap all of in our API wrappers instead of in the client application
from PythonConfluenceAPI import (
    ConfluenceAPI,
    all_of,
)

from atrest.core.application import (
    AppRunMode,
)

from atrest.core.clientbase import (
    AtRESTClientBase,
    ResultsException,
)

from atrest.utils.decorators import (
    debug_log_call,
    logs_httperror,
    makes_kwarg_dict,
)

from atrest.confluence.operations import (
    PageCopier,
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
    common operations. Also acts as the AtREST subcommand for confluence
    operations for now.
    """

    # LEFTOFF - see application.py for base class method.
    # TODO: is this configurable? regardless, there needs to be a way to add
    #       them at init, like via plugin dir or configurable list.
    subcommands = {
        'copypage': (PageCopier, "Copy a page to another location"),
        'spaces': (SpaceLister, "List spaces available to a user"),
    }

# TODO: remove if not needed
#    classes = List([SpaceLister, PageCopier])

    limit = Integer(MAX_RESULTS, min=1, max=MAX_RESULTS,
        help='max number of results returned for queries').tag(config=True)

# TODO: remove if not needed
    # def __init__(self, *args, **kwargs):
    #     """
    #     Init method for class. Calls the base class's constructor.
    #     """
    #     super().__init__(*args, **kwargs)
    #     self._api = None

# TODO: is this needed?
    def initialize(self, *args, **kwargs):
        """
        """
        self.parse_command_line(argv=kwargs.get('argv', None))

    def initialize_api(self, username=None, apiurlbase=None):
        """
        Method to initialize the REST API. Override of base class method.

        NOTE: password is not stored here or echoed. it *is* stored in the
              PythonConfluenceAPI in plaintext however.
        """
        if username:
            self.username = username
        else:
            if not self.username:
                self.log.error('Username not configured for API client')
                return False

        if apiurlbase:
            self.api_url_base = apiurlbase
        else:
            if not self.api_url_base:
                self.log.error('REST API URL base not configured for API client')
                return False

        pw = self.get_password()
        if not pw:
            # can't connect the client without a password.
            self.log.error('Could not get password for API client')
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

    # TODO: Use makes_kwarg_dict instead of in method dicts below
    # TODO: none of these methods respect star/limit (they all use all_of). FIX

    # TODO: get space names doesn't need expand
    @makes_kwarg_dict(ignore_keys=['fetch_all'], sub_keys={'space_filter': 'space_key',})
    @logs_httperror
    @debug_log_call()
    def get_space_names(self, space_filter=None, start=None, limit=None, callback=None, fetch_all=True):
        """
        Returns the names Confluence spaces available. space_filter should be
        a list of space name/key strings to filter with if provided
        """
        # kw = {
        #     'space_key': space_filter,
        #     'start': start,
        #     'limit': limit,
        #     'callback': callback
        # }
        # print('keyword_dict: %s ' % self.get_space_names.keyword_dict)
        res = []
        if fetch_all:
#            res = all_of(self._api.get_spaces, **kw)
            res = all_of(self._api.get_spaces, **self.get_space_names.keyword_dict)
        else:
#            res = self._api.get_spaces(**kw)['results']
            res = self._api.get_spaces(**self.get_space_names.keyword_dict)['results']

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
    def get_space_homepage(self, space_key, expand=None, callback=None):
        """
        Get the homepage content for the space with a given key if it exists.
        None otherwise. Other the space_key, all kwargs are applied to getting
        the homepage content.
        """
        space_info = self.get_space_info(space_key=space_key, expand='homepage')
        hompage_id = space_info['homepage']['id']
        return self.get_content_by_id(homepage_id, expand=expand, callback=callback)


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
    def get_only_content(self, content_type=None, space_key=None, title=None, status=None, posting_day=None,
                    expand=None, callback=None):
        """
        Gets a single content result using the given filters if it exists. If
        zero results or more than one result is returned, a ResultsException
        is thrown. Otherwise the single result is returned.
        """
        kw = {
            'content_type': content_type,
            'space_key': space_key,
            'title': title,
            'status': status,
            'posting_day': posting_day,
            'expand': expand,
            'callback': callback,
        }

        res = self.get_content(**kw)
        n = len(res) if res else 0
        if n != 1:
            e = ResultsException(
                'Invalid number of results returned!',
                expected='One result',
                actual='[%s] results' % n,
                extra='Search params [%s]' % (kw)
            )
            self.log.error(e)
            raise e

        return res[0]

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
            self.log.error(
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
        content = self._api.get_content_by_id(content_id, status=status, version=version, expand=expand, callback=callback)
        if not content:
            e = ResultsException(
                'Could not get content by id!',
                actual='result [%s]' % content,
                extra='Content id searched [%s]' % (content_id)
            )
            self.log.error(e)
            raise e
        return content

    @logs_httperror
    @debug_log_call()
    def get_parent_content_by_id(self, content_id, status=None, version=None, expand=None, callback=None):
        """
        Get the parent of the content with the given id. Other than content_id,
        all other kwargs are applied to getting the parent content. If the
        requested content is a top-level page, its content will be returned as
        it is the top level page in the heirarchy.
        """
        content = self.get_content_by_id(content_id, expand='ancestors')

        # there is a parent, it'll be the first one in ancestors. if there are
        # no ancestors, the content is a top level page, parent id will be set
        # to content_id
        parent_id = content['ancestors'][0]['id'] if \
            len(content['ancestors']) else content_id

        # even if the above content is treated as the parent, need to re-fetch
        # with respect to the passed in kwargs (e.g. caller may not want
        # 'ancestors' expanded in returned content)
        return self.get_content_by_id(parent_id, status=status, version=version, expand=expand, callback=callback)

    @logs_httperror
    @debug_log_call()
    def check_content_title(self, space_key, title, rename=True, rename_limit=100):
        """
        See if the content name 'title' exists in the space already. If not,
        return it. If so, attempt to find a new name for the content if the
        flag is set. Return None if no suitable name can be found.
        """
        # TODO: this method feels wrong (complicated). refactor
        tmp_title = title
#        existing_content = self.get_content(space_key=space_key, title=tmp_title)

#        if existing_content:
        if self.get_content(space_key=space_key, title=tmp_title):
            self.log.warning(
                'Content with name [%s] already exists in %s',
                tmp_title,
                space_key,
            )

            if rename:
                self.log.debug('Attempting rename of [%s]', tmp_title)
                # TODO: add a way for the user to specify a template for the
                #       renames
                # append a counter to the content title until we find one we
                # can use
                rename_title = ''
                for cntr in range(rename_limit):
                    rename_title = '%s %i' % (tmp_title, cntr)
                    self.log.debug('Checking name [%s]', rename_title)
                    # existing_content = self.get_content(
                    #     space_key=space_key,
                    #     title=rename_title
                    # )
                    if not self.get_content(space_key=space_key, title=rename_title):
                        self.log.debug('No conflict, returning [%s]', rename_title)
                        # we should have a good title now.
                        tmp_title = rename_title
                        return tmp_title

                self.log.error(
                    'Hit max number of rename attempts (%i). Aborting operation',
                    rename_limit
                )
                return None
            else:
                # renaming wasn't specified, so we should fail the operation
                self.log.error(
                    'Content with title [%s] exists in space [%s] and ' \
                    'renaming was not specified. Aborting operation',
                    tmp_title, space_key
                )
                return None
        return tmp_title

    @logs_httperror
    @debug_log_call()
    def get_content_children_by_type(self, content_id, child_type, expand=None, parent_version=None,
                                     start=None, limit=None, callback=None, fetch_all=True):
        """
        Gets the children of some content that are of a specified type.
        """
        kw = {
            'content_id': content_id,
            'child_type': child_type,
            'expand': expand,
            'parent_version': parent_version,
            'start': start,
            'limit': limit,
            'callback': callback,
        }

        res = []
        if fetch_all:
            res = all_of(self._api.get_content_children_by_type, **kw)
        else:
            res = self._api.get_content_children_by_type(**kw)['results']

        return [c for c in res] if res else []

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
    def add_attachment(self, content_id, attach_path, title=None, update_existing=True):
        """
        Add an attachment to the content with content_id, or update an
        existing one with the same name if it exists and update is True.
        """
        if not title:
            # use the file name of attach_path as the name of the new
            # attachment
            pth, title = os.path.split(attach_path)

        # LEFTOFF
        existing_attachs = self.get_attachments_for_id(content_id)
        existing_titles = [a['title'] for a in existing_attachs]

        try:
            idx = existing_titles.index(title)
            if update_existing:
                attach_msg = \
                    'Source attachment %s exists in destination ' \
                    'content already. Updating existing.'
                self.log.debug(attach_exists_msg, title)

                if self.mode == AppRunMode.dry_run:
                    self.log.info('Dry run: %s', attach_msg)
                else:
                    self.log.debug(attach_msg)
                    with open(attach_path, 'rb') as dl:
                        self._api.update_attachment(
                            content_id=content_id,
                            attachment_id=existing_attachs[idx]['id'],
                            attachment={'file': dl}
                        )
        except ValueError as e:
            # the title for the source attachment was not found in
            # the destination attachment titles. it means we don't
            # have to update an existing attachment and can just
            # add it to the dst
            attach_msg = 'Creating new attachment %s for destination %s' % (title, content_id)

            if self.mode == AppRunMode.dry_run:
                self.log.info('Dry run: %s', attach_msg)
            else:
                self.log.debug(attach_msg)
                with open(attach_path, 'rb') as dl:
                        self._api.create_new_attachment_by_content_id(
                            content_id=content_id,
                            attachments={'file': dl}
                        )


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
        cntnt = self._api._service_get_request(sub_uri=dl_link, raw=raw)

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
    def create_new_page(self, new_content, callback=None):
        """
        Create a new page. The minimum content needed can be obtained with a
        call to get_page_template with all keyword args provided (values for
        all of them are required for new pages).
        """
        # TODO: generalize to create_new_content?
        if self.mode == AppRunMode.dry_run:
            created_content = new_content.copy().update({'id': DRY_RUN_ID})
            self.log.info('Dry run create_new_page. Would create %s', created_content)
        else:
            created_content = self._api.create_new_content(new_content, callback=callback)
        return created_content


    @logs_httperror
    @debug_log_call()
    def add_comment(self, content_id, title, comment_val):
        """
        Add a new comment to the content with id content_id. The comment will
        have the title and value given.

        NOTE: The comment_val value should be an HTML snippet in <p> tags.
              Seems to work with plain text, but comments added through
              Confluence UI are in <p> tags.

        NOTE: This will not add comments to attachments, or anything else that
              stores comments in a weird place (e.g. attachments use the
              metadata field as opposed to storing them as child types).
        """
        # TODO: make work with non-HTML formatted strings. seems to work ok
        #       with plain text values, but not sure the implications
        # TODO: add mechanism to add comments to oddballs like attachments

        # TODO: what is the bare minimum of the dst_content that's required for
        #       a comment's container?

        dst_content = {}
        dst_space = ''

        if self.mode == AppRunMode.real_run:
            # The id may be invalid in dry run, so only do this for real stuff
            dst_content = self.get_content_by_id(content_id)
            dst_space = dst_content['space']['key']

        new_cmnt = self.get_comment_template(
            space_key=dst_space,
            title=title,
            container_content=dst_content,
            comment_val=comment_val
        )

        if self.mode == AppRunMode.dry_run:
            new_cmnt.update({'id': -1})
            self.log.info('Dry run add_comment. Would add %s', new_cmnt)
        else:
            new_cmnt = self._api.create_new_content(new_cmnt)
        return new_cmnt

    @logs_httperror
    @debug_log_call()
    def add_labels(self, content_id, label_list):
        """
        Add a list of labels to the content with id content_id. The api wants
        this as a list rather than adding one at a time, so there is no
        add_label (singular) method.

        NOTE: The labels are of the format:
            {'prefix': prefix_val, 'name': name_val}
        """
        # TODO: make this not need specifically formatted labels, but rather
        #       take a list of tuples of (prefix, name) pairs
        if self.mode == AppRunMode.dry_run:
            self.log.info('Dry run add_labels. Would add %s', label_list)
        else:
            self._api.create_new_label_by_content_id(
                content_id=content_id,
                label_names=label_list
            )

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

# Template methods for new content
    def get_page_template(self, content_type=None, space_key=None, title=None, parent_id=None, storage_val=None):
        """
        Get a dict with the minimal content needed for a new page.

        NOTE: If the keyword values are not provided, None will be used, and it
              is up to the callet to fill them in before the returned dict can
              be used to create new content
        """
        return {
            'type': content_type,
            'title': title,
            'ancestors': [{'id': parent_id,},],
            'space': {'key': space_key,},
            'body': {'storage': storage_val,},
        }

    def get_comment_template(self, space_key=None, title=None, container_content=None, comment_val=None):
        """
        Get a dict with the minimal content needed for a new comment.

        NOTE: container_content is the content of the container, not an id or
              title.

        NOTE: If the keyword values are not provided, None will be used, and it
              is up to the callet to fill them in before the returned dict can
              be used to create new content
        """
        return {
            'type':'comment',
            'title': title,
            'space': {'key': space_key,},
            'container': container_content,
         	'body': {
                'storage': {
                    'value': comment_val,
                    'representation': 'storage'
                },
            },
        }

# TODO: remove if not needed
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
#SpaceLister.classes.append(ConfluenceRESTClient)
