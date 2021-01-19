import json
import threading
import pprint
from functools import wraps


import consts
import sundry as s
import log


def deco_oprt_json(str):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            # print(traceback.extract_stack()[-2])
            # print(traceback.extract_stack()[-3])
            if RPL == 'no':
                logger = log.Log()
                oprt_id = log.create_oprt_id()
                logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
                logger.write_to_log('OPRT', 'JSON', func.__name__, oprt_id, args)
                result = func(self,*args)
                logger.write_to_log('DATA', 'JSON', func.__name__, oprt_id,result)
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
                json_result = logdb.get_oprt_result(id_result['oprt_id'])
                if json_result['result']:
                    result = eval(json_result['result'])
                else:
                    result = ''
                func(self,*args)
                print(f"RE:{id_result['time']} {str}:")
                pprint.pprint(result)
                print()
                if id_result['db_id']:
                    s.change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate



class JsonOperation(object):
    _instance_lock = threading.Lock()
    json_data = None

    def __init__(self):
        consts.init()
        
        if self.json_data is None:
            self.json_data = self.read_json()


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with JsonOperation._instance_lock:
                if not hasattr(cls, '_instance'):
                    JsonOperation._instance = super().__new__(cls)
        return JsonOperation._instance


    # 读取json文档
    @s.deco_json_operation('<JSON>read json:')
    def read_json(self):
        try:
            json_data = open("../vplx/map_config.json", encoding='utf-8')
            json_dict = json.load(json_data)
            json_data.close()
            return json_dict

        except FileNotFoundError:
            with open('../vplx/map_config.json', "w") as fw:
                json_dict = {
                    "Host": {},
                    "Disk": {},
                    "HostGroup": {},
                    "DiskGroup": {},
                    "Map": {},
                    "Portal":{},
                    "Target":{}}
                json.dump(json_dict, fw, indent=4, separators=(',', ': '))
            s.prt_log('The configuration file has been created, you can enter "vtel iscsi sync" to synchronize data later',2)
        except json.decoder.JSONDecodeError:
            s.prt_log('Failed to read configuration file.',2)

    @s.deco_json_operation('<JSON>commit data')
    def commit_data(self):
        with open('../vplx/map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data


    # 检查key值是否存在
    @s.deco_json_operation('<JSON>check key:')
    def check_key(self, key, target):
        """
        检查某个类型的目标是不是在存在
        """
        if target in self.json_data[key]:
            return True
        else:
            return False


    # 检查value值是否存在
    @s.deco_json_operation('<JSON>check value:')
    def check_value(self, key, target):
        """
        检查目标是不是作为某种资源的使用
        """
        for data in self.json_data[key].values():
            if target in data:
                return True
        return False


    @s.deco_json_operation('<JSON>check if it is used：')
    def check_in_res(self,res,member,target):
        """
        检查目标资源在不在某个res的成员里面，res：Map，Target，Portal
        :param res:
        :param member: 比如HostGroup/DiskGroup
        :param target:
        :return:
        """
        for data in self.json_data[res].values():
            if target in data[member]:
                return True
        return False


    @s.deco_json_operation('<JSON>get all map:')
    def get_map_by_group(self,type,group):
        """
        通过hg/dg取到使用这个hg的所有map
        :param type: "HostGroup"/"DiskGroup"
        :param group: str, hg/dg
        :return:
        """
        list_map = []
        for map,map_member in self.json_data['Map'].items():
            if group in map_member[type]:
                list_map.append(map)
        return list_map


    # 更新Host、HostGroup、DiskGroup、Map的某一个成员的数据
    @deco_oprt_json('<JSON>update data:')
    def update_data(self, first_key, data_key, data_value):
        self.json_data[first_key].update({data_key: data_value})
        return self.json_data[first_key]


    # 更新该资源的全部数据
    @deco_oprt_json(f'<JSON>update all data:）')
    def cover_data(self, first_key, data):
        self.json_data[first_key] = data
        return self.json_data[first_key]
    
    
    # 删除Host、HostGroup、DiskGroup、Map
    @deco_oprt_json('<JSON>delete data:')
    def delete_data(self, first_key, data_key):
        self.json_data[first_key].pop(data_key)
        return self.json_data[first_key]


    def append_member(self,iscsi_type,target,member,type=None):
        """
        :param iscsi_type:
        :param target:
        :param member: list
        :param type: 'DiskGroup'/'HostGroup'
        :return:
        """
        if type == 'Map':
            list_member = self.json_data['Map'][target][iscsi_type]
        else:
            list_member = self.json_data[iscsi_type][target]
        list_member.extend(member)

        if type == 'Map':
            dict_map = self.json_data['Map'][target]
            dict_map.update({iscsi_type:list_member})
            self.update_data('Map',target,dict_map)
        else:
            self.update_data(iscsi_type, target, list(set(list_member)))



    def remove_member(self,iscsi_type,target,member,type=None):
        if type == 'Map':
            list_member = self.json_data['Map'][target][iscsi_type]
        else:
            list_member = self.json_data[iscsi_type][target]

        for i in member:
            list_member.remove(i)

        if type == 'Map':
            dict_map = self.json_data['Map'][target]
            dict_map.update({iscsi_type:list_member})
            self.update_data('Map',target,dict_map)
        else:
            self.update_data(iscsi_type, target, list(set(list_member)))


    def arrange_data(self,type,res):
        """
        删除了传入的资源之后，处理与之相关的其他资源数据
        :param type: 被删除的资源类型 host/hg/dg
        :param res: 被删除的资源名称
        :return:
        """
        import copy
        data = copy.deepcopy(self.json_data)

        if type == 'Host':
            # 会影响到hg，map
            list_hg_delete = []
            for hg,list_host in data['HostGroup'].items():
                if res in list_host:
                    if len(list_host) > 1:
                        self.remove_member('HostGroup',hg,[res])
                    else:
                        list_hg_delete.append(hg)
                        self.delete_data('HostGroup',hg)
            for hg in list_hg_delete:
                for map,map_data in data['Map'].items():
                    if hg in map_data['HostGroup']:
                        if len(data['Map'][map]['HostGroup'])>1:
                            self.remove_member('HostGroup', map, [hg], type='Map')
                        else:
                            self.delete_data('Map', map)

        elif type == 'hg' or type == 'HostGroup':
            # 会影响到map
            for map in data['Map']:
                if len(data['Map'][map]['HostGroup']) > 1:
                    self.remove_member('HostGroup', map, [res], type='Map')
                else:
                    self.delete_data('Map', map)

        elif type == 'dg' or type == 'DiskGroup':
            # 会影响到map
            for map in data['Map']:
                if len(data['Map'][map]['DiskGroup']) > 1:
                    self.remove_member('DiskGroup', map, [res], type='Map')
                else:
                    self.delete_data('Map', map)
        else:
            raise TypeError('type must be "host/hg/dg"')




