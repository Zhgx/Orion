import pickle
import execute as ex

import iscsi_json
import sundry


class HostCommands():
    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        Add commands for the hosw management:create,delete,show
        """
        host_parser = parser.add_parser(
            'host', aliases='h', help='host operation')
        self.host_parser = host_parser
        host_subp = host_parser.add_subparsers(dest='host')

        """
        Create iSCSI Host
        """
        p_create_host = host_subp.add_parser(
            'create', aliases='c', help='host create [host_name] [host_iqn]')

        # add arguments of host create
        p_create_host.add_argument(
            'host', action='store', help='host_name')
        p_create_host.add_argument('iqn', action='store', help='host_iqn')
        p_create_host.add_argument(
            '-gui', help='iscsi gui', nargs='?', default='cmd')

        p_create_host.set_defaults(func=self.create)

        """
        Delete iSCSI Host
        """
        p_delete_host = host_subp.add_parser(
            'delete', aliases='d', help='host delete [host_name]')

        # add arguments of host delete
        p_delete_host.add_argument(
            'host',
            action='store',
            help='host_name',
            default=None)

        p_delete_host.set_defaults(func=self.delete)

        """
        Show iSCSI Host
        """
        p_show_host = host_subp.add_parser(
            'show', aliases='s', help='host show / host show [host_name]')

        # add arguments of host show
        p_show_host.add_argument(
            'show',
            action='store',
            help='host show [host_name]',
            nargs='?',
            default='all')

        p_show_host.set_defaults(func=self.show)

        host_parser.set_defaults(func=self.print_host_help)

    def create(self, args):
        if args.gui == 'gui':
            data = pickle.dumps(ex.Iscsi.create_host(args.host, args.iqn))
            sundry.send_via_socket(data)
        else:
            ex.Iscsi.create_host(args.host, args.iqn)

    # host查询
    def show(self, args):
        js = iscsi_json.JSON_OPERATION()
        if args.show == 'all' or args.show is None:
            hosts = js.get_data("Host")
            print(" " + "{:<15}".format("Hostname") + "Iqn")
            print(" " + "{:<15}".format("---------------") + "---------------")
            for k in hosts:
                print(" " + "{:<15}".format(k) + hosts[k])
        else:
            if js.check_key('Host', args.show):
                print(args.show, ":", js.get_data('Host').get(args.show))
            else:
                print("Fail! Can't find " + args.show)
                return False
        return True

    def delete(self, args):
        js = iscsi_json.JSON_OPERATION()
        print("Delete the host <", args.host, "> ...")
        if js.check_key('Host', args.host):
            if js.check_value('HostGroup', args.host):
                print(
                    "Fail! The host in ... hostgroup, Please delete the hostgroup first.")
                return False
            else:
                js.delete_data('Host', args.host)
                print("Delete success!")
                return True
        else:
            print("Fail! Can't find " + args.host)
            return False

    def print_host_help(self, *args):
        self.host_parser.print_help()
