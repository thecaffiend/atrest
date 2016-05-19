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

# from PythonConfluenceAPI import ConfluenceAPI

# cnfapi = None
# expstr = ''
# expands = {}
# expanded = []

# TODO: class-ify this...

class AtRESTCli():
    """
    """
    def __init__(self, *args, **kwargs):
        """
        """
        self._client = None
        self.__build_ops()

    def __build_ops(self):
        """

        'OPTION NUMBER': {
            'label': 'MENU ITEM TEXT'
            'op': method_to_call,
            'req_api_init': True if API required first, False otherwise,
        },
        """
        self._OPS = {
            # TODO: this should just happent at startup. also shouldn't print
            #       command after it's been done (so shouldn't be a command).
            #       then the req_api_init stuff becomes unnecessary
            '1': {
                'label': 'Initialize the Confluence API Client (must be done first!)',
                'op': self.initialize_api,
                'req_api_init': False,
            },
            '2': {
                'label': 'Print command explainations/doc',
                'op': self.command_doc,
                'req_api_init': False,
            },
            '3': {
                'label': 'List Spaces',
                'op': self.list_spaces,
                'req_api_init': True,
            },
            # '4': ...,
            '0': {
                'label': 'Run away screaming (exit)!',
                'op': self.leave_this_silly_place,
                'req_api_init': False,
            },
        }

    def print_menu(self):
        """
        """
        print('Welcome to the AtREST tester')
        print('What would you like to do (enter number):')
        ordered_opts = OrderedDict(
            sorted(self._OPS.items(), key=lambda t: t[0])
        )

        for k, v in ordered_opts.items():
            if v['req_api_init'] == True and self._client == None:
                # don't give access to the things that require an initialized api
                # until it's been initialized.
                continue
            print('\t%s. %s' % (k, v['label']))
        return input(' >>  ')

    def perform_operation(self, op_val):
        """
        """
        selop = self._OPS.get(op_val, None)
        if selop is None:
            print('Invalid operation. Try again...')
            return
        selop['op']()

    def initialize_client(self):
        """
        """
        uname = input('Enter your username: ')
        url = input('Enter the REST API url base (e.g. https://blah.com/confluence): ')
        client_mode = input(
            'Enter run mode (1 for real, anything else for dry): '
        )
        pw = getpass('Enter password (will not be echoed): ')

        m = ClientMode.dry_run

        if client_mode == '1':
            m = ClientMode.real_run

        self._client = RESTClient(uname, pw, url, mode=m)

    def list_spaces(self):
        """
        """
        space_names = self._client.list_space_names()
        print('\n\t------------------------------')
        print('\tSpace Names:')
        pprint(space_names)
        print('\t------------------------------\n')

    def leave_this_silly_place(self):
        """
        """
        sys.exit(0)


if __name__=='__main__':
    arcli = AtRESTCli()

    print('Let\'s do things with the Confluence API using Python!')

    while(True):
        selection = arcli.print_menu()
        arcli.perform_operation(selection)
