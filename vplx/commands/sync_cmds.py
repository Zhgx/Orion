import consts
import sundry as sd
from execute import CRMData
import iscsi_json



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
        # 添加前置检查
        pass

        obj_crm = CRMData()
        js = iscsi_json.JsonOperation()
        vip = obj_crm.get_vip()
        portblock = obj_crm.get_portblock()
        target = obj_crm.get_target()
        portal = obj_crm.get_portal_data(vip,portblock,target)
        js.json_data.update({'Portal': portal})
        js.json_data.update({'Target': target})
        js.commit_json()
        sd.prt_log('JSON数据更新完成', 1)




