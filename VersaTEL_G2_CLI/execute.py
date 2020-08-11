# coding=utf-8
import re
import subprocess
import time
import iscsi_json
import consts
import sundry as s
import sys


def execute_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    output = p.stdout.read().decode()
    return output


def execute_crm_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    out, err = p.communicate()
    if len(out) > 0:
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output
    if len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
        return output
    if out == b'':  # 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output


# def get_cmd(ssh_obj, unique_str, cmd, oprt_id):
#     logger = consts.get_glo_log()
#     global RPL
#     RPL = 'no'
#     if RPL == 'no':
#         logger.write_to_log('F', 'DATA', 'STR', unique_str, '', oprt_id)
#         logger.write_to_log('T', 'OPRT', 'cmd', 'ssh', oprt_id, cmd)
#         result_cmd = ssh_obj.execute_command(cmd)
#         logger.write_to_log('F', 'DATA', 'cmd', 'ssh', oprt_id, result_cmd)
#         return result_cmd
#     elif RPL == 'yes':
#         pass


class TimeoutError(Exception):
    pass


class CRMData():
    def __init__(self):
        self.crm_conf_data = self.get_crm_conf()

    def get_crm_conf(self):
        cmd = 'crm configure show'
        result = execute_crm_cmd(cmd)
        print("do crm configure show")
        if result:
            return result['rst']

    def get_resource_data(self):
        re_logical = re.compile(
            r'primitive (\w*) iSCSILogicalUnit \\\s\tparams\starget_iqn="([a-zA-Z0-9.:-]*)"\simplementation=lio-t\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators="([a-zA-Z0-9.: -]+)"[\s\S.]*?meta target-role=(\w*)')
        result = s.re_findall(re_logical, self.crm_conf_data)
        return result

    def get_vip_data(self):
        re_vip = re.compile(
            r'primitive\s(\w*)\sIPaddr2\s\\\s*\w*\sip=([0-9.]*)\s\w*=(\d*)\s')
        result = s.re_findall(re_vip, self.crm_conf_data)
        return result

    def get_target_data(self):
        re_target = re.compile(
            r'primitive\s(\w*)\s\w*\s\\\s*params\siqn="([a-zA-Z0-9.:-]*)"\s[a-z=-]*\sportals="([0-9.]*):\d*"\s\\')
        result = s.re_findall(re_target, self.crm_conf_data)
        return result

    # 获取并更新crm信息
    def update_crm_conf(self):
        # crm_config_status = obj_crm.get_crm_data()
        if 'ERROR' in self.crm_conf_data:
            print("Could not perform requested operations, are you root?")
        else:
            js = iscsi_json.JSON_OPERATION()
            res = self.get_resource_data()
            print(res)
            vip = self.get_vip_data()
            target = self.get_target_data()
            js.update_crm_conf(res, vip, target)
            return True


class CRMConfig():
    def __init__(self):
        self.logger = consts.glo_log()

    def create_crm_res(self, res, target_iqn, lunid, path, initiator):
        cmd = f'crm conf primitive {res} iSCSILogicalUnit params ' \
            f'target_iqn="{target_iqn}" ' \
            f'implementation=lio-t ' \
            f'lun={lunid} ' \
            f'path={path} ' \
            f'allowed_initiators="{initiator}" ' \
            f'op start timeout=40 interval=0 ' \
            f'op stop timeout=40 interval=0 ' \
            f'op monitor timeout=40 interval=15 ' \
            f'meta target-role=Stopped'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            print("Create iSCSILogicalUnit success")
            return True

    # 获取res的状态
    def get_res_status(self, res):
        crm_data = CRMData()
        resource_data = crm_data.get_resource_data()
        for s in resource_data:
            if s[0] == res:
                return s[-1]

    # 停用res
    def stop_res(self, res):
        cmd = f'crm res stop {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            print("crm res stop fail")


    # 检查
    def checkout_status(self, res, times, expect_value):
        """
        检查res的状态
        :param res: 需要检查的资源
        :param num: 需要检查的次数
        :param expect_value: 预期值
        :return: 返回True则说明是预期效果
        """
        n = 0
        while n < times:
            n += 1
            if self.get_res_status(res) == expect_value:
                return True
            else:
                time.sleep(1)
        else:
            print("Does not meet expectations, please try again.")

    def delete_crm_res(self, res):
        # crm res stop <LUN_NAME>
        if self.stop_res(res):
            if self.checkout_status(res,10,'Stopped'):
                time.sleep(3)
                # crm conf del <LUN_NAME>
                cmd = f'crm conf del {res}'
                # 使用execute_crm_cmd执行成功，stderr也可能会有输出，导致判断不正确
                result = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result == 0:
                    print("crm conf del " + res)
                    return True
                else:
                    print("crm delete fail")

    def create_col(self, res, target):
        # crm conf colocation <COLOCATION_NAME> inf: <LUN_NAME> <TARGET_NAME>
        print(f'crm conf colocation co_{res} inf: {res} {target}')
        cmd = f'crm conf colocation co_{res} inf: {res} {target}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            print("set coclocation")
            return True

    def create_order(self, res, target):
        # crm conf order <ORDER_NAME1> <TARGET_NAME> <LUN_NAME>
        print(f'crm conf order or_{res} {target} {res}')
        cmd = f'crm conf order or_{res} {target} {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            print("set order")
            return True

    def start_res(self, res):
        # crm res start <LUN_NAME>
        print(f'crm res start {res}')
        cmd = f'crm res start {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True



class LVM():
    def __init__(self):
        self.logger = consts.glo_log()
        self.data_vg = self.get_vg()
        self.data_lv = self.get_thinlv()

    def get_vg(self):
        cmd = 'vgs'
        result = execute_cmd(cmd)
        return result

    def get_thinlv(self):
        cmd = 'lvs'
        result = execute_cmd(cmd)
        return result

    def refine_thinlv(self):
        all_lv = self.data_vg.splitlines()
        list_thinlv = []
        re_ = re.compile(
            r'\s*(\S*)\s*(\S*)\s*\S*\s*(\S*)\s*\S*\s*\S*\s*\S*\s*?')
        for one in all_lv:
            if 'twi' in one:
                thinlv_one = re_.findall(one)
                list_thinlv.append(list(thinlv_one[0]))
        return list_thinlv

    def refine_vg(self):
        all_vg = self.data_lv.splitlines()
        list_vg = []
        re_ = re.compile(
            r'\s*(\S*)\s*\S*\s*\S*\s*\S*\s*\S*\s*(\S*)\s*(\S*)\s*?')
        for one in all_vg[1:]:
            vg_one = re_.findall(one)
            list_vg.append(list(vg_one[0]))
        return list_vg

    def is_vg_exists(self,vg):
        if vg in self.data_vg:
            return True

    def is_thinlv_exists(self,thinlv):
        all_lv_list = self.data_lv.splitlines()[1:]
        for one in all_lv_list:
            if 'twi' and thinlv in one:
                return True



class Linstor():
    def __init__(self):
        self.logger = consts.glo_log()

    def refine_linstor(self,data):
        reSeparate = re.compile(r'(.*?\s\|)')
        list_table = data.split('\n')
        list_data_all = []

        def _clear_symbol(list_data):
            for i in range(len(list_data)):
                list_data[i] = list_data[i].replace(' ', '')
                list_data[i] = list_data[i].replace('|', '')

        for i in range(len(list_table)):
            if list_table[i].startswith('|') and '=' not in list_table[i]:
                valid_data = reSeparate.findall(list_table[i])
                _clear_symbol(valid_data)
                list_data_all.append(valid_data)

        try:
            list_data_all.pop(0)
        except IndexError:
            print('The data cannot be read, please check whether LINSTOR is normal.')
        return list_data_all

    def get_linstor_data(self,cmd):
        cmd_result = execute_cmd(cmd)
        return self.refine_linstor(cmd_result)





# 子命令stor调用的方法
class Stor():

    def __init__(self):
        self.logger = consts.glo_log()

    def judge_result(self,result):
        # 对命令进行结果根据正则匹配进行分类
        re_suc = re.compile('SUCCESS')
        re_war = re.compile('WARNING')
        re_err = re.compile('ERROR')

        """
        suc : 0
        suc with war : 1
        war : 2
        err : 3
        """

        if re_err.search(result):
            return {'sts':3,'rst':result}
        elif re_suc.search(result) and re_war.search(result):
            messege_war = Stor.get_war_mes(result.decode())
            return {'sts':1,'rst':messege_war}
        elif re_suc.search(result):
            return {'sts':0,'rst:':result}
        elif re_war.search(result):
            messege_war = Stor.get_war_mes(result.decode())
            return {'sts':2,'rst':messege_war}


    @staticmethod
    def get_err_detailes(result):
        re_ = re.compile(r'Description:\n[\t\s]*(.*)\n')
        if re_.search(result):
            return (re_.search(result).group(1))

    @staticmethod
    def get_war_mes(result):
        re_ = re.compile(r'\x1b\[1;33mWARNING:\n\x1b(?:.*\s*)+\n$')
        if re_.search(result):
            return (re_.search(result).group())

    # 创建storagepool
    def create_storagepool_lvm(self, node, stp, vg):
        obj_lvm = LVM()
        if vg not in obj_lvm.data_vg:
            print(f'Volume group:"{vg}" does not exist')
            return
        cmd = f'linstor storage-pool create lvm {node} {stp} {vg}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    def create_storagepool_thinlv(self, node, stp, tlv):
        obj_lvm = LVM()
        all_lv_list = obj_lvm.data_lv.splitlines()[1:]
        for one in all_lv_list:
            if 'twi' and tlv not in one:
                print(f'Thin logical volume:"{tlv}" does not exist')
                return
        cmd = f'linstor storage-pool create lvmthin {node} {stp} {tlv}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    # 删除storagepool -- ok
    def delete_storagepool(self, node, stp):
        cmd = f'linstor storage-pool delete {node} {stp}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    # 创建集群节点
    def create_node(self, node, ip, nt):
        cmd = f'linstor node create {node} {ip}  --node-type {nt}'
        nt_value = [
            'Combined',
            'combined',
            'Controller',
            'Auxiliary',
            'Satellite']
        if nt not in nt_value:
            print('node type error,choose from ''Combined',
                  'Controller', 'Auxiliary', 'Satellite''')
        else:
            output = execute_cmd(cmd)
            result = self.judge_result(output)
            if result:
                if result['sts'] == 0:
                    print('SUCCESS')
                elif result['sts'] == 1:
                    print('SUCCESS')
                    print(result['rst'])
                else:
                    print('FAIL')
                    print(result['rst'])

    # 删除node
    def delete_node(self, node):
        cmd = f'linstor node delete {node}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])


class LinstorResource(Stor):
    def __init__(self):
        Stor.__init__(self)

    def collect_args(self,node,sp):
        dict_args = {}
        if len(sp) == 1:
            for node_one in node:
                dict_args.update({node_one:sp[0]})
        else:
            for node_one,sp_one in zip(node,sp):
                dict_args.update({node_one:sp_one})
        return dict_args


    def execute_create_res(self,res,node,sp):
        # 执行在指定节点和存储池上创建resource
        # 成功返回空字典，失败返回 {节点：错误原因}
        cmd = f'linstor resource create {node} {res} --storage-pool {sp}'
        try:
            output = execute_cmd(cmd)
            result = self.judge_result(output)
            if result:
                if result['sts'] == 2:
                    print(Stor.get_war_mes(result))
                if result['sts'] == 0:
                    print(f'Resource {res} was successfully created on Node {node}')
                    return {}
                elif result['sts'] == 1:
                    print(f'Resource {res} was successfully created on Node {node}')
                    return {}
                elif result['sts'] == 3:
                    fail_cause = Stor.get_err_detailes(result)
                    dict_fail = {node: fail_cause}
                    return dict_fail

        except TimeoutError:
            result = f'{res} created timeout on node {node}, the operation has been cancelled'
            print(result)
            return {node:'Execution creation timeout'}


    # 创建resource相关
    def linstor_delete_rd(self, res):
        cmd = f'linstor rd d {res}'
        execute_cmd(cmd)

    def linstor_create_rd(self, res):
        cmd_rd = f'linstor rd c {res}'
        output = execute_cmd(cmd_rd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                return True
            else:
                print('FAIL')
                return result

    def linstor_create_vd(self, res, size):
        cmd_vd = f'linstor vd c {res} {size}'
        output = execute_cmd(cmd_vd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                return True
            else:
                print('FAIL')
                self.linstor_delete_rd(res)
                return result


    # 创建resource 自动
    def create_res_auto(self, res, size, num):
        cmd = f'linstor r c {res} --auto-place {num}'
        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            output = execute_cmd(cmd)
            result = self.judge_result(output)
            if result:
                if result['sts'] == 0:
                    print('SUCCESS')
                    return True
                else:
                    print(output)
                    print('FAIL')
                    self.linstor_delete_rd(res)
                    return result
        else:
            print('The resource already exists')
            return ('The resource already exists')


    def create_res_manual(self, res, size, node, sp):
        dict_all_fail = {}
        dict_args = self.collect_args(node,sp)

        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            pass
        else:
            print('The resource already exists')
            return ('The resource already exists')

        for node_one,sp_one in dict_args.items():
            dict_one_result = self.execute_create_res(res,node_one,sp_one)
            dict_all_fail.update(dict_one_result)

        if len(dict_all_fail.keys()) == len(node):
            self.linstor_delete_rd(res)
        if len(dict_all_fail.keys()):
            print('Creation failure on', *dict_all_fail.keys(), sep=' ')
            for node, cause in dict_all_fail.items():
                print(node, ':', cause)
            return dict_all_fail
        else:
            return True

    # 添加mirror（自动）
    def add_mirror_auto(self, res, num):
        cmd = f'linstor r c {res} --auto-place {num}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    def add_mirror_manual(self, res, node, sp):
        dict_all_fail = {}
        dict_args = self.collect_args(node,sp)

        for node_one,sp_one in dict_args.items():
            dict_one_result = self.execute_create_res(res,node_one,sp_one)
            dict_all_fail.update(dict_one_result)

        if len(dict_all_fail.keys()):
            print('Creation failure on', *dict_all_fail.keys(), sep=' ')
            return dict_all_fail
        else:
            return True

    # 创建resource --diskless
    def create_res_diskless(self, node, res):
        cmd = f'linstor r c {node} {res} --diskless'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    # 删除resource,指定节点
    def delete_resource_des(self, node, res):
        cmd = f'linstor resource delete {node} {res}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])

    # 删除resource，全部节点
    def delete_resource_all(self, res):
        cmd = f'linstor resource-definition delete {res}'
        output = execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                print('SUCCESS')
            elif result['sts'] == 1:
                print('SUCCESS')
                print(result['rst'])
            else:
                print('FAIL')
                print(result['rst'])


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
        list_header = ["Resource Name", "Path"]
        dict_data = self.get_all_disk()
        return s.show_data(list_header,dict_data)

    # 展示指定的disk
    def show_spe_disk(self, disk):
        list_header = ["Resource Name", "Path"]
        dict_data = self.get_spe_disk(disk)
        return s.show_data(list_header,dict_data)

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
        list_header = ["Host Name", "IQN"]
        dict_data = self.get_all_host()
        return s.show_data(list_header, dict_data)

    def show_spe_host(self, host):
        list_header = ["Host Name", "IQN"]
        dict_data = self.get_spe_host(host)
        return s.show_data(list_header, dict_data)

    def delete_host(self, host):
        print(f"Delete the host <{host}> ...")
        if self.js.check_key('Host', host):
            if self.js.check_value('HostGroup', host):
                print(
                    "Fail! The host in ... hostgroup, Please delete the hostgroup first.")
            else:
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
        print("All Disk Group:")
        list_header = ["Diskgroup Name", "Disk Name"]
        dict_data = self.get_all_diskgroup()
        return s.show_data(list_header, dict_data)

    def show_spe_diskgroup(self,dg):
        list_header = ["Diskgroup Name", "Disk Name"]
        dict_data = self.get_spe_diskgroup(dg)
        return s.show_data(list_header, dict_data)


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
        list_header = ["Host Group Name", "Host Name"]
        dict_data = self.get_all_hostgroup()
        return s.show_data(list_header, dict_data)

    def show_spe_hostgroup(self,hg):
        list_header = ["Host Group Name", "Host Name"]
        dict_data = self.get_spe_hostgroup(hg)
        return s.show_data(list_header, dict_data)


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
        list_header = ["Map Name", "Host Group And Disk Group"]
        dict_data = self.get_all_map()
        return s.show_data(list_header, dict_data)


    def show_spe_map(self, map):
        list_data = self.get_spe_map(map)
        hg, dg = self.js.get_data('Map').get(map)
        header_map = ["Map Name", "Host Group And Disk Group"]
        header_host = ["Host Name", "IQN"]
        header_disk = ["Disk Name", "Disk"]
        print(f'Map:{map}')
        s.show_data(header_map, list_data[0])
        print(f'Host Group:{hg}')
        s.show_data(header_host, list_data[1])
        print(f'Disk Group:{dg}')
        s.show_data(header_disk, list_data[2])
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

