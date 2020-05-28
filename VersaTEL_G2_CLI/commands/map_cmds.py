import pickle
import iscsi_json

import execute as ex
import sundry as sd


class MapCommands():

    def __init__(self):
        pass

    def setup_commands(self, parser):
        """
        Add commands for the host group management:create,delete,show
        """
        map_parser = parser.add_parser(
            'map', aliases='m', help='map operation')
        map_subp = map_parser.add_subparsers(dest='map')
        self.map_parser = map_parser


        """
        Create map
        """
        p_create_map = map_subp.add_parser(
            'create',
            aliases='c',
            help='map create [map_name] -hg [hostgroup_name] -dg [diskgroup_name]')

        p_create_map.add_argument(
            'map', action='store', help='map_name')
        p_create_map.add_argument(
            '-hg', action='store', help='hostgroup_name')
        p_create_map.add_argument(
            '-dg', action='store', help='diskgroup_name')
        p_create_map.add_argument(
            '-gui', help='iscsi gui', nargs='?', default='cmd')

        p_create_map.set_defaults(func=self.create)

        """
        Delete map
        """
        p_delete_map = map_subp.add_parser(
            'delete', aliases='d', help='map delete [map_name]')

        p_delete_map.add_argument(
            'map',
            action='store',
            help='map_name',
            default=None)

        p_delete_map.set_defaults(func=self.delete)

        """
        Show map
        """
        p_show_map = map_subp.add_parser(
            'show', aliases='s', help='map show / map show [map_name]')

        p_show_map.add_argument(
            'map',
            action='store',
            help='map show [map_name]',
            nargs='?',
            default='all')

        p_show_map.set_defaults(func=self.show)

        map_parser.set_defaults(func=self.print_map_help)

    def create(self, args):
        obj_iscsi = ex.Iscsi()
        if args.gui == 'gui':
            data = pickle.dumps(obj_iscsi.create_map(args.map, args.hg, args.dg))
            sd.send_via_socket(data)
        else:
            obj_iscsi.create_map(args.map, args.hg, args.dg)

    def show(self, args):
        ex.Iscsi.show_map(args.map)

    def delete(self, args):
        obj_iscsi = ex.Iscsi()
        obj_iscsi.delete_map(args.map)

    def print_map_help(self, *args):
        self.map_parser.print_help()
