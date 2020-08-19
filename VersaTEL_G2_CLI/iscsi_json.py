import json
import consts
import sundry as s
from functools import wraps


class JSON_OPERATION():
    def __init__(self):
        self.logger = consts.glo_log()
        self.RPL = consts.glo_rpl()
        self.json_data = self.read_json()

    # 读取json文档
    def read_json(self):
        # try:
        if self.RPL == 'no':
            oprt_id = s.create_oprt_id()
            self.logger.write_to_log('DATA', 'STR', 'read_json', '',oprt_id)
            self.logger.write_to_log('OPRT','JSON','read_json',oprt_id,'read_json')
            json_data = open("iSCSI_Data.json", encoding='utf-8')
            json_dict = json.load(json_data)
            self.logger.write_to_log('DATA','JSON','read_json',oprt_id,json_dict)
            json_data.close()
            return json_dict
        elif self.RPL == 'yes':
            logdb = consts.glo_db()
            id_result = logdb.get_id(consts.glo_tsc_id(), 'read_json')
            json_result = logdb.get_oprt_result(id_result['oprt_id'])
            if json_result:
                result = eval(json_result['result'])
            else:
                result = None
            if id_result['db_id']:
                s.change_pointer(id_result['db_id'])
            return result


        # except BaseException:
        #     with open('iSCSI_Data.json', "w") as fw:
        #         keydata = {
        #             "Host": {},
        #             "Disk": {},
        #             "HostGroup": {},
        #             "DiskGroup": {},
        #             "Map": {}}
        #         json.dump(keydata, fw, indent=4, separators=(',', ': '))
        #     return keydata

    # 创建Host、HostGroup、DiskGroup、Map
    def add_data(self, first_key, data_key, data_value):
        self.json_data[first_key].update({data_key: data_value})
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))


    # 删除Host、HostGroup、DiskGroup、Map
    def delete_data(self, first_key, data_key):
        self.json_data[first_key].pop(data_key)
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))

    # 获取Host,Disk、Target，HostGroup、DiskGroup、Map的信息
    def get_data(self, first_key):
        all_data = self.json_data[first_key]
        return all_data

    # 检查key值是否存在
    def check_key(self, first_key, data_key):
        if data_key in self.json_data[first_key]:
            return True
        else:
            return False

    # 检查value值是否存在
    @s.json_operate_decorator('JSON检查的值')
    def check_value(self, first_key, data_value):
        for key in self.json_data[first_key]:
            if data_value in self.json_data[first_key][key]:
                return True
        return False


    # 更新disk
    def update_data(self, first_key, data):
        oprt_id = s.create_oprt_id()
        RPL = consts.glo_rpl()
        self.logger.write_to_log('DATA', 'STR', 'update_data', '', oprt_id)
        self.logger.write_to_log('OPRT','json','update',oprt_id,first_key)
        self.json_data[first_key] = data
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        self.logger.write_to_log('DATA','json','update',oprt_id,data)
        if RPL == 'yes':
            logdb = consts.glo_db()
            id_result = logdb.get_id(consts.glo_tsc_id(), 'update_data')
            cmd_result = logdb.get_oprt_result(id_result['oprt_id'])
            print(f"RE:{id_result['time']} JSON更新的disk：\n{data}")
            if id_result['db_id']:
                s.change_pointer(id_result['db_id'])
            return cmd_result['result']

    # 更新crm configure资源的信息
    def update_crm_conf(self, resource,vip,target):
        self.json_data.update({'crm': {}})
        self.json_data['crm'].update({'resource': resource})
        self.json_data['crm'].update({'vip': vip})
        self.json_data['crm'].update({'target': target})
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))





