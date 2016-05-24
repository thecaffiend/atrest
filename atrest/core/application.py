import logging

from traitlets.config.application import Application
from traitlets import (
    Unicode, List, Dict, Bool, 
)

from atrest import __version__ as atrest_version

base_aliases = {
    'log-level' : 'Application.log_level',
    'config' : 'AtRESTApplicationBase.config_file',
}

base_flags = dict(
    debug = ({'Application' : {'log_level' : logging.DEBUG}},
            "set log level to logging.DEBUG (most output)"),
    quiet = ({'Application' : {'log_level' : logging.CRITICAL}},
            "set log level to logging.CRITICAL (least output)"),
)

cli_extra_aliases = {
    'interactive' : 'AtRESTCLIApplication.interactive',
}

# TODO: is there a way to specify both a single char and full flag name
#       in a single element here (e.g. both i and interactive)? any
#       problems specifying 2 flags for the same thing if not?
cli_extra_flags = dict(
    interactive = ({'AtRESTCLIApplication' : {'interactive' : True}},
        "set application mode to interactive"),
    i = ({'AtRESTCLIApplication' : {'interactive' : True}},
        "set application mode to interactive"),
)

class AtRESTApplicationBase(Application):
    """
    Base class for AtREST applications.
    """

    name = Unicode(u'atrestapplicationbase')

    version = atrest_version

    description = """Start an AtREST Application.
    TODO: Add more description...
    """

    examples = """
    TODO: Add examples.
    """

    # any subclass that has configurables used by it should expose those class
    # names to this list in the subclass so the command line options of the
    # subclasses are available
    classes = List([])
    config_file = Unicode(u'',
                   help="Specify a config file to load").tag(config=True)

    aliases = Dict(base_aliases)

    flags = Dict(base_flags)

    def initialize(self, *args, **kwargs):
        """
        """
        super().initialize(*args, **kwargs)
        if self.config_file:
            self.load_config_file(self.config_file)

    def update_aliases(self, extra_aliases):
        """
        """
        self.aliases.update(extra_aliases)

    def update_flags(self, extra_flags):
        """
        """
        self.flags.update(extra_flags)


class AtRESTCLIApplication(AtRESTApplicationBase):
    """
    Base class for AtREST applications that can be run interactively via CLI.

    NOTE: This does not mean they have to be run via shell. They should be
          usable via `app subcmd args` where app is the parent application and
          subcmd is the CLI application.
    """
    name = 'atrest-cliapp'

    description = """Start an AtREST Application that can be run interactively.
    TODO: Add more description...
    """

    examples = """
    TODO: Add examples.
    """
    interactive = Bool(False,
                   help="Run via CLI (interactive)?").tag(config=True)

    def __init__(self, **kwargs):
        """
        """
        super(AtRESTCLIApplication, self).__init__(**kwargs)
        self.update_aliases(cli_extra_aliases)
        self.update_flags(cli_extra_flags)

    def initialize(self, *args, **kwargs):
        """
        """
        super().initialize(*args, **kwargs)

    def _start_interactive(self):
        """
        Method to be overridden for cli mode.
        """
        raise NotImplementedError

    def _start_normal(self):
        """
        Method to be overridden for non-cli mode.
        """
        raise NotImplementedError

    def start(self):
        """
        Override of Application start method. By default, just checks if we are
        to be run interactively or not and goes from there.
        """
        self.log.debug(
            'Starting AtRESTCLIApplication app in interactive mode: ',
            self.interactive
        )
        if self.interactive:
            self._start_interactive()
        else:
            self._start_normal()

# TODO: make a method for this purpose. only override if allowing standalone
#       run of application
# Any application that can be run by itself should define these things (sub
# the application class name for AtRESTApplicationBase and modify the function
# as needed for the app). If it's only needed for testing the app, be sure to
# remove it so it can't be run by itself later
#
# def main():
#     app = AtRESTApplicationBase()
#     # DO MORE THINGS AS NEEDED.
#     app.initialize()
#     app.start()
#
#
# if __name__ == "__main__":
#     main()
