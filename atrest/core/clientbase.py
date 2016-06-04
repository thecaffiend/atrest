import getpass

from traitlets import (
    Dict, Unicode, default,
)

from atrest.core.application import (
    AtRESTCLIApplication,
    cli_aliases, # TODO: cleaner way to do this, like a base class method...
    cli_flags, # TODO: cleaner way to do this, like a base class method...
)

from atrest.core.exception import (
    ResultsException,
)

client_aliases = {
    'username' : 'AtRESTClientBase.username',
    'apiurlbase' : 'AtRESTClientBase.api_url_base',
}
client_aliases.update(cli_aliases)

client_flags = {
}
client_flags.update(cli_flags)

class AtRESTClientBase(AtRESTCLIApplication):
    """
    Base class for all Atlassian REST API Clients.
    """

    name = 'atrest-clientbase'

    description = """Base class for AtREST REST API Clients that can be run
    interactively. This should not be used as is, but should be subclassed.
    """

    examples = """
    Base class has no examples
    """

    aliases = Dict(client_aliases)
    flags = Dict(client_flags)

    # TODO: AtRESTClientOperation also has this username/url need. Figure how
    #       to define just one place.

    username = Unicode(u'',
        help='The username for API auth.').tag(config=True)

    @default('username')
    def _username_default(self):
        """
        Called if username is accessed before it's given a value.
        """
        return input('Please enter username: ')

    # TODO: for now, the server address is just a unicode string. look into
    #       finding/making traitlets for real server values (urls, ports,
    #       prefixes, etc). Jupyterhub uses something called URLPrefix in their
    #       version of traitlets for example.
    api_url_base = Unicode(
        help='The base url for the REST API server (up to but not including /rest/)'
    ).tag(config=True)

    @default('api_url_base')
    def _api_url_base_default(self):
        """
        Called if api_url_base is accessed before it's given a value.
        """
        return input('Please enter the base URL for the API: ')

    # TODO: We don't want it configurable, but being able to specify a trait
    #       like `_api = Type(SomeAPIBase, help="the api object to use")`
    #       would be spiffy. there is no base class for Confluence/Jira/Stash
    #       etc apis though.

    def __init__(self, *args, **kwargs):
        """
        Initializer for class. Nothing special.
        """
        self._api = None

    @property
    def api(self):
        """
        Wrapped API property getter
        """
        #TODO: THIS IS JUST FOR TESTING. REMOVE IT. TOO MUCH INFO IS AVAILABLE
        #      TO INTERACTIVE ENVIRONMENTS WHEN THIS IS EXPOSED (E.G.
        #      PASSWORDS)
        return self._api

    @property
    def status(self):
        """
        status property getter. return tuple of (bool, msg) where bool is True
        if the _api member is initialized and False otherwise.
        """
        return True if self._api else False

# TODO: test if we need this or not
    def initialize(self, *args, **kwargs):
        """
        Initialize the client.
        """
        # NOTE: To get subapps and such, parse_command_line must be done
        self.parse_command_line(argv=kwargs.get('argv', None))

        if self.subapp:
        # starting a subapp, no need to init
            return

    def initialize_api(self, username=None, apiurlbase=None):
        """
        Method to initialize the REST API. All subclasses should implement this
        method, and it is assumed they will all require a username, password,
        and base url for the API of interest.
        """
        # TODO: See if it makes sense to allow params other than
        #       username/password for some APIs. Like a token or something else
        #       more secure.
        raise NotImplementedError

    def get_password(self):
        """
        Prompt the user for a password.
        """
        # TODO: will this work in interactive and non interactive modes?
        return getpass.getpass('Please enter password for REST API: ')

    def start(self):
        """
        Override of Application start method. By default, just checks if we are
        to be run interactively or not and goes from there.
        """
        self.log.debug(
            'Starting AtRESTClientBase app in interactive mode: %s',
            self.interactive
        )

        if self.subapp:
            # TODO: doing a hasattr check feels wrong here. shouldn't require
            #       all subapps to necessarily have a reference to the API
            #       client though. better way?
            if hasattr(self.subapp, 'apiclient'):
                self.subapp.apiclient = self
            self.subapp.start()
            return

        if self.interactive:
            self._start_interactive()
        else:
            self._start_normal()
