# coding=utf-8
import iscsi_json
import consts
import sundry as s
from execute.linstor import Linstor
from execute.crm import CRMData,CRMConfig

class Iscsi():
    def __init__(self):
        self.logger = consts.glo_log()
        self.js = iscsi_json.JSON_OPERATION()

    """
    disk 操作
    """

    def get_all_disk(self):
        linstor = Linstor()
        linstor_res = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        disks = {}
        for d in linstor_res:
            disks.update({d[1]: d[5]})
        self.js.update_data('Disk', disks)
        return disks

    def get_spe_disk(self,disk):
        if self.js.check_key('Disk', disk):
            return {disk: self.js.get_data('Disk').get(disk)}

    # 展示全部disk
    def show_all_disk(self):
        print("All Disk:")
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

    def create_host(self, host, iqn):
        print("Host name:", host)
        print("iqn:", iqn)
        if self.js.check_key('Host', host):
            print(f"Fail! The Host {host} already existed.")
        else:
            self.js.add_data("Host", host, iqn)
            print("Create success!")
            return True

    def get_all_host(self):
        return self.js.get_data("Host")


    def get_spe_host(self,host):
        if self.js.check_key('Host', host):
            return ({host:self.js.get_data('Host').get(host)})

    def show_all_host(self):
        print("All Host:")
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
        print(f"Delete the host <{host}> ...")
        if self.js.check_key('Host', host):
            if self.js.check_value('HostGroup', host):
                print(
                    "Fail! The host in ... hostgroup, Please delete the hostgroup first.")
            else:
                print('2222')
                self.js.delete_data('Host', host)
                print("Delete success!")
                return True
        else:
            print(f"Fail! Can't find {host}")

    """
    diskgroup 操作
    """

    def create_diskgroup(self, diskgroup, disk):
        if self.js.check_key('DiskGroup', diskgroup):
            print(f'Fail! The Disk Group {diskgroup} already existed.')
        else:
            t = True
            for i in disk:
                if self.js.check_key('Disk', i) == False:
                    t = False
                    print(f"Fail! Can't find {i}")
            if t:
                self.js.add_data('DiskGroup', diskgroup, disk)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")


    def get_all_diskgroup(self):
        return self.js.get_data("DiskGroup")

    def get_spe_diskgroup(self,dg):
        if self.js.check_key('DiskGroup', dg):
            return {dg:self.js.get_data('DiskGroup').get(dg)}

    def show_all_diskgroup(self):
        print("All disk group:")
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
        print("Delete the diskgroup <", dg, "> ...")
        if self.js.check_key('DiskGroup', dg):
            if self.js.check_value('Map', dg):
                print("Fail! The diskgroup already map,Please delete the map")
            else:
                self.js.delete_data('DiskGroup', dg)
                print("Delete success!")
        else:
            print(f"Fail! Can't find {dg}")

    """
    hostgroup 操作
    """

    def create_hostgroup(self, hostgroup, host):
        print("Hostgroup name:", hostgroup)
        print("Host name:", host)
        if self.js.check_key('HostGroup', hostgroup):
            print(f'Fail! The HostGroup {hostgroup} already existed.')
        else:
            t = True
            for i in host:
                if self.js.check_key('Host', i) == False:
                    t = False
                    print(f"Fail! Can't find {i}")
            if t:
                self.js.add_data('HostGroup', hostgroup, host)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")

    def get_all_hostgroup(self):
        return self.js.get_data("HostGroup")

    def get_spe_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg):
            return {hg:self.js.get_data('HostGroup').get(hg)}

    def show_all_hostgroup(self):
        print("All Host Group:")
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
        print("Delete the hostgroup <", hg, "> ...")
        if self.js.check_key('HostGroup', hg):
            if self.js.check_value('Map', hg):
                print("Fail! The hostgroup already map,Please delete the map")
            else:
                self.js.delete_data('HostGroup', hg)
                print("Delete success!")
        else:
            print("Fail! Can't find " + hg)

    """
    map操作
    """

    def pre_check_create_map(self, map, hg, dg):
        print("Map name:", map)
        print("Hostgroup name:", hg)
        print("Diskgroup name:", dg)

        if self.js.check_key('Map', map):
            print(f'The Map "{map}" already existed.')
        elif self.js.check_key('HostGroup', hg) == False:
            print(f"Can't find {hg}")
        elif self.js.check_key('DiskGroup', dg) == False:
            print(f"Can't find {dg}")
        else:
            if self.js.check_value('Map', dg):
                print("The diskgroup already map")
            else:
                if self.create_map(hg, dg):
                    self.js.add_data('Map', map, [hg, dg])
                    print('Create success!')
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
            crm_data_dict = self.js.get_data('crm')
            target_all = crm_data_dict['target'][0] # 目前的设计只有一个target，所以取列表的第一个
            return target_all[0], target_all[1]  # 返回target_name, target_iqn

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

    def create_map(self, hg, dg):
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
                    print(f'create colocation and order success:{res}')
                    obj_crm.start_res(res)
                else:
                    print("create colocation and order fail")
            else:
                print('create resource Fail!')
        return True


    def get_all_map(self):
        return self.js.get_data("Map")

    def get_spe_map(self,map):
        dict_hg = {}
        dict_dg = {}
        if not self.js.check_key('Map', map):
            print('no data')
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
        print("All Map:")
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
        result = [f'Map:{map}',table_map,f'Host Group:{hg}',table_hg,f'Disk Group:{dg}',table_dg]
        s.prt_log('\n'.join(result),0)
        return list_data


    def pre_check_delete_map(self, map):
        print("Delete the map <", map, ">...")
        if self.js.check_key('Map', map):
            print(f"{self.js.get_data('Map').get(map)} probably be affected")
            dg = self.js.get_data('Map').get(map)[1]
            resname = self.js.get_data('DiskGroup').get(dg)
            if self.delete_map(resname):
                self.js.delete_data('Map', map)
                print("Delete success!")
        else:
            print("Fail! Can't find " + map)

    # 调用crm删除map
    def delete_map(self, resname):
        obj_crm = CRMConfig()
        crm_data = CRMData()
        crm_config_statu = crm_data.crm_conf_data
        if 'ERROR' in crm_config_statu:
            print("Could not perform requested operations, are you root?")
        else:
            for disk in resname:
                if obj_crm.delete_crm_res(disk):
                    print("delete ", disk)
                else:
                    return False
            return True
