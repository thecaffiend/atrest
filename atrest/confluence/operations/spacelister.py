from pprint import pprint as pp

from traitlets import (
    Unicode
)

from atrest.core.operation import (
    AtRESTClientOperation,
)

sl_extra_aliases = {
    'filter': 'SpaceLister.filter_str',
}

# TODO: fix to not need __init__ (don't rely on update_aliases/flags)

class SpaceLister(AtRESTClientOperation):
    """
    Trivial implementation of a Confluence operation. This one just gets spaces
    from the REST API and prints them.
    """

    name = 'atrest-confluence-spaces'

    description = """Trivial implementation of a Confluence operation as an
    example. This operation prompts for username and API URL base (if not
    provided on command line or in a config file) and then gets a list of
    spaces from the Confluence REST API (filtering if requested) and prints
    them.
    """

    examples = """
    show help:
        atrest confluence spaces --help
    list all spaces the user is allowed to see (prompt for username/url/password):
        atrest confluence spaces
    list all spaces the user is allowed to see with filtering:
        atrest confluence spaces filter=space1,space2
    list all spaces the user is allowed to see (specify username/url):
        atrest confluence spaces --username=myusername --apiurlbase=http://server/confluence
    """
    filter_str = Unicode(u'',
        help="Comma separated list of space keys to filter by (no spaces).").tag(config=True)

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        self.update_aliases(sl_extra_aliases)

    def initialize(self, *args, **kwargs):
        """
        Initialize the operation.
        """
        self.parse_command_line(argv=kwargs.get('argv', None))

    def do_operation(self):
        """
        List the spaces we get back, filtered on the self.space_filter list
        """
        space_filter = self.filter_str.split(',') if self.filter_str else None
        print('Looking for spaces using space_filter: %s' % (space_filter))
        spaces = self.apiclient.get_space_names(space_filter=space_filter)
        pp('Spaces found by SpaceLister: %s' % (spaces))

    def start(self):
        """
        Override of Application start method. By default, just checks if we are
        to be run interactively or not and goes from there.
        """

        self.log.debug(
            'Starting SpaceLister app in interactive mode: %s',
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
        In normal mode, just list the spaces we get back
        """
        if not self.apiclient.status:
            # try to initialize the apiclient
            self.apiclient.initialize_api(username=self.username, apiurlbase=self.api_url_base)
        self.do_operation()

    def _start_interactive(self):
        """
        """
        raise NotImplementedError
