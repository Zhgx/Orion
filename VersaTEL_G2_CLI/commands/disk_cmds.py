import argparse
import pickle

import sundry as sd
import iscsi_json
import execute as ex


class DiskCommands():
    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        Add commands for the disk management:create,delete,show
        """
        disk_parser = parser.add_parser(
            'disk', aliases='d', help='disk operation')
        disk_parser.set_defaults(func=self.print_disk_help)

        disk_subp = disk_parser.add_subparsers(dest='subargs_disk')

        """
        Show disk
        """

        p_show_disk = disk_subp.add_parser(
            'show', aliases='s', help='disk show')

        p_show_disk.add_argument(
            'show',
            action='store',
            help='disk show [disk_name]',
            nargs='?',
            default='all')

        self.disk_parser = disk_parser
        self.p_show_disk = p_show_disk
        p_show_disk.set_defaults(func=self.show)

    def show(self, args):
        js = iscsi_json.JSON_OPERATION()
        cd = ex.CRM()
        data = cd.get_data_linstor()
        linstorlv = ex.LINSTOR.refine_linstor(data)
        disks = {}
        for d in linstorlv:
            disks.update({d[1]: d[5]})
        js.up_data('Disk', disks)
        if args.show == 'all' or args.show is None:
            print(" " + "{:<15}".format("Diskname") + "Path")
            print(" " + "{:<15}".format("---------------") + "---------------")
            for k in disks:
                print(" " + "{:<15}".format(k) + disks[k])
        else:
            if js.check_key('Disk', args.show):
                print(args.show, ":", js.get_data('Disk').get(args.show))
            else:
                print("Fail! Can't find " + args.show)

    def print_disk_help(self, *args):
        self.disk_parser.print_help()
