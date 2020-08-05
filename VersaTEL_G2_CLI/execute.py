# coding=utf-8
import re
import subprocess
import time
import iscsi_json
import consts
import sundry as s


def execute_linstor_cmd(cmd, timeout=60):
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
            r'primitive\s(\w*)\s\w*\s\\\s*\w*\starget_iqn="([a-zA-Z0-9.:-]*)"\s[a-z=-]*\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators="([a-zA-Z0-9.: -]+)"(?:.*\s*){2}meta target-role=(\w*)')
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

    # 获取并更新crm信息, 这部分不需要
    def update_crm_conf(self):
        # crm_config_status = obj_crm.get_crm_data()
        if 'ERROR' in self.crm_conf_data:
            print("Could not perform requested operations, are you root?")
        else:
            js = iscsi_json.JSON_OPERATION()
            res = self.get_resource_data()
            vip = self.get_vip_data()
            target = self.get_target_data()
            # redata = obj_crm.re_crm_data(crm_config_status)
            js.update_crm_conf(res, vip, target)
            return True


class CRM():
    def __init__(self):
        self.logger = consts.get_glo_log()

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
        self.logger = consts.get_glo_log()

    def get_vg(self):
        cmd = 'vgs'
        result = execute_crm_cmd(cmd)
        if result:
            return result['rst']

    def get_thinlv(self):
        cmd = 'lvs'
        result = execute_crm_cmd(cmd)
        if result:
            return result['rst']

    def refine_thinlv(self, str):
        all_lv = str.splitlines()
        list_thinlv = []
        re_ = re.compile(
            r'\s*(\S*)\s*(\S*)\s*\S*\s*(\S*)\s*\S*\s*\S*\s*\S*\s*?')
        for one in all_lv:
            if 'twi' in one:
                thinlv_one = re_.findall(one)
                list_thinlv.append(list(thinlv_one[0]))
        return list_thinlv

    def refine_vg(self, str):
        all_vg = str.splitlines()
        list_vg = []
        re_ = re.compile(
            r'\s*(\S*)\s*\S*\s*\S*\s*\S*\s*\S*\s*(\S*)\s*(\S*)\s*?')
        for one in all_vg[1:]:
            vg_one = re_.findall(one)
            list_vg.append(list(vg_one[0]))
        return list_vg


class Linstor():
    def __init__(self):
        self.logger = consts.get_glo_log()

    @staticmethod
    def refine_linstor(table_data):
        reSeparate = re.compile(r'(.*?\s\|)')
        list_table = table_data.split('\n')
        list_data_all = []

        def clear_symbol(list_data):
            for i in range(len(list_data)):
                list_data[i] = list_data[i].replace(' ', '')
                list_data[i] = list_data[i].replace('|', '')

        for i in range(len(list_table)):
            if list_table[i].startswith('|') and '=' not in list_table[i]:
                valid_data = reSeparate.findall(list_table[i])
                clear_symbol(valid_data)
                list_data_all.append(valid_data)
        try:
            list_data_all.pop(0)
        except IndexError:
            print('The data cannot be read, please check whether LINSTOR is normal.')
        return list_data_all


# 子命令stor调用的方法
class Stor():

    def __init__(self):
        self.logger = consts.get_glo_log()

    def judge_result(self, result):
        # 判断结果，对应进行返回
        jug_result = Stor.re_sort(result)
        if jug_result == 'war':
            messege_war = Stor.get_war_mes(result.decode())
            # print(messege_war)
        if jug_result == 'suc':
            return True
        elif jug_result == 'err':
            return result
        else:
            return result

    @staticmethod
    def re_sort(result):
        # 对命令进行结果根据正则匹配进行分类
        re_suc = re.compile('SUCCESS')
        re_war = re.compile('WARNING')
        re_err = re.compile('ERROR')

        if re_err.search(result):
            return 'err'
        elif re_suc.search(result):
            return 'suc'
        elif re_war.search(result):
            return 'war'

    @staticmethod
    def judge_no_vg(result, node, vg):
        re_ = re.compile(
            r'\(Node: \'' +
            node +
            r'\'\) Volume group \'' +
            vg +
            '\' not found')
        if re_.search(result):
            return (re_.search(result).group())

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

    def print_execute_result(self, cmd):
        cmd_result = execute_linstor_cmd(cmd)
        result = self.judge_result(cmd_result)
        if not result:
            return
        if result is True:
            print('SUCCESS')
            return True
        else:
            print('FAIL')
            return result

    # 创建resource相关
    def linstor_delete_rd(self, res):
        cmd = 'linstor rd d %s' % res
        result = subprocess.check_output(cmd, shell=True)

    def linstor_delete_vd(self, res):
        cmd = 'linstor vd d %s' % res
        result = subprocess.check_output(cmd, shell=True)

    def linstor_create_rd(self, res):
        cmd_rd = 'linstor rd c %s' % res
        output = execute_linstor_cmd(cmd_rd)
        result = self.judge_result(output)
        if result is True:
            return True
        else:
            print('FAIL')
            return result

    def linstor_create_vd(self, res, size):
        cmd_vd = 'linstor vd c %s %s' % (res, size)
        output = execute_linstor_cmd(cmd_vd)
        result = self.judge_result(output)
        if result is True:
            return True
        else:
            print('FAIL')
            self.linstor_delete_rd(res)
            return result

    # 创建resource 自动
    def create_res_auto(self, res, size, num):
        cmd = 'linstor r c %s --auto-place %d' % (res, num)
        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            output = execute_linstor_cmd(cmd)
            result = self.judge_result(output)
            if result is True:
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
        dict_result = {}

        # Actions needed to create a resource
        def execute_(cmd):
            try:
                # Undo the decorator @result_cmd, and execute execute_cmd function
                # ex_cmd = self.execute_cmd.__wrapped__
                # result = ex_cmd(self, cmd)
                result = execute_linstor_cmd(cmd)
                jud_result = Stor.re_sort(str(result))
                if jud_result == 'war':
                    print(Stor.get_war_mes(result))
                if jud_result == 'suc':
                    result = ('Resource %s was successfully created on Node %s' % (res, node_one))
                    print(result)
                elif jud_result == 'err':
                    str_fail_cause = Stor.get_err_detailes(result)
                    dict_fail = {node_one: str_fail_cause}
                    dict_result.update(dict_fail)

            except TimeoutError as e:
                dict_result.update({node_one: 'Execution creation timeout'})
                result = '%s created timeout on node %s, the operation has been cancelled' % (res, node_one)
                print(result)

        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            pass
        else:
            # need to be prefect
            print('The resource already exists')
            return ('The resource already exists')

        if len(sp) == 1:
            for node_one in node:
                cmd = 'linstor resource create %s %s --storage-pool %s' % (node_one, res, sp[0])
                execute_(cmd)
            if len(dict_result.keys()) == len(node):
                self.linstor_delete_rd(res)
            if len(dict_result.keys()):
                print('Creation failure on', *dict_result.keys(), sep=' ')
                for node, cause in dict_result.items():
                    print(node, ':', cause)
                return dict_result
            else:
                return True

        # When sp is not one, it is equal to the number of nodes
        else:
            for node_one, sp_one in zip(node, sp):
                cmd = 'linstor resource create %s %s --storage-pool %s' % (node_one, res, sp_one)
                execute_(cmd)
            if len(dict_result.keys()) == len(node):
                self.linstor_delete_rd(res)
            # whether_delete_rd()
            if len(dict_result.keys()):
                print('Creation failure on', *dict_result.keys(), sep=' ')
                for node, cause in dict_result.items():
                    print(node, ':', cause)
                return dict_result
            else:
                return True
            # return print_fail_node()

    # 添加mirror（自动）
    def add_mirror_auto(self, res, num):
        cmd = 'linstor r c %s --auto-place %d' % (res, num)
        return self.print_execute_result(cmd)

    def add_mirror_manual(self, res, node, sp):
        dict_result = {}

        def execute_(cmd):
            try:
                # Undo the decorator @result_cmd, and execute execute_cmd function
                # ex_cmd = self.execute_cmd.__wrapped__
                # result = ex_cmd(self, cmd)
                result = execute_linstor_cmd(cmd)
                jud_result = Stor.re_sort(str(result))
                if jud_result == 'WAR':
                    print(Stor.get_war_mes(result))
                if jud_result == 'SUC':
                    result = ('Resource %s was successfully created on Node %s' % (res, node_one))
                    print(result)
                elif jud_result == 'ERR':
                    str_fail_cause = Stor.get_err_detailes(result)
                    dict_fail = {node_one: str_fail_cause}
                    dict_result.update(dict_fail)
            except TimeoutError as e:
                dict_result.update({node_one: 'Execution creation timeout'})
                print('%s created timeout on node %s, the operation has been cancelled' % (res, node_one))

        def print_fail_node():
            if len(dict_result.keys()):
                print('Creation failure on', *dict_result.keys(), sep=' ')
                return dict_result
            else:
                return True

        if len(sp) == 1:
            for node_one in node:
                cmd = 'linstor resource create %s %s --storage-pool %s' % (
                    node_one, res, sp[0])
                execute_(cmd)
            return print_fail_node()
        elif len(node) == len(sp):
            for node_one, stp_one in zip(node, sp):
                cmd = 'linstor resource create %s %s --storage-pool %s' % (
                    node_one, res, stp_one)
                execute_(cmd)
            return print_fail_node()
        else:
            print('The number of storage pools does not meet the requirements.')

    # 创建resource --diskless
    def create_res_diskless(self, node, res):
        cmd = 'linstor r c %s %s --diskless' % (node, res)
        return self.print_execute_result(cmd)

    # 删除resource,指定节点
    def delete_resource_des(self, node, res):
        cmd = 'linstor resource delete %s %s' % (node, res)
        return self.print_execute_result(cmd)

    # 删除resource，全部节点
    def delete_resource_all(self, res):
        cmd = 'linstor resource-definition delete %s' % res
        return self.print_execute_result(cmd)

    # 创建storagepool
    def create_storagepool_lvm(self, node, stp, vg):
        cmd = 'linstor storage-pool create lvm %s %s %s' % (node, stp, vg)
        result = execute_linstor_cmd(cmd)
        jud_result = Stor.re_sort(str(result))
        if jud_result == 'war':
            print(result)
        # 发生ERROR的情况
        if jud_result == 'err':
            # 使用不存的vg
            if Stor.judge_no_vg(str(result), node, vg):
                # 获取和打印提示信息
                result = Stor.judge_no_vg(str(result), node, vg)
                print(result)
                # 删除掉已创建的sp
                result_del = subprocess.check_output(
                    'linstor --no-color storage-pool delete %s %s' %
                    (node, stp), shell=True)
            else:
                print(result)
                print('FAIL')
                return result
        # 成功
        elif jud_result == 'suc':
            print('SUCCESS')
            return True

    def create_storagepool_thinlv(self, node, stp, tlv):
        cmd = 'linstor storage-pool create lvmthin %s %s %s' % (node, stp, tlv)
        return self.print_execute_result(cmd)

    # 删除storagepool -- ok
    def delete_storagepool(self, node, stp):
        cmd = 'linstor storage-pool delete %s %s' % (node, stp)
        try:
            return self.print_execute_result(cmd)
        except Exception as e:
            pass
            # self.logger.write_to_log('result_to_show','','',str(traceback.format_exc()))

    # 创建集群节点
    def create_node(self, node, ip, nt):
        cmd = 'linstor node create %s %s  --node-type %s' % (node, ip, nt)
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
            return self.print_execute_result(cmd)

    # 删除node
    def delete_node(self, node):
        cmd = 'linstor node delete %s' % node
        return self.print_execute_result(cmd)


class Iscsi():
    def __init__(self):
        self.logger = consts.get_glo_log()
        self.js = iscsi_json.JSON_OPERATION()

    """
    disk 操作
    """

    # 展示全部disk
    def show_all_disk(self):
        data = execute_linstor_cmd('linstor --no-color --no-utf8 r lv')
        linstorlv = Linstor.refine_linstor(data)
        disks = {}
        for d in linstorlv:
            disks.update({d[1]: d[5]})
        self.js.update_data('Disk', disks)
        print(" " + "{:<15}".format("Diskname") + "Path")
        print(" " + "{:<15}".format("---------------") + "---------------")
        for k in disks:
            output = (" " + "{:<15}".format(k) + disks[k])
            print(output)

    # 展示指定的disk
    def show_spe_disk(self, disk):
        if self.js.check_key('Disk', disk):
            output = (disk, ":", self.js.get_data('Disk').get(disk))
            print(output)
        else:
            print("Fail! Can't find " + disk)

    """
    host 操作
    """

    def create_host(self, host, iqn):
        print("Host name:", host)
        print("iqn:", iqn)
        if self.js.check_key('Host', host):
            print("Fail! The Host " + host + " already existed.")
        else:
            self.js.add_data("Host", host, iqn)
            print("Create success!")
            return True

    def show_all_host(self):
        hosts = self.js.get_data("Host")
        print(" " + "{:<15}".format("Hostname") + "Iqn")
        print(" " + "{:<15}".format("---------------") + "---------------")
        for k in hosts:
            print(" " + "{:<15}".format(k) + hosts[k])
        return True

    def show_spe_host(self, host):
        if self.js.check_key('Host', host):
            print(host, ":", self.js.get_data('Host').get(host))
            return True
        else:
            print("Fail! Can't find " + host)

    def delete_host(self, host):
        print("Delete the host <", host, "> ...")
        if self.js.check_key('Host', host):
            if self.js.check_value('HostGroup', host):
                print(
                    "Fail! The host in ... hostgroup, Please delete the hostgroup first.")
            else:
                self.js.delete_data('Host', host)
                print("Delete success!")
                return True
        else:
            print("Fail! Can't find " + host)

    """
    diskgroup 操作
    """

    def create_diskgroup(self, diskgroup, disk):
        # print("Diskgroup name:", diskgroup)
        # print("Disk name:", disk)
        if self.js.check_key('DiskGroup', diskgroup):
            print(
                "Fail! The DiskGroup " +
                diskgroup +
                " already existed.")
        else:
            t = True
            for i in disk:
                if self.js.check_key('Disk', i) == False:
                    t = False
                    print("Fail! Can't find " + i)
            if t:
                self.js.add_data('DiskGroup', diskgroup, disk)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")

    def show_all_diskgroup(self):
        print("Diskgroup:")
        diskgroups = self.js.get_data("DiskGroup")
        for k in diskgroups:
            print(" " + "---------------")
            print(" " + k + ":")
            for v in diskgroups[k]:
                print("     " + v)

    def show_diskgroup(self, dg):
        if dg == 'all' or dg is None:
            print("Diskgroup:")
            diskgroups = self.js.get_data("DiskGroup")
            for k in diskgroups:
                print(" " + "---------------")
                print(" " + k + ":")
                for v in diskgroups[k]:
                    print("     " + v)
        else:
            if self.js.check_key('DiskGroup', dg):
                print(dg + ":")
                for k in self.js.get_data('DiskGroup').get(dg):
                    print(" " + k)
            else:
                print("Fail! Can't find " + dg)

    def delete_diskgroup(self, dg):
        print("Delete the diskgroup <", dg, "> ...")
        if self.js.check_key('DiskGroup', dg):
            if self.js.check_value('Map', dg):
                print("Fail! The diskgroup already map,Please delete the map")
            else:
                self.js.delete_data('DiskGroup', dg)
                print("Delete success!")
        else:
            print("Fail! Can't find " + dg)

    """
    hostgroup 操作
    """

    def create_hostgroup(self, hostgroup, host):
        print("Hostgroup name:", hostgroup)
        print("Host name:", host)
        if self.js.check_key('HostGroup', hostgroup):
            print(
                "Fail! The HostGroup " +
                hostgroup +
                " already existed.")
        else:
            t = True
            for i in host:
                if self.js.check_key('Host', i) == False:
                    t = False
                    print("Fail! Can't find " + i)
            if t:
                self.js.add_data('HostGroup', hostgroup, host)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")

    def show_all_hostgroup(self):
        print("Hostgroup:")
        hostgroups = self.js.get_data("HostGroup")
        for k in hostgroups:
            print(" " + "---------------")
            print(" " + k + ":")
            for v in hostgroups[k]:
                print("     " + v)

    def show_spe_hostgroup(self, hg):
        if self.js.check_key('HostGroup', hg):
            print(hg + ":")
            for k in self.js.get_data('HostGroup').get(hg):
                print(" " + k)
        else:
            print("Fail! Can't find " + hg)

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
            print("The Map \"" + map + "\" already existed.")
        elif self.js.check_key('HostGroup', hg) == False:
            print("Can't find " + hg)
        elif self.js.check_key('DiskGroup', dg) == False:
            print("Can't find " + dg)
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
            print(crm_data_dict)
            target_all = crm_data_dict['target'][0] # 目前的设计只有一个target，所以取列表的第一个
            return target_all[0], target_all[1]  # 返回target_name, target_iqn

    def get_drbd_data(self, dg):
        # 根据dg去收集drbdd的三项数据：resource name，minor number，device name
        disk_all = self.js.get_data('DiskGroup').get(dg)
        linstor_cmd_result = execute_linstor_cmd('linstor --no-color --no-utf8 r lv')
        linstorlv = Linstor.refine_linstor(linstor_cmd_result)
        drdb_list = []
        for res in linstorlv:
            for disk_one in disk_all:
                if disk_one in res:
                    drdb_list.append([res[1], res[4], res[5]])  # 取Resource,MinorNr,DeviceName
        return drdb_list

    def create_map(self, hg, dg):
        obj_crm = CRM()
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
                    print('create colocation and order success:', res)
                    obj_crm.start_res(res)
                else:
                    print("create colocation and order fail")
            else:
                print('create resource Fail!')
        return True

    def show_all_map(self):
        js = iscsi_json.JSON_OPERATION()
        print("Map:")
        maps = js.get_data("Map")
        for k in maps:
            print(" " + "---------------")
            print(" " + k + ":")
            for v in maps[k]:
                print("     " + v)

    def show_spe_map(self, map):
        if self.js.check_key('Map', map):
            print(map + ":")
            maplist = self.js.get_data('Map').get(map)
            print(' ' + maplist[0] + ':')
            for i in self.js.get_data('HostGroup').get(maplist[0]):
                print('     ' + i + ': ' + self.js.get_data('Host').get(i))
            print(' ' + maplist[1] + ':')
            for i in self.js.get_data('DiskGroup').get(maplist[1]):
                print('     ' + i + ': ' + self.js.get_data('Disk').get(i))
        else:
            print("Fail! Can't find " + map)

    def pre_check_delete_map(self, map):
        print("Delete the map <", map, ">...")
        if self.js.check_key('Map', map):
            print(
                self.js.get_data('Map').get(
                    map),
                "will probably be affected ")
            dg = self.js.get_data('Map').get(map)[1]
            resname = self.js.get_data('DiskGroup').get(dg)
            if self.delete_map(resname):
                self.js.delete_data('Map', map)
                print("Delete success!")
        else:
            print("Fail! Can't find " + map)

    # 调用crm删除map
    def delete_map(self, resname):
        obj_crm = CRM()
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
