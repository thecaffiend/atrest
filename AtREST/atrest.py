import logging
import os
import os.path

from functools import wraps
from enum import Enum
from contextlib import closing
from tempfile import TemporaryDirectory


from requests import (
    HTTPError,
)

from PythonConfluenceAPI import (
    ConfluenceAPI,
    all_of,
)

# TODO: meta TODO, move TODOs to README if possible
# TODO: look at neobunch package (evolution of bunchify). changes a dict to an
#       object that can be accessed via dot notation (instead of with string
#       keys)
# TODO: This is getting unrully. Start breaking up file.
# TODO: use the HTTPError handling decorator where needed (only some places
#       right now).


# TODO: move this to init of ConfluenceRESTClient?
# TODO: this may not work in a notebook. see how to configure logging correctly
#       for use there.
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# content_id val to use for dry runs.
DRY_RUN_ID = -333

# MOVED to AtREST.utils.decorators
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

# TODO: deprecate this
# def requires_kw_vals(req_keys=None):
#     """
#     Decorator for checking if a function/method has the keys required and
#     non-None vals before calling. Example use case, keys are required for calls
#     to the PythonConfluenceAPI.
#
#     req_keys is a list or tuple of required key names.
#     returns None if required keys aren't provided. Otherwise it returns the
#             result of the decorated function call.
#     """
#     def decorator_wrapper(wrapped_func):
#         @wraps(wrapped_func)
#         def wrapper(self, *args, **kwargs):
#             # TODO: set notation here (seta <= setb) is python3 only. problem?
#             if set(req_keys) <= set(kwargs.keys()):
#                 if(all([kwargs[k] for k in req_keys])):
#                     return wrapped_func(self, *args, **kwargs)
#                 else:
#                     logging.error(
#                         'Call to %s has at least one required value as None.',
#                         wrapped_func
#                     )
#                     logging.error('\tNone value found, keys: (%s)', req_keys)
#             else:
#                 logging.error(
#                     'Call to %s does not include the required kwargs.',
#                     wrapped_func
#                 )
#                 logging.error('\tRequires (%s), got (%s)', req_keys, set(kwargs.keys()))
#         return wrapper
#     return decorator_wrapper

# MOVED to AtREST.utils.decorators
# TODO: remove the hand holding checks for none. let exceptions propagate and
#       throw some
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

# MOVED - AtREST.clientbase.py
class ClientMode(Enum):
    """
    Enum for the mode to operate in. dry_run only logs what would happen.
    real_run does it for realz...
    """
    dry_run = 0
    real_run = 1

# NEW BASE CLASS AtRESTClientBase - AtREST.clientbase.py
# TODO: move everything that is command specific to somewhere else (like a
#       command class). this class should expose methods that wrap the api
#       object's calls, but not do things like copying
class ConfluenceRESTClient():
    """
    Class wrapping the PythonConfluenceAPI.ConfluenceAPI. Provides methods for
    common operations.
    """

    # "constants"

    # max results for a query. this is a biggish number that doesn't cause
    # Confluence to bug out (2**32 does for sure).
    # TODO: see if there's a documented limit to this number for Confluence
    MAX_RESULTS = (2**16)*2

# MOVED
    def __init__(self, username, password, url_base, mode=ClientMode.dry_run):
        """
        Init method for class. Nothing special.
        """
        self.__api = ConfluenceAPI(username, password, url_base)
        self.__mode = mode
        self.__query_params = None

# MOVED
    @property
    def api(self):
        """
        Wrapped API property getter
        """
        #TODO: THIS IS JUST FOR TESTING. REMOVE IT. TOO MUCH INFO IS AVAILABLE
        #      TO INTERACTIVE ENVIRONMENTS WHEN THIS IS EXPOSED (E.G.
        #      PASSWORDS)
        return self.__api

# DEPRECATE
    @property
    def query_params(self):
        """
        Property getter for query parameters.
        """
        # TODO: still needed or worthwhile?
        # TODO: do we want a setter?
        if self.__query_params is None:
            # TODO: add more as they are found to  be useful
            self.__query_params = {
                'limit': self.MAX_RESULTS,
            }
        return self.__query_params

# MOVED
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

# DEPRECATE
    def recent_content(self, *args, **kwargs):
        """
        Returns the recent Confluence content available to the user set in the
        REST API object. Used mostly for testing connection worked right now.
        """
        # TODO: support all the params the api's get_content method allows
        return self.__api.get_content()

# TODO: make this a command. should be a good test case.
    @debug_log_call()
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

# MOVED
#    @requires_kw_vals(['space_key'])
    @handles_httperror
    def space_exists(self, space_key=None):
        """
        Checks if a space exists based on the space's key.
        """
        return self.__api.get_space_information(space_key=space_key)

# MOVED
    @handles_httperror
    @debug_log_call()
    def content_exists(self, content_id=None, space_key=None, title=None, content_type=None, expand=None):
        """
        Checks if content exists in the specified space with the specified
        title (and specified content_type if given). If found it returns the
        content (shoud be the only element in the results object), and if not,
        None is returned.

        NOTE: This returns the basic content. No expansions. This may not be
              best long term, but is for now. This content is meant to be used
              for a check on existence, and it is assumed that other operations
              will use this returned value (e.g. to get the content for the id
              and then use that for other things)
        """
        # TODO: support other args supported by the api
        # TODO: Support expand params in here. Important for the recursion...
        cntnt = None
        if content_id is not None:
            logging.debug('Checking for content with id %s', content_id)
            # returns a single result
            cntnt = self.__api.get_content_by_id(content_id, expand=expand)
        elif space_key is not None and title is not None:
            logging.debug(
                'Checking space %s for content %s with type %s',
                space_key, title, content_type
            )
            # potentially returns multiple results, all results in 'results'
            # list
            res = self.__api.get_content(
                space_key=space_key,
                title=title,
                content_type=content_type,
                expand=expand
            )
            num_results = int(res['size'])

            if num_results > 0:
                # matching content found...
                if num_results > 1:
                    # TODO: what if more than one thing is returned?
                    mult_res_err = 'REST API returned multiple results for ' \
                        'query. Returned %i results. Returning first found!'
                    logging.warning(mult_res_err, num_results)
                cntnt = res['results'][0]

        else:
            # no can do. have to specify one of the above conditions
            logging.error(
                'Have to specify either content_id or space_key and title ' \
                'to check for content existance. All were None'
            )

        return cntnt

# MOVED
    @handles_httperror
    @debug_log_call()
    def get_attachments_for_id(self, content_id, expand=None):
        """
        Get attachments for content with id content_id. At this time, all
        attachment entries will be returned.

        TODO: Add support for PythonConfluenceAPI kwargs:
            start, limit, filename, media_type, and callback
        """
        kw = {'content_id': content_id, 'expand':expand}
        attachments = [
            attach for attach in
                all_of(
                    self.__api.get_content_attachments,
                    **kw
                )
        ]

        logging.debug(
            'Content %s has %i attachments',
            content_id,
            len(attachments)
        )

        return attachments

# MOVED
    @handles_httperror
    @debug_log_call()
    def get_comments_for_id(self, content_id, expand=None):
        """
        Get comments for content with id content_id. At this time, all
        comment entries will be returned.

        TODO: Add support for PythonConfluenceAPI kwargs:
            parent_version, start, limit, location, depth, and callback
        """
        kw = {'content_id': content_id, 'expand':expand}
        comments = [
            cmt for cmt in
                all_of(
                    self.__api.get_content_comments,
                    **kw
                )
        ]

        logging.debug(
            'Content %s has %i comments',
            content_id,
            len(comments)
        )

        return comments

# MOVED
    @handles_httperror
    @debug_log_call()
    def get_labels_for_id(self, content_id):
        """
        Get labels for content with id content_id. At this time, all
        label entries will be returned.

        TODO: Add support for PythonConfluenceAPI kwargs:
            prefix, start, limit, and callback
        """
        kw = {'content_id': content_id}
        labels = [
            lab for lab in
                all_of(
                    self.__api.get_content_labels,
                    **kw
                )
        ]

        logging.debug(
            'Content %s has %i labels',
            content_id,
            len(labels)
        )

        return labels

# LEFTOFF moving code elsewhere. below is copier command stuff

# TODO: move to copier command class
    @debug_log_call()
    def copy_content(self, src_spec, dst_spec):
        """
        Copy a content from one place to a new place. Copies an existing page
        to a new page in an existing space right now. See get_default_specs
        in this class for key/value doc of the specs.
        """
        # TODO: Clean up the get bool, check val, print error, exit madness
        #       below
        # TODO: clean up the dict.get('key', default) madness as well. and take
        #       care with the nested dicts (not using .get for them right yet)
        # TODO: support the following:
        #    - copy existing page in existing space to new page in existing space
        #    - copy existing page in existing space to new page in new space
        #    - copy existing space to new space
        #    - copy existing space to new page in existing space
        #    - other copy operations the API will allow...TBD
        #    - filtering of type of content copied (coments, attachments, children, etc)

        # TODO:
        #   Need to know to copy attachments, labels

        # Check the spaces exist.
        # TODO: Does this need to happen? can't we just check the content
        #       exists and error out otherwise? if not, make method for this
        src_space_info = self.space_exists(space_key=src_spec['space_key'])

        if src_space_info is None:
            logging.error(
                'Could not locate source space %s for copying from',
                src_spec.get('space_key', None)
            )
            return False

        dst_space_info = self.space_exists(space_key=dst_spec['space_key'])
        if dst_space_info is None:
            logging.error(
                'Could not locate destination space %s for copying to',
                dst_spec.get('space_key', None)
            )
            return False

        expstr=self.build_expand_str()

        # TODO: make specs use content_type instead of type
        # TODO: handle content being None
        # TODO: make a default dict for the params since this is the same as
        #       below (dst_params). need src_params for copy call, so can't use
        #       same dict

        # get the source content
        src_params = {
            'content_id': src_spec.get('content_id', None),
            'space_key': src_spec.get('space_key', None),
            'title': src_spec.get('title', None),
            'content_type': src_spec.get('type', None),
            'expand': expstr,
        }
        src_content = self.content_exists(**src_params)

        # now the destination content
        dst_params = {
            'content_id': dst_spec.get('content_id', None),
            'space_key': dst_spec.get('space_key', None),
            'title': dst_spec.get('title', None),
            'content_type': dst_spec.get('type', None),
            'expand': expstr,
        }

        dst_content = self.content_exists(**dst_params)

        self._copy(
            src_params,
            dst_content['id'], # don't have the content anymore. so no id.
            dst_spec['space_key'],
            dst_spec['content_copy']['title'],
            rename=dst_spec['content_copy']['rename'],
            rename_limit=dst_spec['content_copy']['rename_limit'],
            overwrite=dst_spec['content_copy']['overwrite'],
        )

        return True

    # TODO: move to copier command class
    @debug_log_call()
    def _copy(self, src_spec, dst_parent_id, dst_space_key, dst_title, rename=True, rename_limit=100, overwrite=False, cpy_attachments=True, cpy_labels=True, cpy_comments=True):
        """
        """
        # This is recursively called.
        # TODO: Do we need to return status? See if we need to do anything with
        #       it
        # TODO: make sure dry run is respected!
        # TODO: rename src_spec above so as not to confuse it with a spec dict
        # TODO: add support for specifying the flags for attachments, sub pages, comments, etc

        # Get source content
        src_content = self.content_exists(**src_spec)

        if src_content is None:
            logging.error(
                'Content %s to copy from DNE or an error occurred!',
                src_spec.get('title', None)
            )
            return

        # ensure dst title is good
        dst_title = self._get_content_title(
            dst_space_key,
            dst_title,
            rename=rename,
            rename_limit=rename_limit,
            overwrite=overwrite
        )
        if dst_title is None:
            # log error and return
            logging.error('Could not get a suitable title for the new content')
            return

        # set the parent/anscestor appropriately
        #   if given, set to that
        #   if not given
        #      set to source ancestor
        # TODO: should we set the id to the id of the space with
        #       dst_space_key if the dst_space_key is different than
        #       src_content['space']['key']? Seems this could bork the copy if
        #       we don't
        if dst_parent_id is None:
            dst_parent_id = src_content['space']['key']

        # copy the page
        new_content = self._copy_page(src_content, dst_parent_id, dst_space_key, dst_title)
        if new_content is None:
            copy_err = 'Could not copy page with args: \n\tsrc_content %s ' \
            '\n\tdst_parent_id %s \n\tdst_space_key %s \n\tdst_title %s'
            logging.error(
                copy_err, src_content, dst_parent_id, dst_space_key, dst_title
            )
            return

        dst_id = new_content['id']

        expstr = src_spec.get('expand', None)

        # copy attachments if specified
        if cpy_attachments:
            self._copy_attachments(src_content, dst_id, expand=expstr)

        # copy comments if specified
        if cpy_comments:
            self._copy_comments(src_content, dst_id, expand=expstr)

        # copy labels if specified
        if cpy_labels:
            self._copy_labels(src_content, dst_id, expand=expstr)

        # copy child pages recursively
        src_id = src_content['id']
        pg_type = 'page'
        kids = self.__api.get_content_children_by_type(content_id=src_id, child_type=pg_type)
        kid_results = kids.get('results', None)

        if kids and kid_results:
            for kid in kid_results:
                new_spec = {
                    'content_id': kid['id'],
                    'content_type': kid['type'],
                    'expand': expstr,
                }

                self._copy(
                    new_spec, dst_id, dst_space_key, kid['title'],
                    rename=rename,
                    rename_limit=rename_limit,
                    overwrite=overwrite
                )
        return

    # TODO: move to copier command class
    @debug_log_call()
    def _copy_attachments(self, src_content, dst_id, expand=None):
        """
        Copy the attachments of a given page to the page with the given id.

        Copy will be done in a temporary directory for now.

        TODO: Add support for other kwargs:
            download_dir (configurable location for attachment downloads, needs
            to be writable by user of atrest)
            delete_downloads (a way to specify delete/keep downloaded files)
        """
        # TODO: Do we actually need to return anything here?
        src_id = src_content.get('id', None)
        if src_id is None:
            logging.error('Attempted copy attachments with no id specified!')
            return False

        src_attachs = self.get_attachments_for_id(src_id, expand=expand)

        dst_attachs = []
        dst_atitles = []

        if self.__mode != ClientMode.dry_run:
            # dst_id is likely DRY_RUN_ID if we are in a dry run, so the call
            # to get by id will fail in that case. if not, try to call
            dst_attachs = self.get_attachments_for_id(dst_id, expand=expand)
            dst_atitles = [a['title'] for a in dst_attachs]

        # TODO: if/when the ability to specify a download dir and/or keeping
        #       of downloaded attachments, this will need to change. Using
        #       TemporaryDirectory and with statement will remove the dir and
        #       contents
        # TODO: break this horrid thing up
        with TemporaryDirectory() as tmp_dl_dir:
            for sattach in src_attachs:
                dl_path = None
                if self.__mode == ClientMode.dry_run:
                    logging.info('Dry run _copy_attachments. Faking download path')
                    dl_path = 'FAKE_PATH'
                else: # real run
                    dl_path = self._download_attachment(sattach, tmp_dl_dir)

                if dl_path:
                    sattach_title = sattach.get('title', None)
                    try:
                        attach_idx = dst_atitles.index(sattach_title)
                        attach_exists_msg = \
                            'Source attachment %s exists in destination ' \
                            'content already. Updating with downloaded ' \
                            'version.'
                        logging.debug(attach_exists_msg, sattach_title)

                        if self.__mode == ClientMode.dry_run:
                            logging.info('Dry run: would update existing attachment with downloaded version')
                        else:
                            with open(dl_path, 'rb') as dl:
                                self.__api.update_attachment(
                                    content_id=dst_id,
                                    attachment_id=dst_attachs[attach_idx]['id'],
                                    attachment={'file': dl}
                                )
                    except ValueError as e:
                        # the title for the source attachment was not found in
                        # the destination attachment titles. it means we don't
                        # have to update an existing attachment and can just
                        # add it to the dst
                        logging.debug('Creating attachment %s for destination content', sattach_title)

                        if self.__mode == ClientMode.dry_run:
                            logging.info('Dry run: would add new attachment')
                        else:
                            with open(dl_path, 'rb') as dl:
                                self.__api.create_new_attachment_by_content_id(
                                    content_id=dst_id,
                                    attachments={'file': dl}
                                )
        return True

    # TODO: make this part of public api
    @handles_httperror
    @debug_log_call()
    def _download_attachment(self, attach_content, dl_dir):
        """
        Download an attachment specified by attach_content (usually returned by
        a call to the Confluence REST API) to the directory dl_dir.
        """
        # TODO: Error check args and vals below
        dl_file_path = None
        attach_name = attach_content.get('title', None)

        logging.debug(
            'Downloading attachment %s to dir %s',
            attach_name,
            dl_dir
        )

        # get the download link minus the preceeding '/'
        dl_link = attach_content['_links']['download'][1:]
        dl_cntnt = self.__api._service_get_request(sub_uri=dl_link, raw=True)
        dl_file_path = os.path.join(dl_dir, attach_name)
        with open(dl_file_path, 'wb') as f:
            f.write(dl_cntnt)
        logging.debug('Download completed')
        return dl_file_path


    # TODO: move to copier command class
    @debug_log_call()
    def _copy_comments(self, src_content, dst_id, expand=None):
        """
        Copy the comments of a given page to the page with the given id.
        E.g. if this is used as part of a page copy function, src_content
        should have the comments expanded and the copied page id would be
        dst_id.
        """
        # TODO: this getattr/check/log/return boilerplate is all over the
        #       place. fix that
        src_id = src_content.get('id', None)
        if src_id is None:
            logging.error('Attempted copy comments with no id specified!')
            return False

        # TODO: this is overriding the passed in kwarg expand, this should
        #       come from outside this method
        expstr = 'container,body.storage'
        src_comments = self.get_comments_for_id(src_id, expand=expstr)

        # TODO: watch for dry run id
        # TODO: need expand here?
        for cmnt in src_comments:
            # TODO: log c or something?
            c = self.create_new_comment_for_content_id(
                dst_id,
                cmnt['title'],
                cmnt['body']['storage']['value']
            )
        return True

    @debug_log_call()
    def create_new_comment_for_content_id(self, dst_id, title, comment_val):
        """
        Add a new comment to the content with id dst_id. The comment will have
        the title and value given.

        NOTE: The comment_val value should be an HTML snippet in <p> tags.

        NOTE: This will not add comments to attachments, or anything else that
              stores comments in the metadata field as opposed to storing them
              as child types.
        """
        # TODO: make work with non-HTML formatted strings. seems to work ok
        #       with plain text values, but not sure the implications
        # TODO: add mechanism to add comments to oddballs like attachments
        # TODO: real close to how copy page works. refactor that...

        # TODO: what is the bare minimum of the dst_content that's required for
        #       a comment's container?
        dst_content = {}
        dst_space = None
        if self.__mode == ClientMode.real_run:
            dst_content = self.content_exists(content_id=dst_id)

            # TODO: getting the space name here is needed because the __api call
            #       for create_new_content requires it. fork that repo and add a
            #       method to make a new comment for content id and remove it from
            #       the content_dict below
            dst_space = dst_content['space']['key']

        new_cmnt = {}
        content_dict = {
            'type':'comment',
            'title': title,
            'space': {
                'key': dst_space,
            },
            'container': dst_content,
         	'body': {
                'storage': {
                    'value': comment_val,
                    'representation': 'storage'
                },
            },
        }

        if self.__mode == ClientMode.dry_run:
            new_cmnt = content_dict.copy()
            new_cmnt.update({'id': DRY_RUN_ID})
            logging.info('Dry run create_new_comment_for_content_id. Returning fake new comment %s', new_cmnt)
        else:
            new_cmnt = self.__api.create_new_content(content_dict)
        return new_cmnt


    # TODO: move to copier command class
    @debug_log_call()
    def _copy_labels(self, src_content, dst_id, expand=None):
        """
        Copy the labels of a given page to the page with the given id.
        E.g. if this is used as part of a page copy function, src_content
        should have the labels expanded and the copied page id would be
        dst_id.
        """
        # TODO: check for self.DRY_RUN_ID for dst_id

        # TODO: this getattr/check/log/return boilerplate is all over the
        #       place. fix that
        src_id = src_content.get('id', None)
        if src_id is None:
            logging.error('Attempted copy labels with no id specified!')
            return False

        # TODO: this is overriding the passed in kwarg expand, this should
        #       come from outside this method
        src_labels = self.get_labels_for_id(src_id)

        label_copies = [
            {'prefix': l['prefix'], 'name': l['name']} for l in src_labels
        ]

        if not len(label_copies):
            # no labels, no copy.
            return

        # TODO: Make a property for mode
        if self.__mode == ClientMode.dry_run:
            logging.info('Dry run _copy_labels. Would copy: %s', label_copies)
        else:
            self.__api.create_new_label_by_content_id(content_id=dst_id, label_names=label_copies)
        # TODO: need to return anything of interest? standardize returns...

    # TODO: move to copier command class
    @debug_log_call()
    def _copy_page(self, src_content, dst_parent_id, dst_space_key, dst_title, expand=None):
        """
        Copy a page (represented by src_content) as a child of the page
        specified dst_parent_id, in the space dst_space_key with the title
        dst_title.
        """
        logging.debug('Attempting copy of page.')
        logging.debug(
            '\tsrc [Space: %s Content: %s]',
            src_content['space']['key'],
            src_content['title'],
        )
        logging.debug(
            '\tdst [Space: %s Parent ID: %s Title: %s]',
            dst_space_key,
            dst_parent_id,
            dst_title,
        )

        cpy = {}
        # TODO: method or something for making this
        content_dict = {
            'type': src_content['type'],
            'title': dst_title,
            'ancestors': [
                {
                    'id': dst_parent_id,
                },
            ],
            'space': {
                'key': dst_space_key,
            },
            'body': {
                'storage': src_content['body']['storage'],
            },
        }

        # TODO: Make a property for mode
        if self.__mode == ClientMode.dry_run:
            logging.info('Dry run _copy_page. Returning fake copy')
            cpy = content_dict.copy()
            cpy.update({'id': DRY_RUN_ID})
        else:
            cpy = self.__api.create_new_content(content_dict)
        return cpy

    # TODO: make part of public api
    @debug_log_call()
    def _get_content_title(self, space_key, title, rename=True, rename_limit=100, overwrite=False):
        """
        See if the content name 'title' exists in the space already. If not,
        return it. If so, attempt to overwrite (not yet implemented) or find
        a new name for the page if the flag is set. Return None if no suitable
        name can be found.
        """
        # TODO: this method feels wrong (complicated). refactor
        tmp_title = title
        logging.debug(
            'Checking for new title [%s] in destination space [%s]',
            space_key,
            tmp_title,
        )
        new_content = self.content_exists(space_key=space_key, title=tmp_title)

        if new_content is not None:
            logging.warning(
                'Content with name [%s] already exists in %s',
                space_key,
                tmp_title,
            )

            if overwrite:
                # TODO: implement overwrite
                logging.error(
                    'Overwriting of content with existing title not yet ' \
                    'supported, moving on to see if renaming is also an option'
                )

            if rename:
                # append a counter to the content title until we find one we
                # can use
                rename_title = ''
                for cntr in range(rename_limit):
                    rename_title = '%s %i' % (tmp_title, cntr)
                    logging.debug(
                        'Checking for new title [%s] in destination space [%s]',
                        rename_title,
                        space_key,
                    )
                    new_content = self.content_exists(
                        space_key=space_key,
                        title=rename_title
                    )
                    if new_content is None:
                        # we should have a good title now.
                        tmp_title = rename_title
                        break

                    if cntr == rename_limit-1:
                        logging.error(
                            'Hit max number of rename attempts (%i). ' \
                            'Aborting operation', rename_limit
                        )
                        return None
            else:
                # renaming wasn't specified, so we should fail the operation
                logging.error(
                    'Content with title [%s] exists in space [%s] and ' \
                    'renaming was not specified. Aborting operation',
                    tmp_title, space_key
                )
                return None
        return tmp_title

# TODO: consider separate classes for expand str building (or make a
#       configurable member of the action classes discussed in other TODOs)...
    @debug_log_call()
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

    # TODO: move to copier command class
    # TODO: move this methods to somewhere else? make a spec class for
    #       ConfluenceAPI calls and extend for specific operations (like
    #       get/create new content, copy src/dst, etc)?
    @debug_log_call()
    def get_default_specs(self):
        """
        Gets a empty dictionaries for copy specs (to and from copying). These
        are returned as a tuple.

        src_spec keys:
            content_id: The id of the piece of content to copy. If this is provided, it
                will be used instead of space key and page title
            space_key: The space key where the content to copy lives in. If this is
                  provided, the title must also be provided.
            title: The name of the piece of content to copy. E.g. if the
                   content is a page, then it is the page title.
            type: The type of the piece of content to copy. E.g. 'page',
                  'attachment', 'comment', 'blogpost', etc. This is optional
                  and will default to 'page' if not specified.
            children: Dict with keys (values apply to all children of content
                      being copied):
                page: True if child pages should be copied as well, False
                      otherwise (defaults to True if not provided).
                attachment: True if attachments should be copied as well, False
                         otherwise (defaults to True if not provided)
                comment: True if content comments should be copied as well,
                         False otherwise (defaults to True if not provided).
                NOT YET SUPPORTED:
                labels: True if content comments should be copied as well,
                         False otherwise (defaults to True if not provided).
        NOTE: the children key above may be replaced with a configurator for
              the types of things to expand for each content type

        dst_spec keys:
            content_id: The id of the content to copy to (the parent of the new
                content). If this is provided, it will be used instead of
                space key and page title
            space_key: The space key where the parent to copy to lives in. If this
                   is provided, the title must also be provided.
            title: The name of the parent content to copy to. E.g. if the
                    content to be the parent is a page, then it is the page
                    title.
            content_copy: Dict with keys:
                title: The title for the new page. If not provided, the title
                       from the source content will be attempted. In case of
                       naming conflicts, something will be done. Not sure what
                       yet.
                rename: True if the given title for the new content should be
                        renamed if the provided title exists. False otherwise.
                        Defaults to True.
                        If overwrite is True, this won't matter. Otherwise, if
                        this is True, the given title will have an incrementing
                        number appended until the title is not used. If this
                        is False and overwrite is False, the copy will fail.
                rename_limit: number of time to attempt a rename
                NOT YET SUPPORTED
                overwrite: True if this should overwrite existing content with
                           the title given for the new content. False otherwise.
                           Defaults to False
        """
        src_spec = {
            'content_id': None,
            'space_key': None,
            'type': 'page',
            'title': None,
            'children': {
                'page': True,
                'attachment': True,
                'comment': True,
            },
        }

        dst_spec = {
            'content_id': None,
            'space_key': None,
            'type': 'page',
            'title': None,
            'content_copy': {
                'title': None,
                'overwrite': False,
                'rename': True,
                'rename_limit': 100,
            },
        }

        return (src_spec, dst_spec)
