import enum

from traitlets.config.configurable import Configurable
from traitlets import (
    Enum as TraitletEnum,
    Unicode,
)

class ClientRunMode(enum.Enum):
    """
    Enum for the mode to operate in. dry_run only logs what would happen.
    real_run does it for realz...
    """
    dry_run = 0
    real_run = 1

# TODO: add a traitlets.config.loader.PyFileConfigLoader to this class.
#       when implemented, the controlling application should load the
#       config, but until then, the clients should do so themselves.
class AtRESTClientBase(Configurable):
    """
    Base class for all Atlassian REST API Clients.
    """
    mode = TraitletEnum(ClientRunMode,
        default_value=ClientRunMode.dry_run,
        help='the run mode of the client'
    ).tag(config=True)

    username = Unicode(help='The username for API auth.').tag(config=True)

    # TODO: for now, the server address is just a unicode string. look into
    #       finding/making traitlets for real server values (urls, ports,
    #       prefixes, etc). Jupyterhub uses something called URLPrefix in their
    #       version of traitlets for example.
    api_url_base = Unicode(
        help='The base url for the REST API server (up to but not including /rest/)'
    ).tag(config=True)

    # TODO: We don't want it configurable, but being able to specify a trait
    #       like `__api = Type(SomeAPIBase, help="the api object to use")`
    #       would be spiffy. there is no base class for Confluence/Jira/Stash
    #       etc apis though.

    def __init__(self, *args, **kwargs):
        """
        Init method for class. Nothing special.
        """
        m = kwargs.get('mode', None)
        if m:
            self.mode = m
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


    def initialize_api(self, username, password, url_base, *args, **kwargs):
        """
        Method to initialize the REST API. All subclasses should implement this
        method, and it is assumed they will all require a username, password,
        and url_base for the API of interest.
        """
        # TODO: See if it makes sense to allow params other than
        #       username/password for some APIs. Like a token or something else
        #       more secure.
        raise NotImplementedError
