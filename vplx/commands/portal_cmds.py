import execute as ex
import consts

class Usage():
    # portal部分使用手册
    portal = '''
    portal {create(c)/modify(m)/delete(d)/show(s)}'''

    portal_create = '''
    portal create(c) PORTAL -ip IP -port [PORT] -netmask [NETMASK]'''

    portal_delete = '''
    portal delete(d) PORTAL'''

    portal_modify = '''
    portal modify(m) PORTAL -ip IP -port PORT'''

    portal_show = '''
    portal show(s)'''


class PortalCommands():

    def __init__(self):
        self.logger = consts.glo_log()

    def setup_commands(self, parser):
        """
        Add commands for the PORTAL management:create,delete,modify,show
        """
        portal_parser = parser.add_parser(
            'portal', aliases=['pt'], help='portal operation',usage=Usage.portal)
        self.portal_parser = portal_parser

        portal_subp = portal_parser.add_subparsers(dest='portal')

        """
        Create PORTAL
        """
        p_create_portal = portal_subp.add_parser(
            'create',
            aliases='c',
            help='Create the PORTAL')

        # add arguments of portal create
        p_create_portal.add_argument(
            'portal',
            action='store',
            help='PORTAL Name')

        p_create_portal.add_argument(
            '-ip',
            action='store',
            required=True,
            dest='ip',
            help='IP'
        )

        p_create_portal.add_argument(
            '-n',
            '-netmaks',
            '--netmask',
            type=int,
            dest='netmask',
            action='store',
            default=24,
            help='Netmask：0-32.It default is 24.')

        p_create_portal.add_argument(
            '-p',
            '-port',
            '--port',
            type=int,
            action='store',
            dest='port',
            default=3360,
            help='Port：3360-65535.It default is 3360.')




        self.p_create_portal = p_create_portal
        p_create_portal.set_defaults(func=self.create)

        """
        Show PORTAL
        """
        p_show_portal = portal_subp.add_parser(
            'show',
            aliases='s',
            help='Show the PORTAL',
            usage=Usage.portal_show)

        p_show_portal.set_defaults(func=self.show)

        """
        Delete PORTAL
        """
        # add arguments of portal delete
        P_delete_portal = portal_subp.add_parser(
            'delete', aliases='d', help='Delete the PORTAL',usage=Usage.portal_delete)

        P_delete_portal.add_argument(
            'portal',
            action='store',
            help='portal name')

        P_delete_portal.set_defaults(func=self.delete)

        portal_parser.set_defaults(func=self.print_portal_help)


        """
        Modify PORTAL
        """
        p_modify_portal = portal_subp.add_parser(
            'modify',
            aliases='m',
            help='Modify the PORTAL',
            usage=Usage.portal_modify)


        p_modify_portal.add_argument(
            'portal',
            help='portal name')


        p_modify_portal.add_argument(
            '-ip',
            dest='ip',
            required=True,
            action='store',
            help='IP',
            metavar='IP',
            nargs='+')

        p_modify_portal.add_argument(
            '-p'
            '-port',
            '--port',
            required=True,
            type=int,
            dest='port',
            action='store',
            help='port',
            metavar='PORT')


        p_modify_portal.set_defaults(func=self.modify)


    # @sd.deco_record_exception
    def create(self, args):
        crm = ex.CRMData()
        vip = crm.get_vip()
        portblock = crm.get_portblock()
        target = crm.get_target()
        crm.check_env_sync(vip,portblock,target)

        portal = ex.Portal()
        portal.create(args.portal,args.ip,args.port,args.netmask)


    # @sd.deco_record_exception
    def show(self, args):
        print('show')
        print(args)
        # portal = ex.PORTAL()
        # if args.portal == 'all' or args.portal is None:
        #     portal.show_all_portal()
        # else:
        #     portal.show_spe_portal(args.portal)

    # @sd.deco_record_exception
    def delete(self, args):
        portal = ex.Portal()
        portal.delete(args.portal)


    # @sd.deco_record_exception
    def modify(self, args):
        print('modify')
        print(args)
        # portal = ex.PORTAL()
        # if args.add:
        #     portal.add_disk(args.portal,args.add)
        # if args.remove:
        #     portal.remove_disk(args.portal,args.remove)


    def print_portal_help(self, *args):
        self.portal_parser.print_help()
