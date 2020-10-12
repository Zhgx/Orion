# coding=utf-8
import iscsi_json
import sundry as s
from execute.linstor import Linstor
from execute.crm import CRMData,CRMConfig


class Disk():
    def __init__(self):
        self.js = iscsi_json.JSON_OPERATION()

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
        self.js = iscsi_json.JSON_OPERATION()

    def create_host(self, host, iqn):
        if self.js.check_key('Host', host)['result']:
            s.prt_log(f"Fail! The Host {host} already existed.",1)
        else:
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
                s.prt_log("Dexlete success!",0)
                return True
        else:
            s.prt_log(f"Fail! Can't find {host}",1)

    """
    diskgroup 操作
    """

class DiskGroup():
    def __init__(self):
        self.js = iscsi_json.JSON_OPERATION()

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
        self.js = iscsi_json.JSON_OPERATION()

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

    """
    map操作
    """

class Map():
    def __init__(self):
        self.js = iscsi_json.JSON_OPERATION()


    def pre_check_create_map(self, map, hg, dg):
        if self.js.check_key('Map', map)['result']:
            s.prt_log(f'The Map "{map}" already existed.',1)
        elif self.js.check_key('HostGroup', hg)['result'] == False:
            s.prt_log(f"Can't find {hg}",1)
        elif self.js.check_key('DiskGroup', dg)['result'] == False:
            s.prt_log(f"Can't find {dg}",1)
        else:
            if self.js.check_value('Map', dg)['result']:
                s.prt_log("The diskgroup already map",1)
            else:
                return True

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
            js = iscsi_json.JSON_OPERATION()
            crm_data_dict = js.get_data('crm')
            if crm_data_dict['target']:
                # 目前的设计只有一个target，所以取列表的第一个
                target_all = crm_data_dict['target'][0]
                # 返回target_name, target_iqn
                return target_all[0], target_all[1]
            else:
                s.prt_log('没有target，创建map失败', 2)

    def get_drbd_data(self, dg):
        # 根据dg去收集drbdd的三项数据：resource name，minor number，device name
        disk_all = self.js.get_data('DiskGroup').get(dg)
        linstor = Linstor()
        linstorlv = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        drdb_list = []
        for res in linstorlv:
            for disk_one in disk_all:
                if disk_one in res:
                    drdb_list.append([res[1], res[4], res[5]])  # 取Resource,MinorNr,DeviceName
        return drdb_list

    def create_map(self, map,hg, dg):
        # 创建前的检查
        if not self.pre_check_create_map(map,hg,dg):
            return

        obj_crm = CRMConfig()
        initiator = self.get_initiator(hg)
        target_name, target_iqn = self.get_target()
        drdb_list = self.get_drbd_data(dg)

        # 执行创建和启动
        for i in drdb_list:
            res, minor_nr, path = i
            lunid = minor_nr[-2:]  # lun id 取自MinorNr的后两位数字
            if obj_crm.create_crm_res(res, target_iqn, lunid, path, initiator):
                c = obj_crm.create_col(res, target_name)
                o = obj_crm.create_order(res, target_name)
                if c and o:
                    s.prt_log(f'create colocation and order success:{res}',0)
                    obj_crm.start_res(res)
                else:
                    s.prt_log("create colocation and order fail",1)
                    return False
            else:
                s.prt_log('Failde to create resource!',1)
                return False

        self.js.add_data('Map', map, [hg, dg])
        s.prt_log('Create success!', 0)
        return True

    def get_all_map(self):
        return self.js.get_data("Map")

    def get_spe_map(self,map):
        dict_hg = {}
        dict_dg = {}
        if not self.js.check_key('Map', map)['result']:
            s.prt_log('No map data',1)
            return

        hg,dg = self.js.get_data('Map').get(map)
        host = self.js.get_data('HostGroup').get(hg)
        disk = self.js.get_data('DiskGroup').get(dg)

        for i in host:
            iqn = self.js.get_data('Host').get(i)
            dict_hg.update({i:iqn})
        for i in disk:
            path = self.js.get_data('Disk').get(i)
            dict_dg.update({i:path})
        return [{map:[hg,dg]},dict_dg,dict_hg]


    def show_all_map(self):
        list_header = ["MapName", "HostGroup","DiskGroup"]
        dict_data = self.get_all_map()
        table = s.show_map_data(list_header,dict_data)
        s.prt_log(table,0)


    def show_spe_map(self, map):
        list_data = self.get_spe_map(map)
        hg, dg = self.js.get_data('Map').get(map)
        header_map = ["MapName", "HostGroup","DiskGroup"]
        header_host = ["HostName", "IQN"]
        header_disk = ["DiskName", "Disk"]
        table_map = s.show_map_data(header_map, list_data[0])
        table_hg = s.show_iscsi_data(header_host, list_data[1])
        table_dg = s.show_iscsi_data(header_disk, list_data[2])
        result = [f'Map:{map}',str(table_map),f'Host Group:{hg}',str(table_hg),f'Disk Group:{dg}',str(table_dg)]
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
        dg = self.js.get_data('Map').get(map)[1]
        resname = self.js.get_data('DiskGroup').get(dg)

        if 'ERROR' in crm_config_statu:
            s.prt_log("Could not perform requested operations, are you root?",1)
        else:
            for disk in resname:
                if obj_crm.delete_crm_res(disk):
                    s.prt_log(f"delete {disk}",0)
                else:
                    return False
            self.js.delete_data('Map', map)
            s.prt_log("Delete success!", 0)
            return True
