import json
import consts
import sundry as s
from functools import wraps
import sys


class JsonOperation():
    def __init__(self):
        self.RPL = consts.glo_rpl()
        self.json_data = self.read_json()

    # 读取json文档
    @s.deco_json_operation('读取到的JSON数据')
    def read_json(self):
        try:
            json_data = open("map_config.json", encoding='utf-8')
            json_dict = json.load(json_data)
            json_data.close()
            return json_dict

        except FileNotFoundError:
            with open('map_config.json', "w") as fw:
                json_dict = {
                    "Host": {},
                    "Disk": {},
                    "HostGroup": {},
                    "DiskGroup": {},
                    "Map": {}}
                json.dump(json_dict, fw, indent=4, separators=(',', ': '))
            return json_dict
        except json.decoder.JSONDecodeError:
            print('Failed to read json file.')
            sys.exit()


    # 创建Host、HostGroup、DiskGroup、Map
    @s.deco_json_operation('JSON添加后的资源信息')
    def add_data(self, first_key, data_key, data_value):
        self.json_data[first_key].update({data_key: data_value})
        with open('map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data[first_key]


    # 删除Host、HostGroup、DiskGroup、Map
    @s.deco_json_operation('JSON删除后的资源信息')
    def delete_data(self, first_key, data_key):
        self.json_data[first_key].pop(data_key)
        with open('map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data[first_key]

    # 获取Host,Disk、Target，HostGroup、DiskGroup、Map的信息
    @s.deco_json_operation('JSON获取资源信息')
    def get_data(self, first_key):
        all_data = self.json_data[first_key]
        return all_data

    # 检查key值是否存在
    @s.deco_json_operation('JSON检查key值的结果')
    def check_key(self,first_key,data_key):
        if data_key in self.json_data[first_key]:
            return {'type':first_key,'alias':data_key, 'result':True}
        else:
            return {'type':first_key,'alias':data_key, 'result':False}


    # 检查value值是否存在
    @s.deco_json_operation('JSON检查value值的结果')
    def check_value(self, first_key, data_value):
        for key in self.json_data[first_key]:
            if data_value in self.json_data[first_key][key]:
                return {'type':first_key,'alias':data_value,'result':True}
        return {'type':first_key,'alias':data_value,'result':False}


    # 更新disk 可能需要注意的地方：没有限制可以修改的key
    @s.deco_json_operation(f'JSON更新资源信息')
    def update_data(self, first_key, data):
        self.json_data[first_key] = data
        with open('map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data[first_key]


    # 更新crm configure资源的信息
    @s.deco_json_operation('JSON更新CRM资源信息')
    def update_crm_conf(self, resource,vip,target):
        self.json_data.update({'crm': {}})
        self.json_data['crm'].update({'resource': resource})
        self.json_data['crm'].update({'vip': vip})
        self.json_data['crm'].update({'target': target})
        with open('map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data['crm']



