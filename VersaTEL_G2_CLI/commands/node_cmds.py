import argparse
import pickle

import sundry as sd
import execute_sys_command as esc
import linstordb as linstordb

class usage():
    node = "111"
    node_create = 'node create'


class NodeCommands():
    def __init__(self):
        pass

    def setup_commands(self,parser):
        """
        Add commands for the node management:create,modify,delete,show
        """

        node_parser = parser.add_parser(
            'node',
            aliases='n',
            help='Management operations for node',
            usage=usage.node)

        node_subp = node_parser.add_subparsers(dest='subargs_node')


        """
        Create LINSTOR Node
        """
        p_create_node = node_subp.add_parser('create', aliases='c', help='Create the node',
                                                   usage=usage.node)
        self.p_create_node = p_create_node
        #add the parameters needed to create the node
        p_create_node.add_argument('node', metavar='NODE', action='store',
                                      help='Name of the new node, must match the nodes hostname')
        p_create_node.add_argument('-ip', dest='ip', action='store',
                                      help='IP address of the new node, if not specified it will be resolved by the name.',
                                      required=True)
        p_create_node.add_argument('-nt', dest='nodetype', action='store',
                                      help='node type: {Controller,Auxiliary,Combined,Satellite}', required=True)
        # add a parameter to interact with the GUI
        p_create_node.add_argument('-gui', dest='gui', action='store_true', help=argparse.SUPPRESS, default=False)

        p_create_node.set_defaults(func=self.create)

        """
        Modify LINSTOR Node
        """
        pass


        """
        Delete LINSTOR Node
        """
        p_delete_node = node_subp.add_parser('delete', aliases='d', help='Delete the node',
                                                   usage=usage.node)
        self.p_delete_node = p_delete_node
        p_delete_node.add_argument('node', metavar='NODE', action='store', help=' Name of the node to remove')
        p_delete_node.add_argument('-y', dest='yes', action='store_true', help='Skip to confirm selection',
                                      default=False)
        p_delete_node.add_argument('-gui', dest='gui', action='store_true', help=argparse.SUPPRESS, default=False)
        p_delete_node.set_defaults(func=self.delete)


        """
        Show LINSTOR Node
        """
        p_show_node = node_subp.add_parser('show', aliases='s', help='Displays the node view', usage=usage.node)
        self.p_show_node = p_show_node
        p_show_node.add_argument('node', metavar='NODE', help='Print information about the node in LINSTOR cluster',
                                    action='store', nargs='?', default=None)
        p_show_node.add_argument('--no-color', dest='nocolor', help='Do not use colors in output.',
                                    action='store_true', default=False)
        p_show_node.set_defaults(func=self.show)

    def create(self,args):
        if args.gui:
            result = esc.stor.create_node(args.node, args.ip, args.nodetype)
            result_pickled = pickle.dumps(result)
            sd.send_via_socket(result_pickled)
        elif args.node and args.nodetype and args.ip:
            esc.stor.create_node(args.node, args.ip, args.nodetype)
        else:
            self.p_create_node.print_help()


    @sd.comfirm_del
    def delete(self,args):
        esc.stor.delete_node(args.node)


    def show(self,args):
        tb = linstordb.OutputData()
        if args.nocolor:
            tb.show_node_one(args.node) if args.node else tb.node_all()
        else:
            tb.show_node_one_color(args.node) if args.node else tb.node_all_color()
