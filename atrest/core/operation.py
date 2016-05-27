from traitlets import (
    Instance, Unicode, default
)

from atrest.core.application import (
    AtRESTCLIApplication,
)

from atrest.core.clientbase import (
    AtRESTClientBase,
)

co_extra_aliases = {
    'username' : 'AtRESTClientOperation.username',
    'apiurlbase' : 'AtRESTClientOperation.api_url_base',
}


# TODO: this name is bad/potentially misleading. Need a base for API commands, but cliapplication is the base for everything else. what's using a REST api to

class AtRESTOperationBase(AtRESTCLIApplication):
    """
    Base class for all AtREST REST API operations. An operation is something
    that uses an API to make calls to a REST interface and does some thing.

    NOTE: Subclasses are not meant to be used on their own as a stand alone
          application. An AtRESTClientBase subclass is needed to perform
          operations. This is possible to put together, but it's not the
          intent. This is meant to be used by AtRESTClientBase subclass
          instantiations.
    """

    name = 'atrest-base-operation'

    description = """AtREST base Operation that can be run interactively.
    TODO: Add more description...
    """

    examples = """
    TODO: Add examples.
    """

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)

    def do_operation(self):
        """
        """
        raise NotImplementedError

    def _start_normal(self):
        """
        """
        self.do_operation()


class AtRESTClientOperation(AtRESTOperationBase):
    """
    Base class for all AtREST REST API operations requiring an API client.
    A client operation is something that uses an API to make calls to a REST
    interface using an api client and does some thing.

    NOTE: Subclasses are not meant to be used on their own as a stand alone
          application. An AtRESTClientBase subclass is needed to perform
          operations. This is possible to put together, but it's not the
          intent. This is meant to be used by AtRESTClientBase subclass
          instantiations.
    """

    name = 'atrest-client-operation'

    description = """AtREST base Client Operation that can be run
    interactively.
    TODO: Add more description...
    """

    examples = """
    TODO: Add examples.
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


    # TODO: Should this be passed in as needed rather than stored?.
    apiclient = Instance(AtRESTClientBase,
        allow_none=True,
        help='the api client for the operation'
    )

    def __init__(self, *args, **kwargs):
        """
        """
        super().__init__(*args, **kwargs)
        self.update_aliases(co_extra_aliases)

    # def initialize(self, *args, **kwargs):
    #     """
    #     Initialize the operation.
    #     """
    #     # TODO: do we need to parse command line in all applications?
    #     # self.parse_command_line
    #     super().initialize(*args, **kwargs)

    # start (and this start_interactive and _start_normal) should call a method
    # where the magic should happen...
