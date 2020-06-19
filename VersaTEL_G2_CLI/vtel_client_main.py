import argparse
import sys
import os
import pickle

import subprocess
import linstordb
import replay
import log
import sundry
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
            username = sundry.get_username()
            transaction_id = sundry.get_transaction_id()
            logger = log.Log(username,transaction_id)
            logger.write_to_log('args_error','','',(msg % ' '.join(argv)))
            self.error(msg % ' '.join(argv))
        return args

    def print_usage(self, file=None):
        username = sundry.get_username()
        transaction_id = sundry.get_transaction_id()
        logger = log.Log(username, transaction_id)
        logger.write_to_log('result_to_show', '', '', 'print usage')
        if file is None:
            file = sys.stdout
        self._print_message(self.format_usage(), file)

    def print_help(self, file=None):
        username = sundry.get_username()
        transaction_id = sundry.get_transaction_id()
        logger = log.Log(username, transaction_id)
        logger.write_to_log('result_to_show', '', '', 'print help')
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
        self.username = sundry.get_username()
        self.transaction_id = sundry.get_transaction_id()
        self.logger = log.Log(self.username,self.transaction_id)

        self._node_commands = NodeCommands(self.logger)
        self._resource_commands = ResourceCommands(self.logger)
        self._storagepool_commands = StoragePoolCommands(self.logger)
        self._disk_commands = DiskCommands(self.logger)
        self._diskgroup_commands = DiskGroupCommands(self.logger)
        self._host_commands = HostCommands(self.logger)
        self._hostgroup_commands = HostGroupCommands(self.logger)
        self._map_commands = MapCommands(self.logger)
        self._parser = self.setup_parser()

    # def write_to_log(self,type,description1,description2,data):
    #     logger = log.Log()
    #     username = self.username
    #     transaction_id = self.transaction_id
    #     logger.add_log(username, type, transaction_id, description1, description2, data)

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

        parser_replay.set_defaults(func=self.replay)

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
            db = linstordb.LINSTORDB(self.logger)
            data = pickle.dumps(db.data_base_dump())
            sundry.send_via_socket(data)
        else:
            self.parser_stor.print_help()

    # When using the parameter '-gui', send the json through the socket
    def send_json(self, args):
        js = iscsi_json.JSON_OPERATION(self.logger)
        if args.gui:
            data = js.read_data_json()
            data_pickled = pickle.dumps(data)
            sundry.send_via_socket(data_pickled)
        else:
            self.parser_iscsi.print_help()

    def replay(self,args):
        logdb = replay.LogDB()
        logdb.produce_logdb()
        if args.transactionid and args.date:
            print('1')
        elif args.transactionid:
            cmd = logdb.get_userinput_from_tid(args.transactionid)
            result = logdb.get_result_from_tid(args.transactionid)
            print('CMD:%s'%cmd)
            subprocess.run('python3 %s'%cmd,shell=True)
            print('--------------------Output comparison--------------------')
            print(result[0])
        elif args.date:
            # python3 vtel_client_main.py re -d '2020/06/16 16:08:00' '2020/06/16 16:08:10'
            cmds = logdb.get_userinput_from_time(args.date[0],args.date[1])
            result_all = logdb.get_result_from_time(args.date[0],args.date[1])
            for cmd,res in zip(cmds,result_all):
                print('CMD:%s' % cmd)
                subprocess.run('python3 %s'%cmd,shell=True)
                print('--------------------Output comparison--------------------')
                print(res[0])
                print('========================= next ==========================')
        else:
            print('replay help')

        pass
        # import replay_test
        # replay_test.get_input(args.date,args.transactionid)


    def run(self):
        pass


    def parse(self):
        if sys.argv:
            path = sundry.get_path()
            cmd = ' '.join(sys.argv)
            self.logger.write_to_log('user_input',path,'',cmd)
        args = self._parser.parse_args()
        if args.subargs_vtel:
            args.func(args) # try expect
        else:
            self._parser.print_help()


def main():
    try:
        cmd = VtelCLI()
        cmd.parse()
    except KeyboardInterrupt:
        sys.stderr.write("\nClient exiting (received SIGINT)\n")


if __name__ == '__main__':
    main()
