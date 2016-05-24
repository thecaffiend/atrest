import enum
import getpass

from traitlets.config.configurable import Configurable
from traitlets import (
    Enum as TraitletEnum, Unicode, default,
)

from atrest.core.application import (
    AtRESTCLIApplication,
)

class ClientRunMode(enum.Enum):
    """
    Enum for the mode to operate in. dry_run only logs what would happen.
    real_run does it for realz...
    """
    dry_run = 0
    real_run = 1

# TODO: extra aliases or flags?
rc_extra_aliases = {
    'username' : 'AtRESTClientBase.username',
    'api-url-base' : 'AtRESTClientBase.api_url_base',
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
    mode = TraitletEnum(ClientRunMode,
        default_value=ClientRunMode.dry_run,
        help='the run mode of the client'
    ).tag(config=True)

    username = Unicode(help='The username for API auth.').tag(config=True)

    @default('username')
    def _username_default(self):
        """
        """
        un = None
        if self.interactive:
            un = input('Please enter username: ')
        else:
            # TODO: has this had a chance to config yet (from file or cmd line
            #       args)? If so, this is ok to return None, as it will cause
            #      a trait error.
            self.log.error('No username specified for REST Client')
        return un

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
        baseurl = None
        if self.interactive:
            baseurl = input('Please enter the base URL for the API: ')
        else:
            # TODO: has this had a chance to config yet (from file or cmd line
            #       args)? If so, this is ok to return None, as it will cause
            #      a trait error.
            self.log.error('No API URL specified for REST Client')
        return baseurl

    # TODO: We don't want it configurable, but being able to specify a trait
    #       like `__api = Type(SomeAPIBase, help="the api object to use")`
    #       would be spiffy. there is no base class for Confluence/Jira/Stash
    #       etc apis though.

    def __init__(self, *args, **kwargs):
        """
        Init method for class. Nothing special.
        """
        self.update_aliases(rc_extra_aliases)

        m = kwargs.pop('mode', None)
        if m:
            self.mode = m
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
        Initialize the client. Assumes username and api_url_base have been set
        """
        # TODO: do we need to parse command line in all applications?
        # self.parse_command_line
        super().initialize(*args, **kwargs)
        pw = self._get_password()
        if not pw:
            # can't connect the client without a password.
            self.log.error('Could not get password for the REST client. Exiting')
            # TODO: is this too harsh? easier way to handle?
            system.exit(-1)

        self._initialize_api(pw)

    def _initialize_api(self, password):
        """
        Method to initialize the REST API. All subclasses should implement this
        method, and it is assumed they will all require a username, password,
        and url_base for the API of interest.
        """
        # TODO: See if it makes sense to allow params other than
        #       username/password for some APIs. Like a token or something else
        #       more secure.
        raise NotImplementedError

    def _get_password(self):
        """
        Prompt the user for a password.
        """
        # TODO: will this work in interactive and non interactive modes?
        return getpass.getpass('Please enter password for REST API: ')
