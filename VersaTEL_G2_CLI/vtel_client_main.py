import argparse
import traceback
import sys
import pickle
import linstordb
import logdb
import log
import sundry
import consts
import iscsi_json
import pytest

from commands import (
    NodeCommands,
    ResourceCommands,
    StoragePoolCommands,
    DiskCommands,
    DiskGroupCommands,
    HostCommands,
    HostGroupCommands,
    MapCommands
)

class MyArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = ('unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        return args

    def print_usage(self, file=None):
        logger = consts.glo_log()
        cmd = ' '.join(sys.argv[1:])
        path = sundry.get_path()
        logger.write_to_log('DATA', 'INFO', 'cmd_input', path, {'valid':'1','cmd':cmd})
        logger.write_to_log('INFO', 'INFO', 'finish','', 'print usage')
        if file is None:
            file = sys.stdout
        self._print_message(self.format_usage(), file)

    def print_help(self, file=None):
        logger = consts.glo_log()
        logger.write_to_log('INFO', 'INFO', 'finish','', 'print help')
        if file is None:
            file = sys.stdout
        self._print_message(self.format_help(), file)

    # def _print_message(self, message, file=None):
    #     if message:
    #         if file is None:
    #             file = sys.stderr
    #         file.write(message)




class VtelCLI(object):
    """
    Vtel command line client
    """
    def __init__(self):
        consts._init()
        self.username = sundry.get_username()
        self.transaction_id = sys.argv[-1] if '-gui' in sys.argv \
            else sundry.create_transaction_id()
        self.logger = log.Log(self.username,self.transaction_id)
        consts.set_glo_log(self.logger)
        self.replay_args_list = []
        self._node_commands = NodeCommands()
        self._resource_commands = ResourceCommands()
        self._storagepool_commands = StoragePoolCommands()
        self._disk_commands = DiskCommands()
        self._diskgroup_commands = DiskGroupCommands()
        self._host_commands = HostCommands()
        self._hostgroup_commands = HostGroupCommands()
        self._map_commands = MapCommands()
        self._parser = self.setup_parser()


    def setup_parser(self):
        parser = MyArgumentParser(prog="vtel")
        """
        Set parser vtel sub-parser
        """
        #parser.add_argument('--version','-v',action='version',version='%(prog)s ' + VERSION + '; ')


        subp = parser.add_subparsers(metavar='',
                                     dest='subargs_vtel')


        parser_stor = subp.add_parser(
            'stor',
            help='Management operations for LINSTOR',
            add_help=False,
            formatter_class=argparse.RawTextHelpFormatter,
        )


        # add parameters to interact with the GUI
        parser_stor.add_argument(
            '-gui',
            dest='gui',
            action='store',
            help=argparse.SUPPRESS)

        parser_iscsi = subp.add_parser(
            'iscsi',
            help='Management operations for iSCSI',
            add_help=False)


        parser_iscsi.add_argument(
            '-gui',
            dest='gui',
            action='store',
            help=argparse.SUPPRESS)


        # replay function related parameter settings
        parser_replay = subp.add_parser(
            'replay',
            aliases=['re'],
            formatter_class=argparse.RawTextHelpFormatter
        )

        parser_replay.add_argument(
            '-t',
            '--transactionid',
            dest='transactionid',
            metavar='',
            help='transaction id')

        parser_replay.add_argument(
            '-d',
            '--date',
            dest='date',
            metavar='',
            nargs=2,
            help='date')

        parser_replay.add_argument(
            '-rg',
            dest = 'rg',
            action='store_true',
            default=False,
            help='RegresessionTesting')


        parser_regress = subp.add_parser(
            'regress',
            aliases=['rt'],
            formatter_class=argparse.RawTextHelpFormatter
        )

        parser_regress.add_argument(
            '-t',
            '--transactionid',
            dest='transactionid',
            metavar='',
            help='transaction id')

        parser_regress.add_argument(
            '-d',
            '--date',
            dest='date',
            metavar='',
            nargs=2,
            help='date')



        self.parser_stor = parser_stor
        self.parser_iscsi = parser_iscsi
        self.parser_replay = parser_replay

        # Set the binding function of stor
        parser_stor.set_defaults(func=self.send_database)
        # Set the binding function of iscsi
        parser_iscsi.set_defaults(func=self.send_json)
        parser_replay.set_defaults(func=self.replay)
        parser_regress.set_defaults(func=self.regress)


        # 绑定replay有问题
        # parser_replay.set_defaults(func=self.replay)

        subp_stor = parser_stor.add_subparsers(dest='subargs_stor',metavar='')
        subp_iscsi = parser_iscsi.add_subparsers(dest='subargs_iscsi',metavar='')

        # add all subcommands and argument
        self._node_commands.setup_commands(subp_stor)
        self._resource_commands.setup_commands(subp_stor)
        self._storagepool_commands.setup_commands(subp_stor)

        self._disk_commands.setup_commands(subp_iscsi)
        self._diskgroup_commands.setup_commands(subp_iscsi)
        self._host_commands.setup_commands(subp_iscsi)
        self._hostgroup_commands.setup_commands(subp_iscsi)
        self._map_commands.setup_commands(subp_iscsi)

        parser.set_defaults(func=self.print_vtel_help)

        return parser


    def print_vtel_help(self,*args):
        self._parser.print_help()

    # When using the parameter '-gui', send the database through the socket
    def send_database(self, args):
        if args.gui:
            db = linstordb.LinstorDB()
            data = pickle.dumps(db.data_base_dump())
            sundry.send_via_socket(data)
        else:
            self.parser_stor.print_help()

    # When using the parameter '-gui', send the json through the socket
    def send_json(self, args):

        if args.gui:
            js = iscsi_json.JSON_OPERATION()
            data = js.read_json()
            data_pickled = pickle.dumps(data)
            sundry.send_via_socket(data_pickled)
        else:
            self.parser_iscsi.print_help()


    def replay_one(self,dict_input):
        if not dict_input:
            print('不存在命令去进行replay')
            return
        print(f"\n-------------- transaction: {dict_input['tid']}  command: {dict_input['cmd']} --------------")
        consts.set_glo_tsc_id(dict_input['tid'])
        if dict_input['valid'] == '0':
            replay_args = self._parser.parse_args(dict_input['cmd'].split())
            try:
                replay_args.func(replay_args)
            except consts.ReplayExit:
                print('该事务replay结束')
            except Exception:
                print(str(traceback.format_exc()))
        else:
            print(f"该命令{dict_input['cmd']}有误，无法执行")


    def replay_more(self,dict_input):
        print('* MODE : REPLAY *')
        print(f'transaction num : {len(dict_input)}')

        number_list = [str(i) for i in list(range(1,len(dict_input)+1))]
        for i in range(len(dict_input)):
            print(f"{i+1:<3} Transaction ID: {dict_input[i]['tid']:<12} CMD: {dict_input[i]['cmd']}")

        answer = ''
        while answer != 'exit':
            print('请输入要执行replay的序号，或者all，输入exit退出：')
            answer = input()
            if answer in number_list:
                dict_cmd = dict_input[int(answer)-1]
                self.replay_one(dict_cmd)
                consts.set_glo_log_id(0)

            elif answer == 'all':
                for dict_cmd in dict_input:
                    self.replay_one(dict_cmd)
            else:
                print('输入的序号不正确')


    def replay(self,args):
        consts.set_glo_log_switch('no')
        consts.set_glo_rpl('yes')
        obj_logdb = logdb.prepare_db()

        if args.rg:
            consts.set_glo_rg('yes')

        if args.transactionid and args.date:
            print('Please specify only one type of data for replay')
            return
        elif args.transactionid:
            dict_cmd = obj_logdb.get_userinput_via_tid(args.transactionid)
            print('* MODE : REPLAY *')
            print(f'transaction num : 1')
            self.replay_one(dict_cmd)
            # print('--------------')
            # import pprint
            # pprint.pprint(consts.glo_rpldata())
            # pytest.main(['-m', dict_cmd['cmd'].replace(' ','_'), 'test/test_cmd.py'])

        elif args.date:
            dict_cmd = obj_logdb.get_userinput_via_time(args.date[0],args.date[1])
            self.replay_more(dict_cmd)
        else:
            dict_cmd = obj_logdb.get_all_transaction()
            self.replay_more(dict_cmd)

        return dict_cmd

    def regress_run(self,dict_cmd):
        print('* MODE : Regression Testing *')
        for one in dict_cmd:
            print(f"\n-------------- transaction: {one['tid']}  command: {one['cmd']} --------------")
            if dict_cmd['valid'] == '0':
                consts.set_glo_tsc_id(one['tid'])
                # pytest.main(['-m', one['cmd'].replace(' ', '_'), 'test/test_cmd.py'])
            else:
                print(f"该命令{dict_cmd['cmd']}有误")


    def regress(self,args):
        consts.set_glo_log_switch('no')
        consts.set_glo_rpl('yes')
        obj_logdb = logdb.prepare_db()
        if args.transactionid and args.date:
            print('Please specify only one type of data for regression testing.')
            return
        elif args.transactionid:
            dict_cmd = [obj_logdb.get_userinput_via_tid(args.transactionid)]
            self.regress_run(dict_cmd)
        elif args.date:
            dict_cmd = obj_logdb.get_userinput_via_time(args.date[0],args.date[1])
            self.regress_run(dict_cmd)
        else:
            dict_cmd = obj_logdb.get_all_transaction()
            self.regress_run(dict_cmd)


    def parse(self): # 调用入口
        args = self._parser.parse_args()
        path = sundry.get_path()
        cmd = ' '.join(sys.argv[1:])

        if args.subargs_vtel:
            if args.subargs_vtel not in ['re', 'replay','regress','rt']:
                self.logger.write_to_log('DATA', 'INPUT', 'cmd_input', path, {'valid': '0', 'cmd': cmd})
        else:
            self.logger.write_to_log('DATA','INPUT','cmd_input', path, {'valid':'0','cmd':cmd})

        args.func(args)


def main():
    try:
        cmd = VtelCLI()
        cmd.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nClient exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()
