from tempfile import TemporaryDirectory

from traitlets import (
    Bool, Dict, Integer, Unicode,
)

from atrest.core.operation import (
    AtRESTClientOperation,
    client_op_aliases,
    client_op_flags,
)

from atrest.core.application import (
    AppRunMode,
)

from atrest.utils.decorators import (
    debug_log_call,
)

# TODO: add aliases as needed
copy_aliases = {
    'srckey' : 'PageCopier.source_space',
    'dstkey' : 'PageCopier.dest_space',
    'page' : 'PageCopier.source_page',
    'pageid' : 'PageCopier.source_content_id',
    'parentid' : 'PageCopier.dest_parent_id',
    'parent' : 'PageCopier.dest_parent',
    'title' : 'PageCopier.dest_title',
    'max_rename' : 'PageCopier.rename_limit',
}
copy_aliases.update(client_op_aliases)

# TODO: add flags as needed
copy_flags = dict(
    subpages = ({'PageCopier' : {'copy_subpages' : True}},
            "copy sub pages of source page"),
    attachments = ({'PageCopier' : {'copy_attachments' : True}},
            "copy attachments of all copied pages"),
    labels = ({'PageCopier' : {'copy_labels' : True}},
            "copy labels of all copied pages"),
    comments = ({'PageCopier' : {'copy_comments' : True}},
            "copy comments of all copied pages"),
    rename = ({'PageCopier' : {'rename_on_conflict' : True}},
            "attempt rename on destination name conflicts"),
    updateattach = ({'PageCopier' : {'update_attachments' : True}},
            "update existing attachments in destination if the already exist"),
    overwrite = ({'PageCopier' : {'overwrite_on_conflict' : True}},
            "NOT YET SUPPORTED - overwrite existing pages on destination name conflicts"),
)
copy_flags.update(client_op_flags)

class PageCopier(AtRESTClientOperation):
    """
    Class for copying pages withing Confluence. Can be recursive or not, and
    can get attachment, labels and comments on pages as well.

    NOTE: Maintaining history is not supported right now. Confluence limitation.
    """

    # TODO: benefit to making a base class for recurive operations?
    # TODO: Do we need a base class for copy of all content types, then
    #       subclass for specific things like pages, spaces, etc?

    name = 'atrest-confluence-copypage'

    description = """AtREST Confluence Operation for copying pages. May be done
    recursively or not, and can get attachments, labels and comments on pages
    as well.

    NOTE: Maintaining history is not supported right now. Confluence limitation
    """

    examples = """
    show help:
        atrest confluence copypage --help
    TODO: add other useful examples
    """

    aliases = Dict(copy_aliases)
    flags = Dict(copy_flags)

    source_space = Unicode(None, allow_none=True,
        help="The source space key of the page to copy.").tag(config=True)

    dest_space = Unicode(None, allow_none=True,
        help="The destination space key to copy page to.").tag(config=True)

    # TODO: change this to source_title
    source_page = Unicode(None, allow_none=True,
        help="The source page to copy.").tag(config=True)

    dest_parent = Unicode(None, allow_none=True,
        help="The destination page to be the parent of the copied page.").tag(config=True)

    dest_title = Unicode(None, allow_none=True,
        help="The title to try to use for the copied page. This will apply the the root only if copying subpages. If empty, the source pages title will be tried").tag(config=True)

    source_content_id = Unicode(None, allow_none=True,
        help="The content id of the page to be copied. If specified, source space key and source page title will be ignored.").tag(config=True)

    dest_parent_id = Unicode(None, allow_none=True,
        help="The content id of the page to be parent of copy. If specified, destination space key and destination parent title will be ignored.").tag(config=True)

    copy_subpages = Bool(False,
        help="True if all subpages should be copied.").tag(config=True)

    copy_attachments = Bool(False,
        help="True if attachments should be copied.").tag(config=True)

    update_attachments = Bool(False,
        help="True if existing attachments should be updated during copy.").tag(config=True)

    copy_labels = Bool(False,
        help="True if labels should be copied.").tag(config=True)

    copy_comments = Bool(False,
        help="True if comments should be copied.").tag(config=True)

    rename_on_conflict = Bool(False,
        help="Rename copied pages if there is a naming conflict in the destination space.").tag(config=True)

    rename_limit = Integer(100,
        help="Number of iterations for attempted renamings.").tag(config=True)

    overwrite_on_conflict = Bool(False,
        help="NOT YET SUPPORTED - Overwrite existing pages if there is a naming conflict in the destination space.").tag(config=True)

    # def __init__(self, *args, **kwargs):
    #     """
    #     TODO: add doc and describe params/returns
    #     """
    #     super().__init__(*args, **kwargs)
    #     self.update_aliases({{cookiecutter.operation_name}}_extra_aliases)
    #     self.update_flags({{cookiecutter.operation_name}}_extra_aliases)

    # TODO: only implement if you need to do something special for the class.
    #       this is called before start() and can do things like custom command
    #       line argument parsing/handling.
    # def initialize(self, *args, **kwargs):
    #     """
    #     Initialize the operation.
    #     """
    #     self.parse_command_line(argv=kwargs.get('argv', None))

    def do_operation(self):
        """
        Copy a content from one place to a new place.
        TODO: beter doc
        """
        print('Copying the things!')
        if not self._validate_values():
            self.log.error('Invalid configuration for copying page.')
            return

        # TODO: check the supported extra params of the api to see if any are
        #       needed
        try:
            if self.source_content_id:
                src_content = self.apiclient.get_content_by_id(self.source_content_id)
            else:
                src_content = self.apiclient.get_only_content(content_type='page', space_key=self.source_space, title=self.source_page)
        except ResultsException as e:
            return

        if not src_content:
            # log and bail
            self.log.error('Could not get source content to copy.')
            return

        parent_content = None
        dst_parent_id = self.dest_parent_id or None
        dst_parent_title = self.dest_parent or None
        dst_space_key = self.dest_space or None
        dst_page_title = self.dest_title or src_content['title']

        try:
            if dst_parent_id:
                # this will override other settings like dest space key and title
                parent_content = self.apiclient.get_content_by_id(dst_parent_id)
            else:
                if dst_space_key:
                    if dst_parent_title:
                        parent_content = self.apiclient.get_only_content(space_key=dst_space_key, title=dst_parent_title)
                    else:
                        parent_content = self.apiclient.get_space_homepage(dst_space_key)
                        dst_parent_title = parent_content['title']
                else:
                    parent_content = self.apiclient.get_parent_content_by_id(src_content['id'])
                    dst_space_key = parent_content['space']['key']
                    dst_parent_title = parent_content['title']
                dst_parent_id = parent_content['id']
        except ResultsException as e:
            self.log.error('Could not get parent content for new copy.')
            return


        self._copy(src_content['id'], dst_parent_id, dst_space_key, dst_page_title)

        return True

    @debug_log_call()
    def _copy(self, src_id, dst_parent_id, dst_space_key, dst_title):
        """
        Copy content with src_id to dest_parent_id
        """
        # TODO: check expand strings and other params supported by api
        # TODO: build expand strings smartly.

        # expand body.storage on the source so we have that for copying
        src_expand = 'body.storage'
        src_content = self.apiclient.get_content_by_id(src_id, expand=src_expand)

        # make sure the destination name is good
        valid_title = self.apiclient.check_content_title(
            dst_space_key,
            dst_title,
            rename=self.rename_on_conflict,
            rename_limit=self.rename_limit
        )
        self.log.debug('Got back valid title: %s', valid_title)
#        raise Exception
        if not valid_title:
            # TODO: make exceptions for content title errors
            self.log.error('Could not get a suitable title for the new content')
            return

        self.log.debug('Trying to copy the page [%s] as [%s]', src_content['title'], valid_title)
        copy_content = self._copy_page(src_content, dst_parent_id, dst_space_key, valid_title)

        if copy_content is None:
            copy_err = 'Could not copy page with args: \n\tsrc_content %s ' \
            '\n\tdst_parent_id %s \n\tdst_space_key %s \n\tvalid_title %s'
            self.log.error(
                copy_err, src_content, dst_parent_id, dst_space_key, valid_title
            )
            return

        self.log.debug('Copy succeded')

        dst_id = copy_content['id']

        # copy attachments if specified
        self.log.debug('Copying attachments: %s', self.copy_attachments)
        if self.copy_attachments:
            self._copy_attachments(src_id, dst_id)

        # copy comments if specified
        self.log.debug('Copying comments: %s', self.copy_comments)
        if self.copy_comments:
            self._copy_comments(src_id, dst_id)

        # copy labels if specified
        self.log.debug('Copying labels: %s', self.copy_labels)
        if self.copy_labels:
            self._copy_labels(src_id, dst_id)

        # copy child pages recursively
        self.log.debug('Copying subpages: %s', self.copy_subpages)
        if self.copy_subpages:
            kids = self.apiclient.get_content_children_by_type(content_id=src_id, child_type='page')

            for kid in kids:
                self._copy(kid['id'], dst_id, dst_space_key, kid['title'])

        self.log.debug('Done with copying...')

    def _validate_values(self):
        """
        Validate the current configured settings to make sure we have enough
        info to copy.
        """
        # content_id OR src space/page required
        if not self.source_content_id:
            if not self.source_space and not self.source_page:
                self.log.error(
                    'Must provide either the content id or the space and title of the page to copy.'
                )
                return False
        return True

    @debug_log_call()
    def _copy_page(self, src_content, dst_parent_id, dst_space_key, dst_title):
        """
        Copy a page (represented by src_content) as a child of the page
        specified dst_parent_id, in the space dst_space_key with the title
        dst_title.
        """

        cpy = self.apiclient.get_page_template(
                content_type=src_content['type'],
                space_key=dst_space_key,
                title=dst_title,
                parent_id=dst_parent_id,
                storage_val=src_content['body']['storage']
        )

        return self.apiclient.create_new_page(cpy)

        # Mode checking done in the apiclient
        # if self.apiclient.mode == AppRunMode.dry_run:
        #     self.log.info('Dry run _copy_page. Returning fake copy')
        #     cpy.update({'id': -1})
        # else:
        #     cpy = self.apiclient.create_new_page(cpy)
        # return cpy

    def _copy_attachments(self, src_id, dst_id):
        """
        Copy the attachments of the source to the destination.
        """
        src_attachs = self.apiclient.get_attachments_for_id(src_id)

        # TODO: all the mode checking should happen in the apiclient. if
        #       running this without an apiclient, we should require a
        #       self.mode
        if self.apiclient.mode == AppRunMode.dry_run:
            self.log.info('Dry run _copy_attachments from source [%s] to destination [%s]', src_id, dst_id)
            self.log.info('\tWould copy source attachments: %s', src_attachs)
            return

        # TODO: if/when the ability to specify a download dir and/or keeping
        #       of downloaded attachments, this will need to change. Using
        #       TemporaryDirectory and with statement will remove the dir and
        #       contents
        with TemporaryDirectory() as tmp_dl_dir:
            for sattach in src_attachs:
                dl_path = self.apiclient.download_attachment_by_id(sattach['id'], tmp_dl_dir)

                if dl_path:
                    self.apiclient.add_attachment(dst_id, dl_path, title=sattach['title'], update_existing=self.update_attachments)


    def _copy_comments(self, src_id, dst_id):
        """
        Copy the comments of content src_id to dst_id.
        """
        src_comments = self.apiclient.get_comments_for_id(src_id, expand='container,body.storage')

        if self.apiclient.mode == AppRunMode.dry_run:
            self.log.info('Dry run _copy_comments from source [%s] to destination [%s]', src_id, dst_id)
            self.log.info('\tWould copy source attachments: %s', src_comments)
            return

        for cmnt in src_comments:
            c = self.apiclient.add_comment(
                dst_id,
                cmnt['title'],
                cmnt['body']['storage']['value']
            )

    def _copy_labels(self, src_id, dst_id):
        """
        Copy the labels of content src_id to the destination dst_id.
        """
        src_labels = self.apiclient.get_labels_for_id(src_id)

        label_copies = [
            {'prefix': l['prefix'], 'name': l['name']} for l in src_labels
        ]

        if not label_copies:
            # no labels, no copy.
            return

        if self.apiclient.mode == AppRunMode.dry_run:
            self.log.info('Dry run _copy_labels. Would copy: %s', label_copies)
        else:
            self.apiclient.add_labels(dst_id, label_copies)

    def start(self):
        """
        Override of Application start method.
        """

        self.log.debug(
            'Starting PageCopier app in interactive mode: %s',
            self.interactive
        )

        if self.subapp:
            self.subapp.start()
            return

        if self.interactive:
            self._start_interactive()
        else:
            self._start_normal()

    def _start_normal(self):
        """
        TODO: Document the non-interactive execution.
        """
        if not self.apiclient.status:
            # try to initialize the apiclient
            self.apiclient.initialize_api(
                username=self.username,
                apiurlbase=self.api_url_base
            )
        self.do_operation()

    # TODO: Implement this. This should provide a cli for interactively
    #       performing the operation (printing help, prompting for param
    #       values, calling subcommands, etc). If nothing special is needed
    #       before starting, just call self.do_operation.
    def _start_interactive(self):
        """
        TODO: Document the interactive execution.
        """
        raise NotImplementedError
