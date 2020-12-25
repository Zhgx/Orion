import execute as ex
import sundry as sd
import consts

class Usage():
    # vip部分使用手册
    vip = '''
    vip {create(c)/modify(m)/delete(d)/show(s)}'''

    vip_create = '''
    vip create(c) VIP -ip IP -port [PORT] -netmask [NETMASK]'''

    vip_delete = '''
    vip delete(d) VIP'''

    vip_modify = '''
    vip modify(m) VIP -ip IP -port PORT'''

    vip_show = '''
    vip show(s)'''


class VIPCommands():

    def __init__(self):
        self.logger = consts.glo_log()

    def setup_commands(self, parser):
        """
        Add commands for the VIP management:create,delete,modify,show
        """
        # VIP:Virtual IP
        vip_parser = parser.add_parser(
            'vip', help='vip operation',usage=Usage.vip)
        self.vip_parser = vip_parser

        vip_subp = vip_parser.add_subparsers(dest='vip')

        """
        Create VIP
        """
        p_create_vip = vip_subp.add_parser(
            'create',
            aliases='c',
            help='Create the VIP')

        # add arguments of vip create
        p_create_vip.add_argument(
            'vip',
            action='store',
            help='VIP Name')

        p_create_vip.add_argument(
            '-ip',
            action='store',
            dest='ip',
            help='IP'
        )

        p_create_vip.add_argument(
            '-n'
            '-netmask',
            '--netmask',
            dest='netmask',
            action='store',
            default=24,
            help='Netmask：0-32.It default is 24.')

        p_create_vip.add_argument(
            '-p',
            '-port',
            '--port',
            action='store',
            dest='port',
            default=3360,
            help='Port：3360-65535.It default is 3360.')




        self.p_create_vip = p_create_vip
        p_create_vip.set_defaults(func=self.create)

        """
        Show VIP
        """
        p_show_vip = vip_subp.add_parser(
            'show',
            aliases='s',
            help='Show the VIP',
            usage=Usage.vip_show)

        p_show_vip.set_defaults(func=self.show)

        """
        Delete VIP
        """
        # add arguments of vip delete
        P_delete_vip = vip_subp.add_parser(
            'delete', aliases='d', help='Delete the VIP',usage=Usage.vip_delete)

        P_delete_vip.add_argument(
            'vip',
            action='store',
            help='vip name')

        P_delete_vip.add_argument(
            '-y',
            dest='yes',
            action='store_true',
            help='Skip to confirm selection',
            default=False)

        P_delete_vip.set_defaults(func=self.delete)

        vip_parser.set_defaults(func=self.print_vip_help)


        """
        Modify VIP
        """
        p_modify_vip = vip_subp.add_parser(
            'modify',
            aliases='m',
            help='Modify the VIP',
            usage=Usage.vip_modify)


        p_modify_vip.add_argument(
            'vip',
            help='vip name')


        p_modify_vip.add_argument(
            '-ip',
            dest='ip',
            action='store',
            help='IP',
            metavar='IP',
            nargs='+')

        p_modify_vip.add_argument(
            '-p'
            '-port',
            '--port',
            dest='port',
            action='store',
            help='port',
            metavar='PORT')


        p_modify_vip.set_defaults(func=self.modify)


    # @sd.deco_record_exception
    def create(self, args):
        print('create')
        print(args)
        # vip = ex.VIP()
        # vip.create_vip(args.vip, args.disk)

    # @sd.deco_record_exception
    def show(self, args):
        print('show')
        print(args)
        # vip = ex.VIP()
        # if args.vip == 'all' or args.vip is None:
        #     vip.show_all_vip()
        # else:
        #     vip.show_spe_vip(args.vip)

    # @sd.deco_record_exception
    # @sd.deco_comfirm_del('vip')
    def delete(self, args):
        print('delete')
        print(args.vip)
        # vip = ex.VIP()
        # vip.delete_vip(args.vip)

    # @sd.deco_record_exception
    def modify(self, args):
        print('modify')
        print(args)
        # vip = ex.VIP()
        # if args.add:
        #     vip.add_disk(args.vip,args.add)
        # if args.remove:
        #     vip.remove_disk(args.vip,args.remove)


    def print_vip_help(self, *args):
        self.vip_parser.print_help()
