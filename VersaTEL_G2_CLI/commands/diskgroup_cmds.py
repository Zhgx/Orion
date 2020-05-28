import argparse
import pickle
import iscsi_json

import execute as ex
import sundry as sd


class DiskGroupCommands():

    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        Add commands for the diskgroup management:create,delete,show
        """
        # dg:diskgroup
        dg_parser = parser.add_parser(
            'diskgroup', aliases=['dg'], help='diskgroup operation')
        self.dg_parser = dg_parser

        dg_subp = dg_parser.add_subparsers(dest='diskgroup')

        """
        Create DiskGroup
        """
        p_create_dg = dg_subp.add_parser(
            'create',
            aliases='c',
            help='diskgroup create [diskgroup_name] [disk_name1] [disk_name2] ...')

        # add arguments of diskgroup create
        p_create_dg.add_argument(
            'diskgroup',
            action='store',
            help='diskgroup_name')
        p_create_dg.add_argument(
            'disk',
            action='store',
            help='disk_name',
            nargs='+')
        p_create_dg.add_argument(
            '-gui', help='iscsi gui', nargs='?', default='cmd')

        self.p_create_dg = p_create_dg
        p_create_dg.set_defaults(func=self.create)

        """
        Show DiskGroup
        """
        p_show_dg = dg_subp.add_parser(
            'show',
            aliases='s',
            help='diskgroup show / diskgroup show [diskgroup_name]')

        # add arguments of diskgroup show
        p_show_dg.add_argument(
            'diskgroup',
            action='store',
            help='diskgroup show [diskgroup_name]',
            nargs='?',
            default='all')

        p_show_dg.set_defaults(func=self.show)

        """
        Delete DiskGroup
        """
        # add arguments of diskgroup delete
        P_delete_dg = dg_subp.add_parser(
            'delete', aliases='d', help='diskgroup delete [diskgroup_name]')

        P_delete_dg.add_argument(
            'diskgroup',
            action='store',
            help='diskgroup_name',
            default=None)

        P_delete_dg.set_defaults(func=self.delete)

        dg_parser.set_defaults(func=self.print_dg_help)

    def create(self, args):
        if args.gui == 'gui':
            data = pickle.dumps(ex.Iscsi.create_diskgroup(args.diskgroup, args.disk))
            sd.send_via_socket(data)
        else:
            ex.Iscsi.create_diskgroup(args.diskgroup, args.disk)

    def show(self, args):
        ex.Iscsi.show_diskgroup(args.diskgroup)

    def delete(self, args):
        ex.Iscsi.delete_diskgroup(args.diskgroup)

    def print_dg_help(self, *args):
        self.dg_parser.print_help()
