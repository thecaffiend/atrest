#!/usr/bin/env python
import sys
from getpass import getpass
from pprint import pprint
from collections import OrderedDict

# ghetto addition of the parent dir path for finding AtREST. Only works from
# the tools directory for now...
sys.path.append('..')

from AtREST.atrest import (
    ConfluenceRESTClient as RESTClient,
    ClientMode,
)

# TODO: make this a traitlets application and make the interactive cli one mode
#       of operation (all operations should be runnable as sub commands of the
#       main application if possible)
# TODO: change prints to logs where/if it makes sense

class AtRESTCli():
    """
    Command line interface for the AtREST package.
    """
    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """
        self._client = None
        self.__build_ops()

    def __build_ops(self):
        """
        Build the dictionary of operations/commands.
        'OPTION NUMBER': {
            'label': 'MENU ITEM TEXT'
            'op': method_to_call,
        },
        """

        # TODO: make these options come from classes that do the actions
        self._OPS = {
            '1': {
                'label': 'Print command explainations/doc',
                'op': self.command_doc,
            },
            '2': {
                'label': 'List Spaces',
                'op': self.list_spaces,
            },
            '3': {
                'label': 'Deep Copy Content (excluding history but including all children, attachments, etc)',
                'op': self.deep_copy_content,
            },
            # 'N': ...,
            '1337': {
                'label': 'IPython Console (DEBUG)!',
                'op': self.debug_ipython,
            },
            '0': {
                'label': 'Run away screaming (exit)!',
                'op': self.leave_this_silly_place,
            },
        }

    def initialize(self):
        """
        Print a startup message and initialize the confluence client.
        """
        print('#'*50)
        print('Welcome to the AtREST CLI!')
        print('Enter required REST API parameters')
        print('#'*50)

        self._initialize_client()
        print('\n')

    def print_menu(self):
        """
        Print the main cli menu.
        """
        print('='*50)
        print('\tWhat would you like to do (enter number of command)')
        print('%s\n' % ('='*50))

        ordered_opts = OrderedDict(
            sorted(self._OPS.items(), key=lambda t: t[0])
        )

        for k, v in ordered_opts.items():
            print('\t%s. %s' % (k, v['label']))
        return input(' >>  ')

    def perform_operation(self, op_val):
        """
        Run the selected command.
        """
        selop = self._OPS.get(op_val, None)
        if selop is None:
            print('Invalid operation. Try again...\n')
            return
        selop['op']()

    def _initialize_client(self):
        """
        Initialize the RESTClient.
        """

        uname = input('username: ')
        url = input('REST API url base (e.g. https://blah.com/confluence): ')
        client_mode = input(
            'Run mode (1 for real, anything else for dry): '
        )
        pw = getpass('Password (will not be echoed): ')

        m = ClientMode.dry_run

        if client_mode == '1':
            m = ClientMode.real_run

        self._client = RESTClient(uname, pw, url, mode=m)

    def list_spaces(self):
        """
        List the space names from REST API available to this user.
        """
        space_names = self._client.list_space_names()
        print('\n%s' % ('-'*50))
        print('\tSpace Names:')
        pprint(space_names)
        print('%s\n' % ('-'*50))

    def deep_copy_content(self):
        """
        Get info about the source space/content and destination space/content
        and deep copy from source to destination.
        """
        # TODO: allow configuration of other items in the specs not handled
        #       here
        # TODO: method for printing these headers...
        print('\n%s' % ('-'*50))
        print('\tDeep copy of content')
        print('%s\t' % ('-'*50))

        src_spec, dst_spec = self._client.get_default_specs()
        src_spec = self._get_src_params(src_spec)
        dst_spec = self._get_dst_params(dst_spec)

        print('\n\tCopying content')

        result = self._client.copy_content(src_spec, dst_spec)
        print('\nCopy success: %s\n' % (result))


    def _get_src_params(self, src_spec):
        """
        """
        # TODO: allow space name instead of key
        # TODO: allow content id instead of all of this?
        # TODO: add defaults (leave blank for ...).
        print('\nSource content parameters')
        src_spec['space_key'] = input('\tSource space key: ')
        src_spec['title'] = input('\tSource content title: ')

        return src_spec

    def _get_dst_params(self, dst_spec):
        """
        Get destination specification.
        """
        # TODO: allow space name instead of key
        # TODO: allow content id instead of dest space/parent?
        # TODO: add defaults (leave blank for ...).
        print('\nDestination content parameters')
        dst_spec['space_key'] = input('\tDestination space key: ')
        dst_spec['title'] = input('\tDestination parent content title: ')
        dst_spec['content_copy']['title'] = input('\tDestination content title: ')

        return dst_spec

    def command_doc(self):
        """
        Print the doc for each command. Not implemented yet.
        """
        print('\n%s' % ('-'*50))
        print('\tCommand documentation')
        print('%s\t' % ('-'*50))
        print('\n\tSorry...this is not implemented yet.\n')


    def debug_ipython(self):
        """
        Open an IPython console for the current state.
        """
        # TODO: this should be available for debug only. remove or set a config
        #       option to specify DEBUG or not
        from IPython import embed as ipyembed
        ipyembed()

    def leave_this_silly_place(self):
        """
        Exit the CLI
        """
        sys.exit(0)


if __name__=='__main__':
    arcli = AtRESTCli()
    arcli.initialize()

    print('Ok, Let\'s do things with the Confluence API using Python!')

    while(True):
        selection = arcli.print_menu()
        arcli.perform_operation(selection)
