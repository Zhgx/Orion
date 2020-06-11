import json


class JSON_OPERATION:

    def __init__(self,logger):
        self.logger = logger
        self.read_data = self.read_data_json()

    # 读取json文档
    def read_data_json(self):
        try:
            rdata = open("iSCSI_Data.json", encoding='utf-8')
            read_json_dict = json.load(rdata)
            rdata.close()
            self.logger.write_to_log('json_operating','read_data_json','',read_json_dict)
            return read_json_dict
        except BaseException:
            with open('iSCSI_Data.json', "w") as fw:
                keydata = {
                    "Host": {},
                    "Disk": {},
                    "HostGroup": {},
                    "DiskGroup": {},
                    "Map": {}}
                json.dump(keydata, fw, indent=4, separators=(',', ': '))
            self.logger.write_to_log('json_operating','err','',keydata)
            return keydata

    # 创建Host、HostGroup、DiskGroup、Map
    def creat_data(self, first_key, data_key, data_value):
        self.read_data[first_key].update({data_key: data_value})
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.read_data, fw, indent=4, separators=(',', ': '))
        self.logger.write_to_log('json_operating',('Create %s'%first_key),'func_name:creat_data',{data_key: data_value})


    # 删除Host、HostGroup、DiskGroup、Map
    def delete_data(self, first_key, data_key):
        self.read_data[first_key].pop(data_key)
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.read_data, fw, indent=4, separators=(',', ': '))
        self.logger.write_to_log('json_operating',('Delete %s'%first_key),'',data_key)

    # 获取Host,Disk、Target，HostGroup、DiskGroup、Map的信息
    def get_data(self, first_key):
        all_data = self.read_data[first_key]
        self.logger.write_to_log('json_operating',('Get %s'%first_key),'',all_data)
        return all_data

    # 检查key值是否存在
    def check_key(self, first_key, data_key):
        if data_key in self.read_data[first_key]:
            self.logger.write_to_log('json_operating','Check Key %s'%data_key,'',True)
            return True
        else:
            self.logger.write_to_log('json_operating', 'Check Key %s' % data_key, '', False)
            return False

    # 检查value值是否存在
    def check_value(self, first_key, data_value):
        for key in self.read_data[first_key]:
            if data_value in self.read_data[first_key][key]:
                self.logger.write_to_log('json_operating',('Check Value %s'%first_key),data_value,True)
                return True
        self.logger.write_to_log('json_operating', ('Check Value %s' % first_key), data_value, False)
        return False


    # 更新disk
    def up_data(self, first_key, data):
        self.read_data[first_key] = data
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.read_data, fw, indent=4, separators=(',', ': '))
        self.logger.write_to_log('json_operating','Update JSON','',data)

    # 更新crm configure资源的信息
    def up_crmconfig(self, data):
        self.read_data.update({'crm': {}})
        self.read_data['crm'].update({'resource': data[0]})
        self.read_data['crm'].update({'vip': data[1]})
        self.read_data['crm'].update({'target': data[2]})
        with open('iSCSI_Data.json', "w") as fw:
            json.dump(self.read_data, fw, indent=4, separators=(',', ': '))
        self.logger.write_to_log('json_operating','Update CRM','',data)
