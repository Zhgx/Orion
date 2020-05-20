import argparse


class NodeCommands():
    def __init__(self):
        pass

    def setup_commands(self,parser):
        """
        Add commands for the node management:create,modify,delete,show
        """
        subargs_node = self.node.add_subparsers(dest='subargs_node')
        self.node_create = subargs_node.add_parser('create', aliases='c', help='Create the node',
                                                   usage=usage.node_create)
        self.node_modify = subargs_node.add_parser('modify', aliases='m', help='Modify the node',
                                                   usage=usage.node_modify)
        self.node_delete = subargs_node.add_parser('delete', aliases='d', help='Delete the node',
                                                   usage=usage.node_delete)
        self.node_show = subargs_node.add_parser('show', aliases='s', help='Displays the node view', usage=usage.node_