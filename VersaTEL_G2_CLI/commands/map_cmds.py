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

        # show_parser = parser.add_parser('show', aliases='s')
        # show_parser.add_argument('js', help='js show')

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
            'show',
            action='store',
            help='map show [map_name]',
            nargs='?',
            default='all')

        p_show_map.set_defaults(func=self.show)

        map_parser.set_defaults(func=self.print_map_help)

    def create(self, args):
        obj_map = ex.Iscsi()
        if args.gui == 'gui':
            data = pickle.dumps(obj_map.create_map(args.map, args.hg, args.dg))
            sd.send_via_socket(data)
        else:
            obj_map.create_map(args.map, args.hg, args.dg)

    def show(self, args):
        obj_map = ex.Iscsi()
        js = iscsi_json.JSON_OPERATION()
        crmdata = obj_map.crm_up(js)
        if args.show == 'all' or args.show is None:
            print("Map:")
            maps = js.get_data("Map")
            for k in maps:
                print(" " + "---------------")
                print(" " + k + ":")
                for v in maps[k]:
                    print("     " + v)
        else:
            if js.check_key('Map', args.show):
                print(args.show + ":")
                maplist = js.get_data('Map').get(args.show)
                print(' ' + maplist[0] + ':')
                for i in js.get_data('HostGroup').get(maplist[0]):
                    print('     ' + i + ': ' + js.get_data('Host').get(i))
                print(' ' + maplist[1] + ':')
                for i in js.get_data('DiskGroup').get(maplist[1]):
                    print('     ' + i + ': ' + js.get_data('Disk').get(i))
            else:
                print("Fail! Can't find " + args.show)

    def delete(self, args):
        js = iscsi_json.JSON_OPERATION()
        obj_map = ex.Iscsi()
        print("Delete the map <", args.map, ">...")
        if js.check_key('Map', args.map):
            print(
                js.get_data('Map').get(
                    args.map),
                "will probably be affected ")
            resname = obj_map.map_data_d(js, args.map)
            if obj_map.map_crm_d(resname):
                js.delete_data('Map', args.map)
                print("Delete success!")
        else:
            print("Fail! Can't find " + args.map)

    def print_map_help(self, *args):
        self.map_parser.print_help()
