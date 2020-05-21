import argparse
import sys
import os
from commands import (
    NodeCommands,
    ResourceCommands
)




class VtelCLI(object):
    """
    Vtel command line client
    """
    def __init__(self):
        self._node_commands = NodeCommands()
        self._resource_commands = ResourceCommands()
        self._parser = self.setup_parser()


    def setup_parser(self):
        parser = argparse.ArgumentParser(prog="vtel")
        """
        Set parser vtel sub-parser
        """
        #parser.add_argument('--version','-v',action='version',version='%(prog)s ' + VERSION + '; ')

        subp = parser.add_subparsers(title='subcommands',
                                     dest = 'subargs_vtel')

        parser_stor = subp.add_parser('stor', help='Management operations for LINSTOR', add_help=False,formatter_class=argparse.RawTextHelpFormatter,)
        self.parser_stor = parser_stor
        parser_iscsi = subp.add_parser('iscsi', help='Management operations for iSCSI', add_help=False)

        # add parameters to interact with the GUI
        parser_stor.add_argument('-gui', dest='gui', action='store_true', help=argparse.SUPPRESS, default=False)
        parser_stor.set_defaults(func=self.func_stor)

        subp.choices.keys()

        subp_stor = parser_stor.add_subparsers(dest = 'subargs_stor')
        # subp_iscsi = parser_iscsi.add_subparsers(dest = 'subargs_iscsi')

        # add all subcommands and argument
        self._node_commands.setup_commands(subp_stor)
        self._resource_commands.setup_commands(subp_stor)

        parser.set_defaults(func=parser.print_help)

        return parser

    def func_stor(self,args):
        if args.gui:
            print('gui')
        else:
            self.parser_stor.print_help()

    # def parse(self,pargs):
    #     return self._parser.parse_args(pargs)

    def run(self):
        pass

    def parse(self):
        args = self._parser.parse_args()
        if args.subargs_vtel:
            args.func(args)
        else:
            self._parser.print_help()



def main():
    try:
        cmd = VtelCLI()
        cmd.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nlinstor: Client exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()