import argparse
import pickle
import sys
from functools import wraps

import log
import sundry as sd
import execute as ex
import linstordb
from consts import ExitCode



class usage():
    # node部分使用手册
    node = '''
    node(n) {create(c)/modify(m)/delete(d)/show(s)}'''

    node_create = '''
    node(n) create(c) NODE -ip IP -nt NODETYPE'''

    node_delete = '''
    node(n) delete(d) NODE'''

    # 待完善
    node_modify = '''
    node(n) modify(m) NODE ...'''

    node_show = '''
    node(n) show(s) [NODE]'''


class NodeCommands():
    def __init__(self):
        self.logger = log.Log()
        self.collector = log.Collector()

    def setup_commands(self, parser):
        """
        Add commands for the node management:create,modify,delete,show
        """
        node_parser = parser.add_parser(
            'node',
            aliases='n',
            help='Management operations for node',
            usage=usage.node)

        self.node_parser = node_parser
        node_subp = node_parser.add_subparsers(dest='subargs_node')

        """
        Create LINSTOR Node
        """
        p_create_node = node_subp.add_parser(
            'create',
            aliases='c',
            help='Create the node',
            usage=usage.node_create)
        self.p_create_node = p_create_node
        # add the parameters needed to create the node
        p_create_node.add_argument(
            'node',
            metavar='NODE',
            action='store',
            help='Name of the new node, must match the nodes hostname')
        p_create_node.add_argument(
            '-ip',
            dest='ip',
            action='store',
            help='IP address of the new node, if not specified it will be resolved by the name.',
            required=True)
        p_create_node.add_argument(
            '-nt',
            dest='nodetype',
            action='store',
            help='node type: {Controller,Auxiliary,Combined,Satellite}',
            required=True)
        # add a parameter to interact with the GUI
        p_create_node.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)

        p_create_node.set_defaults(func=self.create)

        """
        Modify LINSTOR Node
        """
        pass

        """
        Delete LINSTOR Node
        """
        p_delete_node = node_subp.add_parser(
            'delete',
            aliases='d',
            help='Delete the node',
            usage=usage.node_delete)
        self.p_delete_node = p_delete_node
        p_delete_node.add_argument(
            'node',
            metavar='NODE',
            action='store',
            help=' Name of the node to remove')
        p_delete_node.add_argument(
            '-y',
            dest='yes',
            action='store_true',
            help='Skip to confirm selection',
            default=False)
        p_delete_node.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)
        p_delete_node.set_defaults(func=self.delete)

        """
        Show LINSTOR Node
        """
        p_show_node = node_subp.add_parser(
            'show',
            aliases='s',
            help='Displays the node view',
            usage=usage.node_show)
        self.p_show_node = p_show_node
        p_show_node.add_argument(
            'node',
            metavar='NODE',
            help='Print information about the node in LINSTOR cluster',
            action='store',
            nargs='?',
            default=None)
        p_show_node.add_argument(
            '--no-color',
            dest='nocolor',
            help='Do not use colors in output.',
            action='store_true',
            default=False)
        p_show_node.set_defaults(func=self.show)

        node_parser.set_defaults(func=self.print_node_help)

    def create(self, args):
        transaction_id = sd.get_transaction_id()
        if args.gui:
            result = ex.Stor.create_node(args.node, args.ip, args.nodetype)
            result_pickled = pickle.dumps(result)
            sd.send_via_socket(result_pickled)
            return ExitCode.OK
        elif args.node and args.nodetype and args.ip:
            self.logger.InputLogger.debug(
                '',
                extra={
                    'username': self.collector.get_username(),
                    'type': 'cli_user_input',
                    'transaction_id': transaction_id,
                    'describe1': self.collector.get_path(),
                    'describe2': '',
                    'data': 'vtel stor n c %s -ip %s -nt %s' %(args.node,args.ip,args.nodetype)})
            ex.Stor.create_node(args.node, args.ip, args.nodetype)
            return ExitCode.OK
        else:
            self.p_create_node.print_help()
            return ExitCode.ARGPARSE_ERROR

    @sd.comfirm_del('node')
    def delete(self, args):
        ex.Stor.delete_node(args.node)

    def show(self, args):
        #sys.argv
        transaction_id = sd.get_transaction_id()
        username = self.collector.get_username()
        path = self.collector.get_path()
        tb = linstordb.OutputData()
        cmd = ' '.join(sys.argv)

        if args.nocolor:
            if args.node:
                self.logger.add_log(username, 'cli_user_input', transaction_id, path, '', cmd)
                tb.show_node_one(args.node,username,transaction_id)
                return ExitCode.OK
            else:
                tb.node_all()
                return ExitCode.OK
        else:
            if args.node:
                self.logger.add_log(username,'cli_user_input',transaction_id,path,'',cmd)
                tb.show_node_one_color(args.node,username,transaction_id)
                return ExitCode.OK
            else:
                self.logger.add_log(username, 'cli_user_input', transaction_id, path, '', cmd)
                result = tb.node_all_color(username,transaction_id)
                self.logger.add_log(username,'result_to_show', transaction_id, '', '', result)
                return ExitCode.OK

    def print_node_help(self, *args):
        self.node_parser.print_help()


# def log_node_show(str):
#     logger = log.Log()
#     collector = log.Collector()
#     transaction_id = sd.get_transaction_id()
#     def decorate(func):
#         @wraps(func)
#         def wrapper(*args):
#
#             logger.InputLogger.debug(
#                 '',
#                 extra={
#                     'username': collector.get_username(),
#                     'type': 'cli_user_input',
#                     'transaction_id': transaction_id,
#                     'describe1': collector.get_path(),
#                     'describe2': '',
#                     'data': 'vtel stor n s %s' % args.node})
#             func(*args)
#             return wrapper
#         return decorate
