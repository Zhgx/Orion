import argparse
import pickle

import sundry as sd
import execute_sys_command as esc
import linstordb


class usage():
    storagepool = '''
    storagepool(sp) {create(c)/modify(m)/delete(d)/show(s)}'''

    storagepool_create = '''
    storagepool(sp) create(c) STORAGEPOOL -n NODE -lvm LVM/-tlv THINLV'''

    storagepool_delete = '''
    storagepool(sp) delete(d) STORAGEPOOL -n NODE'''

    # 待完善
    storagepool_modify = '''
    storagepool(sp) modify(m) STORAGEPOOL ...'''

    storagepool_show = '''
    storagepool(sp) show(s) [STORAGEPOOL]'''


class NodeCommands():
    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        sp(storage pool)
        Add commands for the storage pool management:create,modify,delete,show
        """
        sp_parser = parser.add_parser(
            'storagepool',
            aliases=['sp'],
            help='Management operations for storagepool',
            usage=usage.storagepool)

        sp_subp = sp_parser.add_subparsers(
            dest='subargs_sp')

        """
        Create LINSTOR Storage Pool
        """
        p_create_sp = sp_subp.add_parser(
            'create',
            aliases='c',
            help='Create the storagpool',
            usage=usage.storagepool_create)

        p_create_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            action='store',
            help='Name of the new storage pool')
        p_create_sp.add_argument(
            '-n',
            dest='node',
            action='store',
            help='Name of the node for the new storage pool',
            required=True)
        p_create_sp.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)
        group_type = p_create_sp.add_mutually_exclusive_group()
        group_type.add_argument(
            '-lvm',
            dest='lvm',
            action='store',
            help='The Lvm volume group to use.')
        group_type.add_argument(
            '-tlv',
            dest='tlv',
            action='store',
            help='The LvmThin volume group to use. The full name of the thin pool, namely VG/LV')

        p_create_sp.set_defaults(func=self.create)


        """
        Modify LISNTOR Storage Pool
        """
        pass

        """
        Delete LISNTOR Storage Pool
        """
        p_delete_sp = sp_subp.add_parser(
            'delete',
            aliases='d',
            help='Delete the storagpool',
            usage=usage.storagepool_delete)

        p_delete_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            help='Name of the storage pool to delete',
            action='store')
        p_delete_sp.add_argument(
            '-n',
            dest='node',
            action='store',
            help='Name of the Node where the storage pool exists',
            required=True)
        p_delete_sp.add_argument(
            '-y',
            dest='yes',
            action='store_true',
            help='Skip to confirm selection',
            default=False)
        p_delete_sp.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)




        """
        Show LISNTOR Storage Pool
        """
        p_show_sp = sp_subp.add_parser(
            'show',
            aliases='s',
            help='Displays the storagpool view',
            usage=usage.storagepool_show)

        p_show_sp.add_argument(
            'storagepool',
            metavar='STORAGEPOOL',
            help='Print information about the storage pool in LINSTOR cluster',
            action='store',
            nargs='?')
        p_show_sp.add_argument(
            '--no-color',
            dest='nocolor',
            help='Do not use colors in output.',
            action='store_true',
            default=False)

        p_show_sp.set_defaults(func=self.show)



    def create(self, args):
        if args.gui:
            result = esc.stor.create_node(args.node, args.ip, args.nodetype)
            result_pickled = pickle.dumps(result)
            sd.send_via_socket(result_pickled)
        elif args.node and args.nodetype and args.ip:
            esc.stor.create_node(args.node, args.ip, args.nodetype)
        else:
            self.p_create_node.print_help()

    @sd.comfirm_del('node')
    def delete(self, args):
        esc.stor.delete_node(args.node)

    def show(self, args):
        tb = linstordb.OutputData()
        if args.nocolor:
            tb.show_node_one(args.node) if args.node else tb.node_all()
        else:
            tb.show_node_one_color(
                args.node) if args.node else tb.node_all_color()
