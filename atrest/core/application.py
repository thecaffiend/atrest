import logging
import enum

from traitlets.config.application import Application

from traitlets import (
    Unicode, Dict, Bool, Enum as TraitletEnum,
)

from atrest import __version__ as atrest_version
from atrest.utils.appfuncts import (
    find_subcommands,
)

class AppRunMode(enum.Enum):
    """
    Enum for the mode to operate in. dry_run only logs what would happen.
    real_run does it for realz...
    """
    dry_run = 0
    real_run = 1

# Aliases and flags for all AtRESTApplicationBase decendants
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

cli_aliases = {
    'interactive' : 'AtRESTCLIApplication.interactive',
}
cli_aliases.update(base_aliases)

# TODO: is there a way to specify both a single char and full flag name
#       in a single element here (e.g. both i and interactive)? any
#       problems specifying 2 flags for the same thing if not?
cli_flags = dict(
    interactive = ({'AtRESTCLIApplication' : {'interactive' : True}},
        "set application mode to interactive"),
    i = ({'AtRESTCLIApplication' : {'interactive' : True}},
        "set application mode to interactive"),
)
cli_flags.update(base_flags)

class AtRESTApplicationBase(Application):
    """
    Base class for AtREST applications.
    """

    name = Unicode(u'atrest-base')

    version = atrest_version

    description = """Base class for AtREST Applications. Should not be used
    as is, but should be subclassed.
    """

    examples = """
    Base class has no examples.
    """

    config_file = Unicode(u'',
                   help="Specify a config file to load").tag(config=True)

    aliases = Dict(base_aliases)

    flags = Dict(base_flags)

    # TODO: Once tested, the mode should default to real_run.
    mode = TraitletEnum(AppRunMode,
        default_value=AppRunMode.dry_run,
        help='the run mode of the client'
    ).tag(config=True)

    extra_subcommands = Dict({},
        help='user added extra subcommands for the application').tag(config=True)

    extra_cmd_dirs = Unicode(u'',
        help='directory to scan for subcommand files').tag(config=True)

    # TODO: may be best to set mode explicitly instead of in __init__. Then the
    #       __init__would really be unnecessary. So if this works, remove it
    # def __init__(self, *args, **kwargs):
    #     """
    #     Base initializer. Set the mode if provided.
    #     """
    #     super().__init__(*args, **kwargs)
    #     m = kwargs.pop('mode', None)
    #     if m:
    #         self.mode = m

    # TODO: make @classmethod?
    def update_aliases(self, extra_aliases):
        """
        Update the aliases dict with the provided extra_aliases
        """
        self.aliases.update(extra_aliases)

    # TODO: make @classmethod?
    def update_flags(self, extra_flags):
        """
        Update the flags dict with the provided extra_flags
        """
        self.flags.update(extra_flags)
            
    @classmethod
    def _get_subcommands(cls):
        """
        Get subcommands for this application. These may be in a directory
        specified in the config, a dict in the config, and in the subcommands
        dict of the class itself.
        """
        # TODO: in progress. finish later. should load all subcommands found
        #       in the usual python script loactions, on the user's path, and
        #       specified in subclasses
        subcommands = cls.subcommands

        # LEFTOFF
        # TODO: get configurable SC's working..

        # subcmd_list = []
        #
        # # scan for subcommands (named app_name-cmd_name)
        # subcmd_list += find_subcommands(cls.name, extra_dirs=cls.extra_cmd_dirs)
        #
        # # This subcmd_list is a list of commands, but we need to load the help
        # # from them and such
        #
        # # load the ones from the config. they should be formatted like if they
        # # were defined in this class.
        #
        # # add all to the existing sc's
        # # return the updated dict of SC's
        return subcommands


class AtRESTCLIApplication(AtRESTApplicationBase):
    """
    Base class for AtREST applications that can be run interactively via CLI.

    NOTE: This does not mean they have to be run via shell. They should be
          usable via `app subcmd args` where app is the parent application and
          subcmd is the CLI application.
    """
    name = 'atrest-cliapp'

    description = """Start an AtREST Application that can be run interactively.
    This should not be used as is and should instead be subclassed
    """

    examples = """
    Base class has no examples.
    """

    aliases = Dict(cli_aliases)

    flags = Dict(cli_flags)

    interactive = Bool(False,
                   help="Run via CLI (interactive)?").tag(config=True)

# TODO: remove if not needed
    # TODO: find a way to update flags and aliases without an __init__ to
    #       remove need to call super().__init__(). Once done, remove this.
    #       see NewToken in juyterhub repo.
#     def __init__(self, *args, **kwargs):
#         """
#         Initialize the instance. Update the aliases/flags
#         """
# #        super().__init__(**kwargs)
#         self.update_aliases(cli_extra_aliases)
#         self.update_flags(cli_extra_flags)

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

# TODO: remove if not needed
    # def start(self):
    #     """
    #     Override of Application start method. By default, just checks if we are
    #     to be run interactively or not and goes from there.
    #     """
    #
    #     self.log.debug(
    #         'Starting AtRESTCLIApplication app in interactive mode: %s',
    #         self.interactive
    #     )
    #
    #     if self.subapp:
    #         self.subapp.start()
    #         return
    #
    #     if self.interactive:
    #         self._start_interactive()
    #     else:
    #         self._start_normal()

# TODO: make this doc accurate after getting the architecture down.

# NOTE: Applications that will be runnable by themselves (not as sub apps to
#       another app) need to hav a method to run them. An example of this
#       exists in /tools (atrest-confluence). The top level application may
#       just make it's own main method and run from there (see jupyterhub as
#       an example). for that, the code might look like:

# def main():
#     app = ApplicationName()
#     # DO MORE THINGS AS NEEDED.
#     app.initialize()
#     app.start()
#
#
# if __name__ == "__main__":
#     main()
