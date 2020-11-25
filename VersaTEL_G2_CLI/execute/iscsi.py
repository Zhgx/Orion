# coding=utf-8
import iscsi_json
import sundry as s
from execute.linstor import Linstor
from execute.crm import CRMData, CRMConfig


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

    def get_spe_disk(self, disk):
        self.get_all_disk()
        if self.js.check_key('Disk', disk)['result']:
            return {disk: self.js.get_data('Disk').get(disk)}

    # 展示全部disk
    def show_all_disk(self):
        list_header = ["ResourceName", "Path"]
        dict_data = self.get_all_disk()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    # 展示指定的disk
    def show_spe_disk(self, disk):
        list_header = ["ResourceName", "Path"]
        dict_data = self.get_spe_disk(disk)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    """
    host 操作
    """


class Host():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()

    def check_iqn(self, iqn):
        """
        判断iqn是否符合格式
        """
        if not s.re_findall(r'^iqn\.\d{4}-\d{2}\.[a-zA-Z0-9.:-]+', iqn):
            s.prt_log(f"The format of IQN is wrong. Please confirm and fill in again.", 2)

    def create_host(self, host, iqn):
        if self.js.check_key('Host', host)['result']:
            s.prt_log(f"Fail! The Host {host} already existed.", 1)
        else:
            self.check_iqn(iqn)
            self.js.add_data("Host", host, iqn)
            s.prt_log("Create success!", 0)
            return True

    def get_all_host(self):
        return self.js.get_data("Host")

    def get_spe_host(self, host):
        if self.js.check_key('Host', host)['result']:
            return ({host: self.js.get_data('Host').get(host)})

    def show_all_host(self):
        list_header = ["HostName", "IQN"]
        dict_data = self.get_all_host()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def show_spe_host(self, host):
        list_header = ["HostName", "IQN"]
        dict_data = self.get_spe_host(host)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def delete_host(self, host):
        if self.js.check_key('Host', host)['result']:
            if self.js.check_value('HostGroup', host)['result']:
                s.prt_log(
                    "Fail! The host in ... hostgroup.Please delete the hostgroup first", 1)
            else:
                self.js.delete_data('Host', host)
                s.prt_log("Delete success!", 0)
                return True
        else:
            s.prt_log(f"Fail! Can't find {host}", 1)



    def verf_modify_host(self,host,iqn):
        if not self.js.check_key('Host',host)['result']:
            s.prt_log("不存在这个host可以去进行修改", 2)

        list_disk = self.js.get_disk_by_host(host)

        print(f'修改该{host}的iqn为{iqn}会影响到已存在的disk:{",".join(list_disk)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改,退出',2)

    def modify_host(self, host, iqn):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.add_data('Host', host, iqn)
        obj_crm = CRMConfig()

        list_disk = self.js.get_disk_by_host(host)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                print(f'删除{disk}')
                obj_crm.delete_res(disk)
            else:
                print(f'修改{disk}的iqn为{iqn_now}')
                obj_crm.change_initiator(disk, iqn_now)

        self.js.add_data('Host', host, iqn)



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
            s.prt_log(f'Fail! The Disk Group {diskgroup} already existed.', 1)
        else:
            for i in disk:
                if self.js.check_key('Disk', i)['result'] == False:
                    s.prt_log(f"Fail! Can't find {i}.Please give the true name.", 1)
                    return

            self.js.add_data('DiskGroup', diskgroup, disk)
            s.prt_log("Create success!", 0)
            return True

    def get_all_diskgroup(self):
        return self.js.get_data("DiskGroup")

    def get_spe_diskgroup(self, dg):
        if self.js.check_key('DiskGroup', dg)['result']:
            return {dg: self.js.get_data('DiskGroup').get(dg)}

    def show_all_diskgroup(self):
        list_header = ["DiskgroupName", "DiskName"]
        dict_data = self.get_all_diskgroup()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def show_spe_diskgroup(self, dg):
        list_header = ["DiskgroupName", "DiskName"]
        dict_data = self.get_spe_diskgroup(dg)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def delete_diskgroup(self, dg):
        if self.js.check_key('DiskGroup', dg)['result']:
            if self.js.check_value('Map', dg)['result']:
                s.prt_log("Fail! The diskgroup already map,Please delete the map", 1)
            else:
                self.js.delete_data('DiskGroup', dg)
                s.prt_log("Delete success!", 0)
        else:
            s.prt_log(f"Fail! Can't find {dg}", 1)


    def verf_add_disk(self,dg,list_disk):
        for disk in list_disk:
            if self.js.check_value_in_key("DiskGroup", dg, disk)['result']:
                s.prt_log(f'{disk}已存在{dg}中',2)
            if not self.js.check_key("Disk", disk)['result']:
                s.prt_log(f'json文件中不存在{disk}，无法进行添加',2)


        list_map = self.js.get_map_by_group('DiskGroup', dg)
        print(f'在{dg}中添加新成员{",".join(list_disk)}会影响到已存在的map:{",".join(list_map)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改,退出',2)


    def add_disk(self,dg,list_disk):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.append_member('DiskGroup',dg,list_disk)
        obj_crm = CRMConfig()
        obj_map = Map()


        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                print(f'删除{disk}')
                obj_crm.delete_res(disk)
            elif not iqn_before:
                print(f'新建{disk}的iqn为{iqn_now}')
                path = self.js.get_data('Disk')[disk]
                obj_map.create_res(disk,path,iqn_now)
            else:
                print(f'修改{disk}的iqn为{iqn_now}')
                obj_crm.change_initiator(disk, iqn_now)


        self.js.append_member('DiskGroup',dg,list_disk)


    def verf_remove_disk(self,dg,list_disk):
        for disk in list_disk:
            if not self.js.check_value_in_key("DiskGroup", dg, disk)['result']:
                s.prt_log(f'{dg}中不存在成员{disk}，无法进行移除',2)

        list_map = self.js.get_map_by_group('DiskGroup', dg)
        print(f'从{dg}移除成员{",".join(list_disk)}会影响到已存在的map:{",".join(list_map)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)


    def remove_disk(self,dg,list_disk):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('DiskGroup', dg, list_disk)

        obj_crm = CRMConfig()
        obj_map = Map()

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                print(f'删除{disk}')
                obj_crm.delete_res(disk)
            elif not iqn_before:
                print(f'新建{disk}的iqn为{iqn_now}')
                path = self.js.get_data('Disk')[disk]
                obj_map.create_res(disk, path, iqn_now)
            else:
                print(f'修改{disk}的iqn为{iqn_now}')
                obj_crm.change_initiator(disk, iqn_now)

        # 配置文件移除成员
        self.js.remove_member('DiskGroup', dg, list_disk)


    """
    hostgroup 操作
    """


class HostGroup():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()

    def create_hostgroup(self, hostgroup, host):
        if self.js.check_key('HostGroup', hostgroup)['result']:
            s.prt_log(f'Fail! The HostGroup {hostgroup} already existed.', 1)
        else:
            for i in host:
                if self.js.check_key('Host', i)['result'] == False:
                    s.prt_log(f"Fail! Can't find {i}.Please give the true name.", 1)
                    return

            self.js.add_data('HostGroup', hostgroup, host)
            s.prt_log("Create success!", 0)
            return True

    def get_all_hostgroup(self):
        return self.js.get_data("HostGroup")

    def get_spe_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg)['result']:
            return {hg: self.js.get_data('HostGroup').get(hg)}

    def show_all_hostgroup(self):
        list_header = ["HostGroupName", "HostName"]
        dict_data = self.get_all_hostgroup()
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def show_spe_hostgroup(self, hg):
        list_header = ["HostGroupName", "HostName"]
        dict_data = self.get_spe_hostgroup(hg)
        table = s.show_iscsi_data(list_header, dict_data)
        s.prt_log(table, 0)

    def delete_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg)['result']:
            if self.js.check_value('Map', hg)['result']:
                s.prt_log("Fail! The hostgroup already map,Please delete the map", 1)
            else:
                self.js.delete_data('HostGroup', hg)
                s.prt_log("Delete success!", 0)
        else:
            s.prt_log(f"Fail! Can't find {hg}", 1)


    def verf_add_host(self, hg, list_host):
        for host in list_host:
            if self.js.check_value_in_key("HostGroup", hg, host)['result']:
                s.prt_log(f'{host}已存在{hg}中',2)
            if not self.js.check_key("Host", host)['result']:
                s.prt_log(f'json文件中不存在{host}，无法进行添加',2)

        list_disk = self.js.get_disk_by_hg(hg)
        print(f'在{hg}中添加{",".join(list_host)}会影响到已存在的res：{",".join(list_disk)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改,退出',2)

    def add_host(self, hg, list_host):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.append_member('HostGroup', hg, list_host)

        obj_crm = CRMConfig()

        list_disk = self.js.get_disk_by_host(list_host)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                print(f'删除{disk}')
                obj_crm.delete_res(disk)
            else:
                print(f'修改{disk}的iqn为{iqn_now}')
                obj_crm.change_initiator(disk, iqn_now)

        # 配置文件更新修改的资源
        self.js.append_member('HostGroup', hg, list_host)


    def verf_remove_host(self, hg ,list_host):
        for host in list_host:
            if not self.js.check_value_in_key("HostGroup", hg, host)['result']:
                s.prt_log(f'{hg}中不存在成员{host}，无法进行移除',2)

        # 交互提示：
        list_disk = self.js.get_disk_by_hg(hg) # 去重的列表

        print(f'在{hg}中移除{",".join(list_host)}会影响到已存在的res：{",".join(list_disk)}? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)

    def remove_host(self, hg, list_host):
        # 临时json对象进行数据的更新
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('HostGroup', hg, list_host)
        obj_crm = CRMConfig()

        # 获取所有受影响的disk
        list_disk = self.js.get_disk_by_host(list_host)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                obj_crm.delete_res(disk)
            else:
                obj_crm.change_initiator(disk,iqn_now)

        #配置文件移除成员，可以考虑修改为直接用js_modify.jsondata来替换
        self.js.remove_member('HostGroup', hg, list_host)


    """
    map操作
    """


class Map():
    def __init__(self):
        self.js = iscsi_json.JsonOperation()
        # 用于收集创建成功的resource
        self.list_res_created = []
        self.target_name, self.target_iqn = self.get_target()

    def pre_check_create_map(self, map, hg, dg):
        if self.js.check_key('Map', map)['result']:
            s.prt_log(f'The Map "{map}" already existed.', 1)
        elif self.checkout_exist('HostGroup', hg) == False:
            s.prt_log(f"Can't find {hg}", 1)
        elif self.checkout_exist('DiskGroup', dg) == False:
            s.prt_log(f"Can't find {dg}", 1)
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

    def create_map(self, map, hg_list, dg_list):
        """
        创建map
        :param map:
        :param hg: list,
        :param dg: list,
        :return:T/F
        """
        # 创建前的检查
        if not self.pre_check_create_map(map, hg_list, dg_list):
            return

        # 检查disk是否已map过
        # if self.check_dg_map(map, hg, dg):
        #     return True

        initiator = self.get_all_initiator(hg_list)
        disk_dict = self.get_all_disk(dg_list)
        obj_crm = CRMConfig()
        # 执行创建和启动
        for res in disk_dict:
            path = disk_dict[res]
            map_list = self.js.get_map_by_disk(res)
            if map_list == []:
                if self.create_res(res, path, initiator) == False:
                    return False
            else:
                s.prt_log(f"The {res} already map, change allowed_initiators...", 0)
                iqn_list_new = self.js.get_iqn_by_hg(hg_list)
                iqn_list = []
                for i in map_list:
                    iqn_list += self.js.get_iqn_by_map(i)
                list_iqn = s.append_list(iqn_list,iqn_list_new)
                obj_crm.change_initiator(res, list_iqn)

        self.js.add_data('Map', map, {'HostGroup': hg_list, 'DiskGroup': dg_list})
        s.prt_log('Create map success!', 0)
        return True

    def create_res(self, res, path, initiator):
        obj_crm = CRMConfig()
        # 取DeviceName后四位数字，减一千作为lun id
        lunid = int(path[-4:]) - 1000
        # 创建iSCSILogicalUnit
        if obj_crm.create_crm_res(res, self.target_iqn, lunid, path, initiator):
            self.list_res_created.append(res)
            # 创建order，colocation
            if obj_crm.create_set(res, self.target_name):
                # 尝试启动资源，成功失败都不影响创建
                s.prt_log(f"try to start {res}", 0)
                obj_crm.start_res(res)
                obj_crm.checkout_status_start(res)
            else:
                for i in self.list_res_created:
                    obj_crm.delete_res(i)
                return False
        else:
            s.prt_log('Fail to create iSCSILogicalUnit', 1)
            for i in self.list_res_created:
                obj_crm.delete_res(i)
            return False

    def get_all_map(self):
        return self.js.get_data("Map")

    def get_spe_map(self, map):
        list_hg = []
        list_dg = []
        if not self.js.check_key('Map', map)['result']:
            s.prt_log('No map data', 2)
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
        return [{map: map_data}, list_hg, list_dg]

    def show_all_map(self):
        list_header = ["MapName", "HostGroup", "DiskGroup"]
        dict_data = self.get_all_map()
        table = s.show_map_data(list_header, dict_data)
        s.prt_log(table, 0)

    def show_spe_map(self, map):
        list_data = self.get_spe_map(map)
        header_map = ["MapName", "HostGroup", "DiskGroup"]
        header_host = ["HostGroup", "HostName", "IQN"]
        header_disk = ["DiskGroup", "DiskName", "Disk"]
        table_map = s.show_map_data(header_map, list_data[0])
        table_hg = s.show_spe_map_data(header_host, list_data[1])
        table_dg = s.show_spe_map_data(header_disk, list_data[2])
        result = [str(table_map), str(table_hg), str(table_dg)]
        s.prt_log('\n'.join(result), 0)
        return list_data

    def pre_check_delete_map(self, map):
        if self.js.check_key('Map', map)['result']:
            return True
        else:
            s.prt(f"Fail! Can't find {map}", 1)

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
            s.prt_log("Could not perform requested operations, are you root?", 1)
        else:
            for disk in set(resname):
                map_list = self.js.get_map_by_disk(disk)
                if map_list == [map]:
                    if obj_crm.delete_res(disk) != True:
                        return False
                else:
                    map_list.remove(map)
                    iqn_list = []
                    for i in map_list:
                        iqn_list += self.js.get_iqn_by_map(i)
                    obj_crm.change_initiator(disk, iqn_list)
            self.js.delete_data('Map', map)
            s.prt_log("Delete map success!", 0)
            return True

    # 获取已map的dg对应的hg
    def get_hg_by_dg(self, dg):
        map = self.js.get_data('Map')
        hg_list = []
        for i in map.values():
            if dg in i:
                hg_list.append(i[0])
        return hg_list


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


    def verf_add_hg(self, map, list_hg):
        for hg in list_hg:
            if self.js.check_map_member(map, hg, "HostGroup"):
                s.prt_log(f'{hg}已存在{map}中',2)
            if not self.js.check_key("HostGroup", hg)['result']:
                s.prt_log(f'json文件中不存在{hg}，无法进行添加',2)

        print(f'确定修改{map}的hostgroup? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)

    def add_hg(self, map, list_hg):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.append_member('HostGroup', map, list_hg, type='Map')
        obj_crm = CRMConfig()

        # 获取所有受影响的disk
        list_disk = self.js.get_disk_by_hg(list_hg)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                obj_crm.delete_res(disk)
            elif not iqn_before:
                path = self.js.get_data('Disk')[disk]
                self.create_res(disk, path, iqn_now)
            else:
                obj_crm.change_initiator(disk, iqn_now)

        # 配置文件添加数据
        self.js.append_member('HostGroup', map, list_hg, type='Map')


    def verf_add_dg(self, map, list_dg):
        for dg in list_dg:
            if self.js.check_map_member(map, dg, "DiskGroup"):
                s.prt_log(f'{dg}已存在{map}中', 2)
            if not self.js.check_key("DiskGroup", dg)['result']:
                s.prt_log(f'json文件中不存在{dg}，无法进行添加', 2)

        print(f'确定修改{map}的hostgroup? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)


    def add_dg(self, map, list_dg):
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('DiskGroup', map, list_dg, type='Map')
        obj_crm = CRMConfig()

        # 获取所有受影响的disk
        list_disk = self.js.get_disk_by_dg(list_dg)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                obj_crm.delete_res(disk)
            elif not iqn_before:
                path = self.js.get_data('Disk')[disk]
                self.create_res(disk,path,iqn_now)
            else:
                obj_crm.change_initiator(disk,iqn_now)

        #配置文件移除成员，可以考虑修改为直接用js_modify.jsondata来替换
        self.js.remove_member('DiskGroup', map, list_dg, type='Map')


    def verf_remove_hg(self, map, list_hg):
        for hg in list_hg:
            if not self.js.check_map_member(map, hg, "HostGroup"):
                s.prt_log(f'{map}中不存在成员{hg}，无法进行移除',2)

        print(f'确定修改{map}的hostgroup? yes/no')
        answer = input()
        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)

    def remove_hg(self, map, list_hg):
        # 临时json对象进行数据的更新
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('HostGroup', map, list_hg, type='Map')
        obj_crm = CRMConfig()

        # 获取所有受影响的disk
        list_disk = self.js.get_disk_by_hg(list_hg)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                obj_crm.delete_res(disk)
            else:
                obj_crm.change_initiator(disk, iqn_now)

        # 配置文件移除成员
        self.js.remove_member('HostGroup', map, list_hg, type='Map')



    def verf_remove_dg(self,map,list_dg):
        for dg in list_dg:
            if not self.js.check_map_member(map, dg, "DiskGroup"):
                s.prt_log(f'{map}中不存在成员{dg}，无法进行移除',2)

        print(f'确定修改{map}的diskgroup? yes/no')
        answer = input()
        #[2020/11/25 13:35:47] [1606282545] [root] [DATA] [INPUT] [confirm_input] [confirm deletion] [n]|

        if not answer in ['y', 'yes', 'Y', 'YES']:
            s.prt_log('取消修改，退出',2)


    def remove_dg(self, map, list_dg):
        # 临时json对象进行数据的更新
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('DiskGroup', map, list_dg, type='Map')
        obj_crm = CRMConfig()

        # 获取所有受影响的disk
        list_disk = self.js.get_disk_by_dg(list_dg)

        # 固定的一套流程，获取disk的旧iqn，和获取新的iqn，进行比较和处理
        for disk in list_disk:
            iqn_before = self.js.get_res_initiator(disk)
            iqn_now = js_modify.get_res_initiator(disk)
            if iqn_now == iqn_before:
                continue
            elif not iqn_now:
                obj_crm.delete_res(disk)
            else:
                obj_crm.change_initiator(disk,iqn_now)

        #配置文件移除成员，可以考虑修改为直接用js_modify.jsondata来替换
        self.js.remove_member('DiskGroup', map, list_dg, type='Map')
