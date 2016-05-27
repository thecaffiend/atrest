import getpass
import sys

from traitlets.config.configurable import Configurable
from traitlets import (
    Enum as TraitletEnum, Unicode, default,
)

from atrest.core.application import (
    AppRunMode,
    AtRESTCLIApplication,
)

# TODO: extra aliases or flags?
rc_extra_aliases = {
    'username' : 'AtRESTClientBase.username',
    'apiurlbase' : 'AtRESTClientBase.api_url_base',
}

# rc_extra_flags = dict(
#     # Format:
#     #flag = ({'ClassName' : {'trait' : value}},
#     #    "flag help string"),
# )


class AtRESTClientBase(AtRESTCLIApplication):
    """
    Base class for all Atlassian REST API Clients.
    """
    username = Unicode(help='The username for API auth.').tag(config=True)

    @default('username')
    def _username_default(self):
        """
        """
        return input('Please enter username: ')
        # un = ''
        # if self.interactive:
        #     un = input('Please enter username: ')
        # else:
        #     self.log.error('No username specified for REST Client')
        # return un

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
        """
        return input('Please enter the base URL for the API: ')

        # baseurl = ''
        # if self.interactive:
        #    baseurl = input('Please enter the base URL for the API: ')
        # else:
        #     self.log.error('No API URL specified for REST Client')
        # return baseurl

    # TODO: We don't want it configurable, but being able to specify a trait
    #       like `__api = Type(SomeAPIBase, help="the api object to use")`
    #       would be spiffy. there is no base class for Confluence/Jira/Stash
    #       etc apis though.

    def __init__(self, *args, **kwargs):
        """
        Init method for class. Nothing special.
        """
        self.update_aliases(rc_extra_aliases)

        super().__init__(*args, **kwargs)

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
        if the __api member is initialized and False otherwise.
        """
        return True if self._api else False

    def initialize(self, *args, **kwargs):
        """
        Initialize the client.
        """
        # LEFTOFF
        # NOTE: To get subapps and such, parse_command_line must be done
        self.parse_command_line(argv=kwargs.get('argv', None))

        if self.subapp:
        # starting a subapp, no need to init
            return

#        self.initialize_api()

    def initialize_api(self, username=None, apiurlbase=None):
        """
        Method to initialize the REST API. All subclasses should implement this
        method, and it is assumed they will all require a username, password,
        and url_base for the API of interest.
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
        """
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
#            self.initialize_api()
            self._start_normal()
