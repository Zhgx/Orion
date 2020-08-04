import pickle
import execute as ex
import sundry as sd
import consts


class HostGroupCommands():

    def __init__(self):
        self.logger = consts.get_glo_log()
        self.obj_iscsi = ex.Iscsi()

    def setup_commands(self, parser):
        """
        Add commands for the host group management:create,delete,show
        """
        # hg:hostgroup
        hg_parser = parser.add_parser(
            'hostgroup', aliases=['hg'], help='hostgroup operation')
        self.hg_parser = hg_parser
        hg_subp = hg_parser.add_subparsers(dest='hostgroup')

        """
        Create HostGroup
        """
        p_create_hg = hg_subp.add_parser(
            'create',
            aliases='c',
            help='hostgroup create [hostgroup_name] [host_name1] [host_name2] ...')

        p_create_hg.add_argument(
            'hostgroup',
            action='store',
            help='hostgroup_name')
        p_create_hg.add_argument(
            'host',
            action='store',
            help='host_name',
            nargs='+')
        p_create_hg.add_argument(
            '-gui', help='iscsi gui', nargs='?', default='cmd')

        # level4,arguments of hostgroup show
        p_create_hg.add_argument(
            'show',
            action='store',
            help='hostgroup show [hostgroup_name]',
            nargs='?',
            default='all')

        p_create_hg.set_defaults(func=self.create)

        """
        Show HostGroup
        """
        p_show_hg = hg_subp.add_parser(
            'show',
            aliases='s',
            help='hostgroup show / hostgroup show [hostgroup_name]')

        p_show_hg.add_argument(
            'hostgroup',
            action='store',
            help='hostgroup show [hostgroup_name]',
            nargs='?',
            default='all')

        p_show_hg.set_defaults(func=self.show)

        """
        Delete HostGroup
        """
        p_delete_hg = hg_subp.add_parser(
            'delete', aliases='d', help='hostgroup delete [hostgroup_name]')

        p_delete_hg.add_argument(
            'hostgroup',
            action='store',
            help='hostgroup_name',
            default=None)

        p_delete_hg.set_defaults(func=self.delete)

        hg_parser.set_defaults(func=self.print_hg_help)

    @sd.record_exception
    def create(self, args):
        if args.gui == 'gui':
            data = pickle.dumps(
                self.obj_iscsi.create_hostgroup(
                    args.hostgroup, args.host))
            sd.send_via_socket(data)
        else:
            self.obj_iscsi.create_hostgroup(args.hostgroup, args.host)

    @sd.record_exception
    def show(self, args):
        if args.hostgroup == 'all' or args.hostgroup is None:
            self.obj_iscsi.show_all_hostgroup()
        else:
            self.obj_iscsi.show_spe_hostgroup(args.hostgroup)

    @sd.record_exception
    def delete(self, args):
        self.obj_iscsi.delete_hostgroup(args.hostgroup)

    def print_hg_help(self, *args):
        self.hg_parser.print_help()
