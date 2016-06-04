from traitlets import (
    Dict, Instance, Unicode, default
)

from atrest.core.application import (
    AtRESTCLIApplication,
    cli_aliases, # TODO: cleaner way to do this, like a base class method...
    cli_flags, # TODO: cleaner way to do this, like a base class method...
)

from atrest.core.clientbase import (
    AtRESTClientBase,
)

# TODO: clean this implementation up for the classes here and subclasses
op_aliases = {}
op_aliases.update(cli_aliases)

op_flags = {}
op_flags.update(cli_flags)

client_op_aliases = {
    'username' : 'AtRESTClientOperation.username',
    'apiurlbase' : 'AtRESTClientOperation.api_url_base',
}
client_op_aliases.update(cli_aliases)

client_op_flags = {}
client_op_flags.update(cli_flags)


# TODO: this name is bad/potentially misleading. Need a base for general
#       operations (e.g. something that calls a bash script), REST API
#       operations (like the space lister or page copier), etc, but
#       cliapplication is the base for everything else.

class AtRESTOperationBase(AtRESTCLIApplication):
    """
    Base class for all AtREST operations. An operation is something that does
    some thing in the context of AtREST or one of it's subcommands.
    """

    name = 'atrest-operationbase'

    description = """Base class for AtREST Operations that can be run
    interactively. This should not be used as is, but should be subclassed.
    """

    examples = """
    Base class has no examples
    """

    # TODO: provide methods in the base classes for getting their flags/aliases
    #       as dicts, update sub classes using these.
    aliases = Dict(op_aliases)
    flags = Dict(op_flags)

    # def __init__(self, *args, **kwargs):
    #     """
    #     """
    #     super().__init__(*args, **kwargs)

    def do_operation(self):
        """
        This is where the main operation code should go. In general, this
        will likely be called by _start_normal at least (and probably
        _start_interactive at some point like after interactive configuration).
        """
        raise NotImplementedError

    def _start_normal(self):
        """
        Start in normal (non-interactive) mode. Calling do_operation is the
        minimal case, and most of the time this may be sufficient.
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

    name = 'atrest-clientoperation'

    description = """Base class for AtREST Client Operations that can be run
    interactively. This should not be used as is, but should rather be
    subclassed.
    """

    examples = """
    Base class has no examples.
    """

    # TODO: provide methods in the base classes for getting their flags/aliases
    #       as dicts, update sub classes using these.
    aliases = Dict(client_op_aliases)
    flags = Dict(client_op_flags)

    # username for REST API authentication
    username = Unicode(u'',
        help='The username for API auth.').tag(config=True)

    @default('username')
    def _username_default(self):
        """
        Called if username is accessed before it's been assigned a value.
        """
        return input('Please enter username: ')

    # TODO: for now, the server address is just a unicode string. look into
    #       finding/making traitlets for real server values (urls, ports,
    #       prefixes, etc). Jupyterhub uses something called URLPrefix in their
    #       version of traitlets for example.
    api_url_base = Unicode(u'',
        help='The base url for the REST API (up to but not including /rest/)'
    ).tag(config=True)

    @default('api_url_base')
    def _api_url_base_default(self):
        """
        Called if api_url_base is accessed before it's been assigned a value.
        """
        return input('Please enter the base URL for the API: ')

    # TODO: Should this be passed in as needed rather than stored?.
    # TODO: Any reason to make this readonly (see traitlets doc)?
    apiclient = Instance(AtRESTClientBase,
        allow_none=True,
        help='the api client for the operation'
    )

# TODO: remove if not needed
    # def __init__(self, *args, **kwargs):
    #     """
    #     """
    #     super().__init__(*args, **kwargs)
    #     self.update_aliases(co_extra_aliases)
