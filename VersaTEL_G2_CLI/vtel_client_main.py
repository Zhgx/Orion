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

    def _print_message(self, message, file=None):
        if message:
            if file is None:
                file = sys.stderr
            file.write(message)




class VtelCLI(object):
    """
    Vtel command line client
    """
    def __init__(self):
        consts._init()
        self.username = sundry.get_username()
        self.transaction_id = sundry.create_transaction_id()
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
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)

        parser_iscsi = subp.add_parser(
            'iscsi',
            help='Management operations for iSCSI',
            add_help=False)


        parser_iscsi.add_argument(
            '-gui',
            dest='gui',
            action='store_true',
            help=argparse.SUPPRESS,
            default=False)


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

        self.parser_stor = parser_stor
        self.parser_iscsi = parser_iscsi
        self.parser_replay = parser_replay

        # Set the binding function of stor
        parser_stor.set_defaults(func=self.send_database)
        # Set the binding function of iscsi
        parser_iscsi.set_defaults(func=self.send_json)


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

        parser.set_defaults(func=parser.print_help)

        return parser

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


    # def replay_run(self,cmd_list):
    #     if not cmd_list:
    #         print('不存在命令去进行replay')
    #         return
    #
    #     trasanction_num = len(cmd_list)
    #
    #
    #     for replay_cmd in cmd_list:
    #         print(f"--------------transaction:{replay_cmd['tid']}--------------")
    #         consts.set_glo_tsc_id(replay_cmd['tid'] )
    #         if replay_cmd:
    #             print(replay_cmd)
    #             if not replay_cmd['valid'] == 0:
    #                 replay_args = self._parser.parse_args(replay_cmd['user_input']['cmd'].split())
    #                 print(f"* 执行命令：{replay_cmd['user_input']['cmd']} *")
    #                 try:
    #                     replay_args.func(replay_args)
    #                 except consts.ReplayExit:
    #                     print('该事务replay结束')
    #                 except Exception:
    #                     print(str(traceback.format_exc()))
    #             else:
    #                 print(f"该命令{replay_cmd['cmd']}有误，无法执行")
    #
    #             # if not replay_cmd['type'] == 'err':
    #             #     replay_args = self._parser.parse_args(replay_cmd['cmd'].split())
    #             #     print(f"* 执行命令：{replay_cmd['cmd']} *")
    #             #     try:
    #             #         replay_args.func(replay_args)
    #             #     except consts.ReplayExit:
    #             #         print('该事务replay结束')
    #             #     except Exception:
    #             #         print(str(traceback.format_exc()))
    #             #
    #             # else:
    #             #     print(f"该命令{replay_cmd['cmd']}有误，无法执行")
    #         else:
    #             print('该事务id:不存在或者不符合replay条件（python vtel_client_main）')


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
            print(f"{i+1} transaction:{dict_input[i]['tid']} cmd:{dict_input[i]['cmd']}")


        print('请输入要执行replay的序号，或者all：')
        answer = ''
        while answer != 'exit':
            answer = input()
            if answer in number_list:
                dict_cmd = dict_input[int(answer)-1]
                self.replay_one(dict_cmd)

            elif answer == 'all':
                for dict_cmd in dict_input:
                    self.replay_one(dict_cmd)
            else:
                print('输入的序号不正确')


    def replay(self,args):
        logdb = consts.glo_db()
        consts.set_glo_log_switch('no')
        if args.transactionid and args.date:
            print('Please specify only one type of data for replay')
            return
        elif args.transactionid:
            dict_cmd = logdb.get_userinput_via_tid(args.transactionid)
            print('* MODE : REPLAY *')
            print(f'transaction num : 1')
            self.replay_one(dict_cmd)
        elif args.date:
            dict_cmd = logdb.get_userinput_via_time(args.date[0],args.date[1])
            self.replay_more(dict_cmd)
        else:
            dict_cmd = logdb.get_all_transaction()
            self.replay_more(dict_cmd)
        return dict_cmd




    def parse(self):
        args = self._parser.parse_args()
        path = sundry.get_path()
        cmd = ' '.join(sys.argv[1:])

        if args.subargs_vtel:
            if args.subargs_vtel in ['re', 'replay']:
                consts.set_glo_rpl('yes')
                logdb.prepare_db()
                # cmd = self.replay_collect(args)
                # self.replay_run_date(cmd)
                self.replay(args)
            else:
                self.logger.write_to_log('DATA','INPUT','cmd_input',path,{'valid':'0','cmd':cmd})
                args.func(args)
        else:
            self.logger.write_to_log('DATA','INPUT','cmd_input', path, {'valid':'0','cmd':cmd})
            self._parser.print_help()


def main():
    try:
        cmd = VtelCLI()
        cmd.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nClient exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()
