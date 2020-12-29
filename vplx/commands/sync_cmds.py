import execute as ex
import consts
import sundry as sd


class SyncCommands():
    def __init__(self):
        self.logger = consts.glo_log()

    def setup_commands(self, parser):
        """
        Add commands for the disk management:create,delete,show
        """
        sync_parser = parser.add_parser(
            'sync', help='sync data')
        sync_parser.set_defaults(func=self.sycn_data)


    @sd.deco_record_exception
    def sycn_data(self, args):
        pass
