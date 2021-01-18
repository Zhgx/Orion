import json
import consts
import sundry as s
import threading
import pprint
from functools import wraps


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
                logger = consts.glo_log()
                oprt_id = s.create_oprt_id()
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
        if self.json_data is None:
            self.json_data = self.read_json()


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with JsonOperation._instance_lock:
                if not hasattr(cls, '_instance'):
                    JsonOperation._instance = super().__new__(cls)
        return JsonOperation._instance


    # 读取json文档
    @s.deco_json_operation('读取到的JSON数据')
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
            return json_dict
        except json.decoder.JSONDecodeError:
            s.prt_log('Failed to read json file.',2)

    @s.deco_json_operation('提交了JSON数据')
    def commit_json(self):
        with open('../vplx/map_config.json', "w") as fw:
            json.dump(self.json_data, fw, indent=4, separators=(',', ': '))
        return self.json_data


    # 获取Host,Disk、Target，HostGroup、DiskGroup、Map的信息
    def get_data(self, first_key):
        all_data = self.json_data[first_key]
        return all_data




    # 检查key值是否存在
    @s.deco_json_operation('JSON检查key值的结果')
    def check_key(self, type, target):
        """
        检查某个类型的目标是不是在存在
        """
        if target in self.json_data[type]:
            return True
        else:
            return False


    # 检查value值是否存在
    @s.deco_json_operation('JSON检查value值的结果')
    def check_value(self, type, target):
        """
        检查目标是不是作为某种资源的使用
        """
        for key in self.json_data[type]:
            if target in self.json_data[type][key]:
                return True
        return False


    @s.deco_json_operation('JSON检查某个key值是否存在于某个value值')
    def check_value_in_key(self, type, key, value):
        """
        检查某个key值是否存在某个value值,默认
        """
        if key in self.json_data[type]:
            if value in self.json_data[type][key]:
                return True
            else:
                return False


    def check_in_res(self,res,type,target):
        """
        检查目标资源在不在某个res的成员里面，res：Map，Target，Portal
        :param res:
        :param type:
        :param target:
        :return:
        """
        for res in self.json_data[res].values():
            if target in res[type]:
                return True
        return False



    @s.deco_json_operation('JSON通过host获取到所有相关的hostgroup')
    def get_hg_by_host(self,host):
        """
        通过host取到使用这个host的所有hg
        :param host:str
        :return:list
        """
        list_host = []
        for hg,hg_member in self.json_data["HostGroup"].items():
            if host in hg_member:
                list_host.append(hg)
        return list_host

        # list_host = []
        # if not isinstance(host,list):
        #     host = [host]
        # for host_one in host:
        #     for hg,hg_member in self.json_data["HostGroup"].items():
        #         if host_one in hg_member:
        #             list_host.append(hg)
        # return list_host

    @s.deco_json_operation('JSON通过map获取到所有相关的diskgroup/hostgroup')
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


    @s.deco_json_operation('JSON通过dg列表获取到所有相关的disk')
    def get_disk_by_dg(self,list_dg):
        """
        过dg列表获取到所有相关的disk
        :param dg:list
        :return:list
        """
        list_disk = []
        for dg in list_dg:
            list_disk+=self.get_data('DiskGroup')[dg]
        return list(set(list_disk))

    @s.deco_json_operation('JSON通过host获取到所有相关的map')
    # 问题：日志记录的是只需要通过host获取到map的这一数据，还是需要将通过host获取到map的过程也记录下来（通过host获取hg，通过hg获取map）
    # 目前的通过调用get_hg_by_host()和get_map_by_group()，这两个方法也会进行日志的记录。
    # 下面一个方法get_map_by_disk()，就只会记录通过disk获取到的map这一数据，过程(get_dg_by_disk，get_map_by_group)就不进行记录。
    def get_map_by_host(self,host):
        list_map = []
        list_hg = self.get_hg_by_host(host)
        for hg in list_hg:
            list_map.extend(self.get_map_by_group('HostGroup',hg))
        return list(set(list_map))

    @s.deco_json_operation('JSON通过disk获取到所有相关的map')
    def get_map_by_disk(self, disk):
        # 使用
        # list_map = []
        # list_dg = self.get_dg_by_disk(disk)
        # for dg in list_dg:
        #     list_map.extend(self.get_map_by_group('DiskGroup',dg))
        # return list(set(list_map))

        dg_dict = self.get_data("DiskGroup")
        map_dict = self.get_data("Map")
        # 根据disk获取dg
        dg_list = []
        for dg in dg_dict.items():
            if disk in dg[1]:
                dg_list.append(dg[0])
        # 根据dg获取map
        map_list = []
        for dg in dg_list:
            for map in map_dict.items():
                if dg in map[1]['DiskGroup']:
                    map_list.append(map[0])
        return list(set(map_list))

    @s.deco_json_operation('JSON通过disk获取到所有相关的iqn')
    def get_iqn_by_disk(self,disk):
        """
        通过disk获取到对应iSCSILogicalUnit的allowed initiators
        allowed initiators即host的iqn
        :param disk:str
        :return:list
        """
        # 通过disk获取dg
        list_initiator = []
        list_hg = []
        list_host = []
        list_map = self.get_map_by_disk(disk)
        for map in list_map:
            list_hg+=self.get_data('Map')[map]['HostGroup']

        for hg in set(list_hg):
            for host in self.get_data('HostGroup')[hg]:
                list_host.append(host)

        for host in set(list_host):
            list_initiator.append(self.get_data('Host')[host])

        return list(set(list_initiator))


    @s.deco_json_operation('JSON通过disk获取到相关的dg')
    def get_dg_by_disk(self,disk):
        list_dg = []
        dict_dg = self.get_data('DiskGroup')
        for dg,member in dict_dg.items():
            if disk in member:
                list_dg.append(dg)
        return list(set(list_dg))




    @s.deco_json_operation('JSON通过disk获取到相关的hg')
    #"改改改"
    def get_disk_by_hg(self,hg):
        list_map = self.get_map_by_group('HostGroup',hg)
        list_disk = []
        for map in list_map:
            for disk in self.get_disk_by_dg(self.get_data('Map')[map]['DiskGroup']):
                list_disk.append(disk)
        return list(set(list_disk))



    @s.deco_json_operation('JSON通过disk获取到相关的host')
    def get_disk_by_host(self,host):
        """
        通过disk获取到相关的host
        :param host: str
        :return:
        """
        list_disk = []
        list_map = self.get_map_by_host(host)
        for map in list_map:
            for disk in self.get_disk_by_dg(self.get_data('Map')[map]['DiskGroup']):
                list_disk.append(disk)
        return list(set(list_disk))


    @s.deco_json_operation('JSON通过map获取到相关的iqn')
    def get_iqn_by_map(self, map):
        list_iqn = []
        hg_list = self.get_data('Map')[map]['HostGroup']
        list_iqn.extend(self.get_iqn_by_hg(hg_list))
        return list(set(list_iqn))


    @s.deco_json_operation('JSON通过hg列表获取到相关的iqn')
    def get_iqn_by_hg(self,list_hg):
        list_iqn = []
        for hg in list_hg:
            for host in self.get_data('HostGroup')[hg]:
                iqn = self.get_data('Host')[host]
                list_iqn.append(iqn)

        return list(set(list_iqn))


    # 更新Host、HostGroup、DiskGroup、Map的某一个成员的数据
    @deco_oprt_json('JSON更新后的数据（某资源的成员）')
    def update_data(self, first_key, data_key, data_value):
        self.json_data[first_key].update({data_key: data_value})
        return self.json_data[first_key]


    # 更新该资源的全部数据
    @deco_oprt_json(f'JSON更新后的数据（某资源的全部）')
    def cover_data(self, first_key, data):
        self.json_data[first_key] = data
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
            list_member = self.get_data('Map')[target][iscsi_type]
        else:
            list_member = self.get_data(iscsi_type)[target]
        list_member.extend(member)

        if type == 'Map':
            dict_map = self.get_data('Map')[target]
            dict_map.update({iscsi_type:list_member})
            self.update_data('Map',target,dict_map)
        else:
            self.update_data(iscsi_type, target, list(set(list_member)))



    def remove_member(self,iscsi_type,target,member,type=None):
        if type == 'Map':
            list_member = self.get_data('Map')[target][iscsi_type]
        else:
            list_member = self.get_data(iscsi_type)[target]

        for i in member:
            list_member.remove(i)

        if type == 'Map':
            dict_map = self.get_data('Map')[target]
            dict_map.update({iscsi_type:list_member})
            self.update_data('Map',target,dict_map)
        else:
            self.update_data(iscsi_type, target, list(set(list_member)))


    # 删除Host、HostGroup、DiskGroup、Map
    @deco_oprt_json('JSON删除后的资源信息')
    def delete_data(self, first_key, data_key):
        self.json_data[first_key].pop(data_key)
        return self.json_data[first_key]