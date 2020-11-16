# coding=utf-8
import iscsi_json
import sundry as s
from execute.linstor import Linstor
from execute.crm import CRMData,CRMConfig


class Disk():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()

    def get_all_disk(self):
        linstor = Linstor()
        linstor_res = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        disks = {}
        for d in linstor_res:
            disks.update({d[1]: d[5]})
        self.js.update_data('Disk', disks)
        return disks

    def get_spe_disk(self,disk):
        self.get_all_disk()
        if self.js.check_key('Disk', disk)['result']:
            return {disk: self.js.get_data('Disk').get(disk)}

    # 展示全部disk
    def show_all_disk(self):
        list_header = ["ResourceName", "Path"]
        dict_data = self.get_all_disk()
        table = s.show_iscsi_data(list_header,dict_data)
        s.prt_log(table,0)

    # 展示指定的disk
    def show_spe_disk(self, disk):
        list_header = ["ResourceName", "Path"]
        dict_data = self.get_spe_disk(disk)
        table = s.show_iscsi_data(list_header,dict_data)
        s.prt_log(table,0)

    """
    host 操作
    """

class Host():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()


    def check_iqn(self,iqn):
        """
        判断iqn是否符合格式
        """
        if not s.re_findall(r'^iqn\.\d{4}-\d{2}\.[a-zA-Z0-9.:-]+', iqn):
            s.prt_log(f"The format of IQN is wrong. Please confirm and fill in again.", 2)

    def create_host(self, host, iqn):
        if self.js.check_key('Host', host)['result']:
            s.prt_log(f"Fail! The Host {host} already existed.",1)
        else:
            self.check_iqn(iqn)
            self.js.add_data("Host", host, iqn)
            s.prt_log("Create success!",0)
            return True

    def get_all_host(self):
        return self.js.get_data("Host")

    def get_spe_host(self,host):
        if self.js.check_key('Host', host)['result']:
            return ({host:self.js.get_data('Host').get(host)})

    def show_all_host(self):
        list_header = ["HostName", "IQN"]
        dict_data = self.get_all_host()
        table =  s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)

    def show_spe_host(self, host):
        list_header = ["HostName", "IQN"]
        dict_data = self.get_spe_host(host)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)

    def delete_host(self, host):
        if self.js.check_key('Host', host)['result']:
            if self.js.check_value('HostGroup', host)['result']:
                s.prt_log(
                    "Fail! The host in ... hostgroup.Please delete the hostgroup first",1)
            else:
                self.js.delete_data('Host', host)
                s.prt_log("Delete success!",0)
                return True
        else:
            s.prt_log(f"Fail! Can't find {host}",1)


    def modify_host(self,host,iqn):
        if self.js.check_key('Host', host)['result']:
            disk = Disk()
            disk.get_all_disk()
            self.check_iqn(iqn)
            # 添加map处理的代码
            iqn_before = self.js.get_data('Host')[host]
            obj_crm = CRMConfig()
            obj_map = Map()

            map_inuse = self.js.get_map_by_host(host)

            print(f'修改该{host}的iqn为{iqn}会影响到已存在的map：{",".join(map_inuse)}? yes/no')
            answer = input()
            if not answer in ['y', 'yes', 'Y', 'YES']:
                print('退出')
                return
            for map in map_inuse:
                iqn_all = obj_map.get_all_initiator(self.js.get_data('Map')[map]['HostGroup'])
                iqns = iqn_all.replace(iqn_before, iqn)
                for disk in self.js.get_disk_by_dg(self.js.get_data('Map')[map]['DiskGroup']):
                    obj_crm.change_initiator(disk,iqns)
            self.js.add_data('Host', host, iqn)
        else:
            s.prt_log("不存在这个host可以去进行修改",1)



    """
    diskgroup 操作
    """

class DiskGroup():
    def __init__(self):
        # 更新json文档中的disk信息
        disk = Disk()
        disk.get_all_disk()
        self.js = iscsi_json.JsonOperation()

    def create_diskgroup(self, diskgroup, disk):
        if self.js.check_key('DiskGroup', diskgroup)['result']:
            s.prt_log(f'Fail! The Disk Group {diskgroup} already existed.',1)
        else:
            for i in disk:
                if self.js.check_key('Disk', i)['result'] == False:
                    s.prt_log(f"Fail! Can't find {i}.Please give the true name.",1)
                    return

            self.js.add_data('DiskGroup', diskgroup, disk)
            s.prt_log("Create success!",0)
            return True


    def get_all_diskgroup(self):
        return self.js.get_data("DiskGroup")

    def get_spe_diskgroup(self,dg):
        if self.js.check_key('DiskGroup', dg)['result']:
            return {dg:self.js.get_data('DiskGroup').get(dg)}

    def show_all_diskgroup(self):
        list_header = ["DiskgroupName", "DiskName"]
        dict_data = self.get_all_diskgroup()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)

    def show_spe_diskgroup(self,dg):
        list_header = ["DiskgroupName", "DiskName"]
        dict_data = self.get_spe_diskgroup(dg)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)


    def delete_diskgroup(self, dg):
        if self.js.check_key('DiskGroup', dg)['result']:
            if self.js.check_value('Map', dg)['result']:
                s.prt_log("Fail! The diskgroup already map,Please delete the map",1)
            else:
                self.js.delete_data('DiskGroup', dg)
                s.prt_log("Delete success!",0)
        else:
            s.prt_log(f"Fail! Can't find {dg}",1)

    """
    hostgroup 操作
    """

class HostGroup():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()

    def create_hostgroup(self, hostgroup, host):
        if self.js.check_key('HostGroup', hostgroup)['result']:
            s.prt_log(f'Fail! The HostGroup {hostgroup} already existed.',1)
        else:
            for i in host:
                if self.js.check_key('Host', i)['result'] == False:
                    s.prt_log(f"Fail! Can't find {i}.Please give the true name.",1)
                    return

            self.js.add_data('HostGroup', hostgroup, host)
            s.prt_log("Create success!",0)
            return True


    def get_all_hostgroup(self):
        return self.js.get_data("HostGroup")

    def get_spe_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg)['result']:
            return {hg:self.js.get_data('HostGroup').get(hg)}

    def show_all_hostgroup(self):
        list_header = ["HostGroupName", "HostName"]
        dict_data = self.get_all_hostgroup()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)

    def show_spe_hostgroup(self,hg):
        list_header = ["HostGroupName", "HostName"]
        dict_data = self.get_spe_hostgroup(hg)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table,0)


    def delete_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg)['result']:
            if self.js.check_value('Map', hg)['result']:
                s.prt_log("Fail! The hostgroup already map,Please delete the map",1)
            else:
                self.js.delete_data('HostGroup', hg)
                s.prt_log("Delete success!",0)
        else:
            s.prt_log(f"Fail! Can't find {hg}",1)

    def add_host(self,hg,list_host):
        for host in list_host:
            if self.js.check_value_in_key("HostGroup", hg, host)['result']:
                print(f'{host}已存在{hg}中')
                return
            if not self.js.check_key("Host", host)['result']:
                print(f'json文件中不存在{host}，无法进行添加')
                return

        obj_map = Map()
        obj_crm = CRMConfig()
        iqn_new = ''
        map_inuse = self.js.get_map_by_hg(hg)

        # 获取新添加的iqn
        for host in list_host:
            iqn_new = f"{self.js.get_data('Host')[host]} {iqn_new}"

        print(f'修改该{hg}会影响到已存在的map：{",".join(map_inuse)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            print('退出')
            return
        for map in map_inuse:
            iqn_all = obj_map.get_all_initiator(self.js.get_data('Map')[map]['HostGroup'])

            iqns = f'{iqn_all} {iqn_new}'
            for disk in self.js.get_disk_by_dg(self.js.get_data('Map')[map]['DiskGroup']):
                obj_crm.change_initiator(disk, iqns)

        # 最后在配置文件中添加
        hg_member = self.js.get_data('HostGroup')[hg] + list_host
        self.js.add_data('HostGroup',hg,hg_member)




    def remove_host(self,hg,list_host):
        for host in list_host:
            if not self.js.check_value_in_key("HostGroup", hg, host)['result']:
                print(f'{hg}中不存在成员{host}，无法进行移除')
                return
            else:
                print(f'remove {host}')

        obj_map = Map()
        obj_crm = CRMConfig()
        iqn_new = ''
        map_inuse = self.js.get_map_by_hg(hg)


        # 获取新添加的iqn
        for host in list_host:
            iqn_new = f"{self.js.get_data('Host')[host]} {iqn_new}"

        print(f'修改该{hg}会影响到已存在的map：{",".join(map_inuse)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            print('退出')
            return
        for map in map_inuse:
            iqn_all = obj_map.get_all_initiator(self.js.get_data('Map')[map]['HostGroup'])
            list_iqn = iqn_all.split(' ')
            for host in list_host:
                list_iqn.remove(self.js.get_data('Host')[host])

            iqns = ' '.join(list_iqn)

            for disk in self.js.get_disk_by_dg(self.js.get_data('Map')[map]['DiskGroup']):
                obj_crm.change_initiator(disk, iqns)

        # 最后在配置文件中删除
        hg_member = self.js.get_data('HostGroup')[hg]
        hg_member = list(set(hg_member) - set(list_host))
        self.js.add_data('HostGroup',hg,hg_member)



    """
    map操作
    """


class Map():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()


    def pre_check_create_map(self, map, hg, dg):
        if self.js.check_key('Map', map)['result']:
            s.prt_log(f'The Map "{map}" already existed.',1)
        elif self.checkout_exist('HostGroup', hg) == False:
            s.prt_log(f"Can't find {hg}",1)
        elif self.checkout_exist('DiskGroup', dg) == False:
            s.prt_log(f"Can't find {dg}",1)
        else:
            return True

    # 检查列表的每个成员hg/dg是否存在
    def checkout_exist(self, key, data_list):
        for i in data_list:
            if self.js.check_key(key, i)['result'] == False:
                return False

    def get_initiator(self, hg):
        # 根据hg去获取hostiqn，返回由hostiqn组成的initiator
        hostiqn = []
        for h in self.js.get_data('HostGroup').get(hg):
            iqn = self.js.get_data('Host').get(h)
            hostiqn.append(iqn)
        initiator = " ".join(hostiqn)
        return initiator

    def get_target(self):
        # 获取target
        crm_data = CRMData()
        if crm_data.update_crm_conf():
            js = iscsi_json.JsonOperation()
            crm_data_dict = js.get_data('crm')
            if crm_data_dict['target']:
                # 目前的设计只有一个target，所以取列表的第一个
                target_all = crm_data_dict['target'][0]
                # 返回target_name, target_iqn
                return target_all[0], target_all[1]
            else:
                s.prt_log('No target，please create target first', 2)

    def get_disk_data(self, dg):
        # 根据dg去收集drbdd的三项数据：resource name，device name
        disk = self.js.get_data('DiskGroup').get(dg)
        linstor = Linstor()
        linstor_res = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        disks = {}
        for disk_all in linstor_res:
            # 获取diskgroup中每个disk的相关数据
            for d in disk:
                if d in disk_all:
                    disks.update({disk_all[1]: disk_all[5]})  # 取Resource, DeviceName
        return disks

    def create_map(self, map, hg, dg):
        """
        创建map
        :param map:
        :param hg: list,
        :param dg: list,
        :return:T/F
        """
        # 创建前的检查
        if not self.pre_check_create_map(map, hg, dg):
            return

        # 检查disk是否已map过
        if self.check_dg_map(map, hg, dg):
            return True

        obj_crm = CRMConfig()
        initiator = self.get_all_initiator(hg)
        target_name, target_iqn = self.get_target()
        disk_dict = self.get_all_disk(dg)

        # 用于收集创建成功的resource
        list_res_created = []

        # 执行创建和启动
        for i in disk_dict:
            res = i
            path = disk_dict[i]
            # 取DeviceName后四位数字，减一千作为lun id
            lunid = int(path[-4:]) - 1000
            # 创建iSCSILogicalUnit
            if obj_crm.create_crm_res(res, target_iqn, lunid, path, initiator):
                list_res_created.append(res)
                # 创建order，colocation
                if obj_crm.create_set(res, target_name):
                    # 尝试启动资源，成功失败都不影响创建
                    s.prt_log(f"try to start {res}", 0)
                    obj_crm.start_res(res)
                    obj_crm.checkout_status_start(res)
                else:
                    for i in list_res_created:
                        obj_crm.delete_res(i)
                    return False
            else:
                s.prt_log('Fail to create iSCSILogicalUnit',1)
                for i in list_res_created:
                    obj_crm.delete_res(i)
                return False

        self.js.add_data('Map', map, {'HostGroup':hg, 'DiskGroup':dg})
        s.prt_log('Create map success!', 0)
        return True

    def get_all_map(self):
        return self.js.get_data("Map")

    def get_spe_map(self,map):
        list_hg = []
        list_dg = []
        if not self.js.check_key('Map', map)['result']:
            s.prt_log('No map data',2)
        # {map1: {"HostGroup": [hg1, hg2], "DiskGroup": [dg1, dg2]}
        map_data = self.js.get_data('Map').get(map)
        hg_list = map_data["HostGroup"]
        dg_list = map_data["DiskGroup"]
        for hg in hg_list:
            host = self.js.get_data('HostGroup').get(hg)
            for i in host:
                iqn = self.js.get_data('Host').get(i)
                list_hg.append([hg, i, iqn])
        for dg in dg_list:
            disk = self.js.get_data('DiskGroup').get(dg)
            for i in disk:
                path = self.js.get_data('Disk').get(i)
                list_dg.append([dg, i, path])
        return [{map:map_data}, list_hg, list_dg]


    def show_all_map(self):
        list_header = ["MapName", "HostGroup","DiskGroup"]
        dict_data = self.get_all_map()
        table = s.show_map_data(list_header,dict_data)
        s.prt_log(table,0)


    def show_spe_map(self, map):
        list_data = self.get_spe_map(map)
        header_map = ["MapName", "HostGroup","DiskGroup"]
        header_host = ["HostGroup", "HostName", "IQN"]
        header_disk = ["DiskGroup", "DiskName", "Disk"]
        table_map = s.show_map_data(header_map, list_data[0])
        table_hg = s.show_spe_map_data(header_host, list_data[1])
        table_dg = s.show_spe_map_data(header_disk, list_data[2])
        result = [str(table_map), str(table_hg), str(table_dg)]
        s.prt_log('\n'.join(result),0)
        return list_data


    def pre_check_delete_map(self, map):
        if self.js.check_key('Map', map)['result']:
            return True
        else:
            s.prt(f"Fail! Can't find {map}",1)

    # 调用crm删除map
    def delete_map(self, map):
        if not self.pre_check_delete_map(map):
            return
        obj_crm = CRMConfig()
        crm_data = CRMData()
        crm_config_statu = crm_data.crm_conf_data
        map_data = self.js.get_data('Map').get(map)
        dg_list = map_data['DiskGroup']
        resname = []
        for dg in dg_list:
            resname = resname + self.js.get_data('DiskGroup').get(dg)
        if 'ERROR' in crm_config_statu:
            s.prt_log("Could not perform requested operations, are you root?",1)
        else:
            for disk in set(resname):
                map_list = self.js.get_map_by_disk(disk)
                if map_list == [map]:
                    if obj_crm.delete_res(disk) != True:
                        return False
                else:
                    iqn = self.get_initiator(disk)
                    obj_crm.change_initiator(disk, iqn)
            self.js.delete_data('Map', map)
            s.prt_log("Delete map success!", 0)
            return True

    # 对已map的dg进行二次map
    def check_dg_map(self, map, hg, dg):
        if self.js.check_value('Map', dg)['result']:
            s.prt_log("The DiskGroup already map, continue the map? yes/no",0)
            answer = input()
            if answer in ['y', 'yes', 'Y', 'YES']:
                obj_crm = CRMConfig()
                disk_list = self.get_disk_data(dg)
                initiator = self.change_merge_initiator(hg, dg)
                for disk in disk_list:
                    obj_crm.change_initiator(disk, initiator)
                self.js.add_data('Map', map, [hg, dg])
                s.prt_log('Create map success!', 0)
            return True
        else:
            return False

    # 获取已map的dg对应的hg
    def get_hg_by_dg(self, dg):
        map = self.js.get_data('Map')
        hg_list = []
        for i in map.values():
            if dg in i:
                hg_list.append(i[0])
        return hg_list

    # 修改map的hg，将hg的iqn合并
    def change_merge_initiator(self, hg, dg):
        initiator_new = self.get_initiator(hg)
        hg_list = self.get_hg_by_dg(dg)
        initiator_old = self.get_all_initiator(hg_list)
        initiator = f'{initiator_old} {initiator_new}'
        return initiator




    def get_all_initiator(self, hg_list):
        initiator = ''
        for hg in hg_list:
            initiator = f'{initiator} {self.get_initiator(hg)}'
        return initiator[1:]

    def get_all_disk(self, dg_list):
        all_disk = {}
        for dg in dg_list:
            dgdata = self.get_disk_data(dg)
            all_disk.update(dgdata)
        return all_disk


    def add_hg(self,map,list_hg):
        for hg in list_hg:
            if self.js.check_map_member(map,hg,"HostGroup"):
                print(f'{hg}已存在{map}中')
                return
            if not self.js.check_key("HostGroup", hg)['result']:
                print(f'json文件中不存在{hg}，无法进行添加')
                return

        for hg in list_hg:
            print(f'添加{hg}')


    def add_dg(self,map,list_dg):
        for dg in list_dg:
            if self.js.check_map_member(map,dg,"DiskGroup"):
                print(f'{dg}已存在{map}中')
                return
            if not self.js.check_key("DiskGroup", dg)['result']:
                print(f'json文件中不存在{dg}，无法进行添加')
                return

        for dg in list_dg:
            print(f'添加{dg}')


    def remove_hg(self,map,list_hg):
        for hg in list_hg:
            if not self.js.check_map_member(map, hg, "HostGroup"):
                print(f'{map}中不存在成员{hg}，无法进行移除')
                return
        for hg in list_hg:
            print(f'remove {hg}')


    def remove_dg(self,map,list_dg):
        for dg in list_dg:
            if not self.js.check_map_member(map, dg, "DiskGroup"):
                print(f'{map}中不存在成员{dg}，无法进行移除')
                return
        for dg in list_dg:
            print(f'remove {dg}')

    #
    # "Map": {
    #     "map1": {
    #         "HostGroup": [
    #             "hg1",
    #             "hg2"
    #         ],
    #         "DiskGroup": [
    #             "dg1",
    #             "dg2"
    #         ]
    #     }
    # }




