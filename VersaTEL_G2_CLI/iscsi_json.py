import json
import consts


class JSON_OPERATION():
    def __init__(self):
        self.logger = consts.get_glo_log()
        self.json_data = self.read_json()

    # 读取json文档
    def read_json(self):
        try:
            json_data = open("iSCSI_Data.json", encoding='utf-8')
            json_dict = json.load(json_data)
            json_data.close()
            return json_dict
        except BaseException:
            with open('iSCSI_Data.json', "w") as fw:
                keydata = {
                    "Host": {},
                    "Disk": {},
                    "HostGroup": {},
                    "DiskGroup": {},
                    "Map": {}}
                json.dump(keydata, fw, indent=4, separators=(',', ': '))
            return keydata

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
    def check_value(self, first_key, data_value):
        for key in self.json_data[first_key]:
            if data_value in self.json_data[first_key][key]:
                return True
        return False


    # 更新disk
    def update_data(self, first_key, data):
        self.json_data[first_key] = data
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))

    # 更新crm configure资源的信息
    def update_crm_conf(self, data):
        self.json_data.update({'crm': {}})
        self.json_data['crm'].update({'resource': data[0]})
        self.json_data['crm'].update({'vip': data[1]})
        self.json_data['crm'].update({'target': data[2]})
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
