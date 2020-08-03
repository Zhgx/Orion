import traceback
import execute as ex
import consts



def record_exception(func):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def wrapper(self,*args):
        try:
            return func(self,*args)
        except Exception as e:
            self.logger.write_to_log('result_to_show', 'ERR', '', str(traceback.format_exc()))
            raise e
    return wrapper


class DiskCommands():
    def __init__(self):
        self.logger = consts.get_glo_log()


    def setup_commands(self, parser):
        """
        Add commands for the disk management:create,delete,show
        """
        disk_parser = parser.add_parser(
            'disk', aliases='d', help='disk operation')
        disk_parser.set_defaults(func=self.print_disk_help)

        disk_subp = disk_parser.add_subparsers(dest='subargs_disk')

        """
        Show disk
        """

        p_show_disk = disk_subp.add_parser(
            'show', aliases='s', help='disk show')

        p_show_disk.add_argument(
            'disk',
            action='store',
            help='disk show [disk_name]',
            nargs='?',
            default='all')

        self.disk_parser = disk_parser
        self.p_show_disk = p_show_disk
        p_show_disk.set_defaults(func=self.show)



    @record_exception
    def show(self, args):
        obj_iscsi = ex.Iscsi()
        if args.disk == 'all' or args.disk is None:
            obj_iscsi.show_all_disk()
        else:
            obj_iscsi.show_spe_disk(args.disk)



    def print_disk_help(self, *args):
        self.disk_parser.print_help()
