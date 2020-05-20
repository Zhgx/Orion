import argparse
import sys
import os
from VersaTEL_G2_CLI.commands import (
    NodeCommands
)

from VersaTEL_G2_CLI.consts import (
    VERSION
)


class VtelCLI(object):
    """
    Vtel command line client
    """
    def __init__(self):
        pass
        self._node_commands = NodeCommands()
        self._parser = self.setup_parser()


    def setup_parser(self):
        parser = argparse.ArgumentParser(prog="vtel")
        """
        Set parser vtel sub-parser
        """
        #parser.add_argument('--version','-v',action='version',version='%(prog)s ' + VERSION + '; ')

        subp = parser.add_subparsers(title='subcommands',
                                     description='valid subcommands',
                                     help='Use the list command to print a '
                                          'nicer looking overview of all valid commands')

        parser_stor = subp.add_parser('stor', help='Management operations for LINSTOR', add_help=False,usage=usage.stor)
        parser_iscsi = subp.add_parser('iscsi', help='Management operations for iSCSI', add_help=False)

        # add parameters to interact with the GUI
        parser_stor.add_argument('-gui', dest='gui', action='store_true', help=argparse.SUPPRESS, default=False)
        parser_stor.set_defaults(func=self.func_stor)

        subp.choices.keys()

        subp_stor = parser_stor.add_subparsers(dest = 'subargs_stor')
        subp_iscsi = parser_iscsi.add_subparsers(dest = 'subargs_iscsi')

        # add all node commands
        self._node_commands.setup_commands(subp_stor)

        return parser

    def func_stor(self,args,parser):
        if args.gui:
            print('gui')
        else:
            parser.stor.print_help()

    def parse(self,pargs):
        return self._parser.parse_args(pargs)

    def run(self):
        pass


def main():
    try:
        VtelCLI().run()
    except KeyboardInterrupt:
        sys.stderr.write("\nlinstor: Client exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()