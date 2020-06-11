# coding=utf-8
import re
import subprocess
import time
import traceback
import iscsi_json
import log
import sys
from functools import wraps
from collections import OrderedDict


class TimeoutError(Exception):
    pass

class CRM():
    def __init__(self,logger):
        self.logger = logger

    def re_data(self, crmdatas):
        crmdata = str(crmdatas)
        plogical = re.compile(
            r'primitive\s(\w*)\s\w*\s\\\s*\w*\starget_iqn="([a-zA-Z0-9.:-]*)"\s[a-z=-]*\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators="([a-zA-Z0-9.: -]+)"(?:.*\s*){2}meta target-role=(\w*)')
        pvip = re.compile(
            r'primitive\s(\w*)\sIPaddr2\s\\\s*\w*\sip=([0-9.]*)\s\w*=(\d*)\s')
        ptarget = re.compile(
            r'primitive\s(\w*)\s\w*\s\\\s*params\siqn="([a-zA-Z0-9.:-]*)"\s[a-z=-]*\sportals="([0-9.]*):\d*"\s\\')
        redata = [
            plogical.findall(crmdata),
            pvip.findall(crmdata),
            ptarget.findall(crmdata)]
        print("get crm config data")
        return redata

    def get_data_crm(self):
        crmconfig = subprocess.getoutput('crm configure show')
        self.logger.write_to_log('CRM_CMD','crm configure show','',crmconfig)
        print("do crm configure show")
        # print("crmconfig:",crmconfig)
        return crmconfig

    def get_data_linstor(self):
        linstorres = subprocess.getoutput('linstor --no-color --no-utf8 r lv')
        print("do linstor r lv")
        return linstorres

    def createres(self, res, hostiqn, targetiqn):
        initiator = " ".join(hostiqn)
        lunid = str(int(res[1][1:]))
        op = " op start timeout=40 interval=0" \
             " op stop timeout=40 interval=0" \
             " op monitor timeout=40 interval=15"
        meta = " meta target-role=Stopped"
        mstr = "crm conf primitive " + res[0] \
               + " iSCSILogicalUnit params target_iqn=\"" + targetiqn \
               + "\" implementation=lio-t lun=" + lunid \
               + " path=\"" + res[2] \
               + "\" allowed_initiators=\"" + initiator + "\"" \
               + op + meta
        print(mstr)
        createcrm = subprocess.call(mstr, shell=True)
        print("call", mstr)
        if createcrm == 0:
            print("create iSCSILogicalUnit success")
            return True
        else:
            return False

    def delres(self, res):
        # crm res stop <LUN_NAME>
        stopsub = subprocess.call("crm res stop " + res, shell=True)
        if stopsub == 0:
            print("crm res stop " + res)
            n = 0
            while n < 10:
                n += 1
                if self.resstate(res):
                    print(res + " is Started, Wait a moment...")
                    time.sleep(1)
                else:
                    print(res + " is Stopped")
                    break
            else:
                print("Stop ressource " + res + " fail, Please try again.")
                return False

            time.sleep(3)
            # crm conf del <LUN_NAME>
            delsub = subprocess.call("crm conf del " + res, shell=True)
            if delsub == 0:
                print("crm conf del " + res)
                return True
            else:
                print("crm delete fail")
                return False
        else:
            print("crm res stop fail")
            return False

    def createco(self, res, target):
        # crm conf colocation <COLOCATION_NAME> inf: <LUN_NAME> <TARGET_NAME>
        print("crm conf colocation co_" + res + " inf: " + res + " " + target)
        coclocation = subprocess.call(
            "crm conf colocation co_" +
            res +
            " inf: " +
            res +
            " " +
            target,
            shell=True)
        if coclocation == 0:
            print("set coclocation")
            return True
        else:
            return False

    def createor(self, res, target):
        # crm conf order <ORDER_NAME1> <TARGET_NAME> <LUN_NAME>
        print("crm conf order or_" + res + " " + target + " " + res)
        order = subprocess.call(
            "crm conf order or_" +
            res +
            " " +
            target +
            " " +
            res,
            shell=True)
        if order == 0:
            print("set order")
            return True
        else:
            return False

    def resstart(self, res):
        # crm res start <LUN_NAME>
        print("crm res start " + res)
        start = subprocess.call("crm res start " + res, shell=True)
        if start == 0:
            return True
        else:
            return False

    def resstate(self, res):
        crm_show = self.get_data_crm()
        redata = self.re_data(crm_show)
        for s in redata[0]:
            if s[0] == res:
                if s[-1] == 'Stopped':
                    return False
                else:
                    return True


class LVM():
    @staticmethod
    def get_vg():
        result_vg = subprocess.Popen(
            'vgs',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return result_vg.stdout.read().decode()

    @staticmethod
    def get_thinlv():
        result_thinlv = subprocess.Popen(
            'lvs',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return result_thinlv.stdout.read().decode()

    @staticmethod
    def refine_thinlv(str):
        list_tb = str.splitlines()
        list_thinlv = []
        re_ = re.compile(
            r'\s*(\S*)\s*(\S*)\s*\S*\s*(\S*)\s*\S*\s*\S*\s*\S*\s*?')
        for list_one in list_tb:
            if 'twi' in list_one:
                thinlv_one = re_.findall(list_one)
                list_thinlv.append(list(thinlv_one[0]))
        return list_thinlv

    @staticmethod
    def refine_vg(str):
        list_tb = str.splitlines()
        list_vg = []
        re_ = re.compile(
            r'\s*(\S*)\s*\S*\s*\S*\s*\S*\s*\S*\s*(\S*)\s*(\S*)\s*?')
        for list_one in list_tb[1:]:
            vg_one = re_.findall(list_one)
            list_vg.append(list(vg_one[0]))
        return list_vg


class LINSTOR():
    def __init__(self,logger):
        self.logger = logger

    def get_linstor(self,cmd):
        Popen_linstor = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        str_result = Popen_linstor.stdout.read().decode('utf-8')
        self.logger.write_to_log('LINSTORDB',cmd,'',str_result)
        return str_result

    # def get_node(self):
    #     result_node = subprocess.Popen(
    #         'linstor --no-color --no-utf8 n l',
    #         shell=True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT)
    #     return result_node.stdout.read().decode('utf-8')
    #
    # @staticmethod
    # def get_res():
    #     result_res = subprocess.Popen(
    #         'linstor --no-color --no-utf8 r lv',
    #         shell=True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT)
    #     return result_res.stdout.read().decode('utf-8')
    #
    # @staticmethod
    # def get_sp():
    #     result_sp = subprocess.Popen(
    #         'linstor --no-color --no-utf8 sp l',
    #         shell=True,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT)
    #     return result_sp.stdout.read().decode('utf-8')

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


def result_cmd(func):
    """
    Decorator for post processing of execution commands.
    Judge the output of the command.
    :param result: command stdout
    :return: True/Command output
    """
    @wraps(func)
    def wrapper(*args):
        result = func(*args)
        if Stor.judge_cmd_result_war(str(result)):
            messege_war = Stor.get_war_mes(result.decode('utf-8'))
            print(messege_war)
        if Stor.judge_cmd_result_suc(str(result)):
            return True
        elif Stor.judge_cmd_result_err(str(result)):
            return result.decode()
        else:
            return result.decode()
    return wrapper


# 子命令stor调用的方法
class Stor():

    def __init__(self,logger):
        self.logger = logger


    @staticmethod
    def judge_cmd_result(result):
        re_suc = re.compile('SUCCESS')
        re_war = re.compile('WARNING')
        re_err = re.compile('ERROR')
        if re_war.search(result):
            return 'WAR'
        elif re_err.search(result):
            return 'ERR'
        elif re_suc.search(result):
            return 'SUC'


    @staticmethod
    def judge_cmd_result_suc(cmd):
        re_suc = re.compile('SUCCESS')
        if re_suc.search(cmd):
            return True

    @staticmethod
    def judge_cmd_result_err(cmd):
        re_err = re.compile('ERROR')
        if re_err.search(cmd):
            return True

    @staticmethod
    def judge_cmd_result_war(cmd):
        re_err = re.compile('WARNING')
        if re_err.search(cmd):
            return True

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


    @result_cmd
    def execute_cmd(self,cmd, timeout=60):
        """
        Execute the command cmd to return the content of the command output.
        If it times out, a TimeoutError exception will be thrown.
        cmd - Command to be executed
        timeout - The longest waiting time(unit:second)
        """
        p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
        t_beginning = time.time()
        seconds_passed = 0
        while True:
            if p.poll() is not None:
                break
            seconds_passed = time.time() - t_beginning
            if timeout and seconds_passed > timeout:
                p.terminate()
                self.logger.write_to_log('LINSTOR',cmd,'','TimeoutError')
                raise TimeoutError(cmd, timeout)
            time.sleep(0.1)
        result = p.stdout.read()
        self.logger.write_to_log('LINSTOR', cmd, '', result)
        return result


    def print_execute_result(self,cmd):
        result = self.execute_cmd(cmd)
        if not result:
            self.logger.write_to_log('result_to_show','','',result)
            return
        if result is True:
            print('SUCCESS')
            self.logger.write_to_log('result_to_show','','','SUCCESS')
            return True
        else:
            print(result)
            print('FAIL')
            self.logger.write_to_log('result_to_show',result,'','FAIL')
            return result


    # 创建resource相关 -- ok
    def linstor_delete_rd(self,res):
        cmd = 'linstor rd d %s' % res
        result = subprocess.check_output(cmd, shell=True)
        self.logger.write_to_log('LINSTOR',cmd,'',result)


    def linstor_delete_vd(self,res):
        cmd = 'linstor vd d %s' % res
        result = subprocess.check_output(cmd, shell=True)
        self.logger.write_to_log('LINSTOR',cmd,'',result)

    def linstor_create_rd(self,res):
        cmd_rd = 'linstor rd c %s' % res
        result = self.execute_cmd(cmd_rd)
        if result is True:
            return True
        else:
            print('FAIL')
            return result

    def linstor_create_vd(self,res, size):
        cmd_vd = 'linstor vd c %s %s' % (res, size)
        result = self.execute_cmd(cmd_vd)
        if result is True:
            return True
        else:
            print('FAIL')
            self.linstor_delete_rd(res)
            return result

    # 创建resource 自动
    def create_res_auto(self,res, size, num):
        cmd = 'linstor r c %s --auto-place %d' % (res, num)
        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            result = self.execute_cmd(cmd)
            if result is True:
                print('SUCCESS')
                self.logger.write_to_log('result_to_show','','','SUCCESS')
                return True
            else:
                print('FAIL')
                self.linstor_delete_rd(res)
                self.logger.write_to_log('result_to_show','','','FAIL')
                return result
        else:
            print('The resource already exists')
            # cls.logger.add_log(username, 'result_to_show', transaction_id, '', '', 'The resource already exists')
            return ('The resource already exists')


    def create_res_manual(self,res,size,node,sp):
        flag = OrderedDict()

        # Actions needed to create a resource
        def excute_(cmd):
            try:
                # Undo the decorator @result_cmd, and execute execute_cmd function
                ex_cmd = self.execute_cmd.__wrapped__
                result = ex_cmd(self, cmd)
                if Stor.judge_cmd_result_war(str(result)):
                    print(Stor.get_war_mes(result.decode('utf-8')))
                if Stor.judge_cmd_result_suc(str(result)):
                    result = ('Resource %s was successfully created on Node %s' % (res, node_one))
                    print(result)
                    self.logger.write_to_log('result_to_show','','',result)
                elif Stor.judge_cmd_result_err(str(result)):
                    str_fail_cause = Stor.get_err_detailes(result.decode('utf-8'))
                    dict_fail = {node_one: str_fail_cause}
                    flag.update(dict_fail)
            except TimeoutError as e:
                flag.update({node_one: 'Execution creation timeout'})
                # logger
                print('%s created timeout on node %s, the operation has been cancelled' % (res, node_one))

        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            pass
        else:
            # need to be prefect
            print('The resource already exists')
            self.logger.write_to_log('result_to_show','','','The resource already exists')
            return ('The resource already exists')

        if len(sp) == 1:
            for node_one in node:
                cmd = 'linstor resource create %s %s --storage-pool %s' % (node_one, res, sp[0])
                excute_(cmd)
            if len(flag.keys()) == len(node):
                self.linstor_delete_rd(res)
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
                self.logger.write_to_log('result_to_show', '', '','Creation failure on %s'%' '.join(flag.keys()))
                for node, cause in flag.items():
                    print(node, ':', cause)
                return flag
            else:
                return True

        # When sp is not one, it is equal to the number of nodes
        else:
            for node_one, sp_one in zip(node, sp):
                cmd = 'linstor resource create %s %s --storage-pool %s' % (node_one, res, sp_one)
                excute_(cmd)
            if len(flag.keys()) == len(node):
                self.linstor_delete_rd(res)
            # whether_delete_rd()
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
                self.logger.write_to_log('result_to_show', '', '','Creation failure on %s'%' '.join(flag.keys()))
                for node, cause in flag.items():
                    print(node, ':', cause)
                return flag
            else:
                return True
            # return print_fail_node()

    # 添加mirror（自动）
    def add_mirror_auto(self,res, num):
        cmd = 'linstor r c %s --auto-place %d' % (res, num)
        return self.print_execute_result(cmd)

    def add_mirror_manual(self,res, node, sp):
        flag = OrderedDict()
        def excute_(cmd):
            try:
                # Undo the decorator @result_cmd, and execute execute_cmd function
                ex_cmd = self.execute_cmd.__wrapped__
                result = ex_cmd(self, cmd)
                if Stor.judge_cmd_result_war(str(result)):
                    print(Stor.get_war_mes(result.decode('utf-8')))
                if Stor.judge_cmd_result_suc(str(result)):
                    result = ('Resource %s was successfully created on Node %s' % (res, node_one))
                    print(result)
                    self.logger.write_to_log('result_to_show','','',result)
                elif Stor.judge_cmd_result_err(str(result)):
                    str_fail_cause = Stor.get_err_detailes(result.decode('utf-8'))
                    dict_fail = {node_one: str_fail_cause}
                    flag.update(dict_fail)
            except TimeoutError as e:
                flag.update({node_one: 'Execution creation timeout'})
                print('%s created timeout on node %s, the operation has been cancelled' % (res, node_one))
                self.logger.write_to_log('result_to_show','','','%s created timeout on node %s, the operation has been cancelled' % (res, node_one))

        def print_fail_node():
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
                self.logger.write_to_log('result_to_show','','','Creation failure on %s'%' '.join(flag.keys()))
                return flag
            else:
                return True

        if len(sp) == 1:
            for node_one in node:
                cmd = 'linstor resource create %s %s --storage-pool %s' % (
                    node_one, res, sp[0])
                excute_(cmd)
            return print_fail_node()
        elif len(node) == len(sp):
            for node_one, stp_one in zip(node, sp):
                cmd = 'linstor resource create %s %s --storage-pool %s' % (
                    node_one, res, stp_one)
                excute_(cmd)
            return print_fail_node()
        else:
            print('The number of storage pools does not meet the requirements.')

    # 创建resource --diskless
    def create_res_diskless(self,node, res):
        cmd = 'linstor r c %s %s --diskless' % (node, res)
        return self.print_execute_result(cmd)

    # 删除resource,指定节点
    def delete_resource_des(self,node, res):
        cmd = 'linstor resource delete %s %s' % (node, res)
        return self.print_execute_result(cmd)

    # 删除resource，全部节点
    def delete_resource_all(self,res):
        cmd = 'linstor resource-definition delete %s' % res
        return self.print_execute_result(cmd)

    # 创建storagepool
    def create_storagepool_lvm(self,node, stp, vg):
        cmd = 'linstor storage-pool create lvm %s %s %s' % (node, stp, vg)
        action = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        result = action.stdout
        self.logger.write_to_log('LINSTOR', cmd, '', result.decode())
        if Stor.judge_cmd_result_war(str(result)):
            print(result.decode('utf-8'))
            self.logger.write_to_log('result_to_show','','',result.decode())
        # 发生ERROR的情况
        if Stor.judge_cmd_result_err(str(result)):
            # 使用不存的vg
            if Stor.judge_no_vg(str(result), node, vg):
                # 获取和打印提示信息
                result = Stor.judge_no_vg(str(result), node, vg)
                print(result)
                self.logger.write_to_log('result_to_show','','',result) # result为vg相关的提示
                # 删除掉已创建的sp
                result_del = subprocess.check_output(
                    'linstor --no-color storage-pool delete %s %s' %
                    (node, stp), shell=True)
                self.logger.write_to_log('LINSTOR','linstor --no-color storage-pool delete %s %s'%(node, stp), 'post-processing', result_del.decode())
            else:
                print(result.decode('utf-8'))
                print('FAIL')
                self.logger.write_to_log('result_to_show',str(result),'','FAIL') # result为其他ERROR信息
                return result.decode()
        # 成功
        elif Stor.judge_cmd_result_suc(str(result)):
            print('SUCCESS')
            self.logger.write_to_log('LINSTOR',cmd,'',str(result))
            self.logger.write_to_log('result_to_show','','','SUCCESS')
            return True

    def create_storagepool_thinlv(self,node, stp, tlv):
        cmd = 'linstor storage-pool create lvmthin %s %s %s' % (node, stp, tlv)
        return self.print_execute_result(cmd)

    # 删除storagepool -- ok
    def delete_storagepool(self,node, stp):
        cmd = 'linstor storage-pool delete %s %s' % (node, stp)
        try:
            return self.print_execute_result(cmd)
        except Exception as e:
            self.logger.write_to_log('result_to_show','','',str(traceback.format_exc()))

    # 创建集群节点
    def create_node(self,node, ip, nt):
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
            self.logger.write_to_log('result_to_show','','','node type error,choose from Combined Controller Auxiliary Satellite')
        else:
            return self.print_execute_result(cmd)

    # 删除node
    def delete_node(self,node):
        cmd = 'linstor node delete %s' % node
        return self.print_execute_result(cmd)


class Iscsi():
    def __init__(self,logger):
        self.logger = logger

    # 获取并更新crm信息
    def crm_up(self, js):
        cd = CRM(self.logger)
        crm_config_statu = cd.get_data_crm()
        if 'ERROR' in crm_config_statu:
            print("Could not perform requested operations, are you root?")
            self.logger.write_to_log('result_to_show','','','Could not perform requested operations, are you root?')
            return False
        else:
            redata = cd.re_data(crm_config_statu)
            js.up_crmconfig(redata)
            return redata

    # 获取创建map所需的数据
    def map_data(self, js, crmdata, hg, dg):
        mapdata = {}
        hostiqn = []
        for h in js.get_data('HostGroup').get(hg):
            iqn = js.get_data('Host').get(h)
            hostiqn.append(iqn)
        mapdata.update({'host_iqn': hostiqn})
        disk = js.get_data('DiskGroup').get(dg)
        cd = CRM(self.logger)
        data = cd.get_data_linstor()
        linstorlv = LINSTOR.refine_linstor(data)
        diskd = {}
        for d in linstorlv:
            for i in disk:
                if i in d:
                    diskd.update({d[1]: [d[4], d[5]]})
        mapdata.update({'disk': diskd})
        mapdata.update({'target': crmdata[2]})

        return mapdata

    # 获取删除map所需的数据
    def map_data_d(self, js, mapname):
        dg = js.get_data('Map').get(mapname)[1]
        disk = js.get_data('DiskGroup').get(dg)
        return disk

    # 调用crm创建map
    def map_crm_c(self, mapdata):
        cd = CRM(self.logger)
        for i in mapdata['target']:
            target = i[0]
            targetiqn = i[1]
        for disk in mapdata['disk']:
            res = [
                disk,
                mapdata['disk'].get(disk)[0],
                mapdata['disk'].get(disk)[1]]
            if cd.createres(res, mapdata['host_iqn'], targetiqn):
                c = cd.createco(res[0],target)
                o = cd.createor(res[0],target)
                s = cd.resstart(res[0])
                if c and o and s:
                    print('create colocation and order success:', disk)
                else:
                    print("create colocation and order fail")
                    return False
            else:
                print('create resource Fail!')
                return False
        return True

    # 调用crm删除map
    def map_crm_d(self, resname):
        cd = CRM(self.logger)
        crm_config_statu = cd.get_data_crm()
        if 'ERROR' in crm_config_statu:
            print("Could not perform requested operations, are you root?")
            return False
        else:
            for disk in resname:
                if cd.delres(disk):
                    print("delete ", disk)
                else:
                    return False
            return True


    def show_disk(self,disk):
        js = iscsi_json.JSON_OPERATION(self.logger)

        data = LINSTOR.get_linstor(LINSTOR(self.logger),'linstor --no-color --no-utf8 r lv')
        linstorlv = LINSTOR.refine_linstor(data)
        disks = {}
        for d in linstorlv:
            disks.update({d[1]: d[5]})
        js.up_data('Disk', disks)
        if disk == 'all' or disk is None:
            print(" " + "{:<15}".format("Diskname") + "Path")
            print(" " + "{:<15}".format("---------------") + "---------------")
            self.logger.write_to_log('result_to_show','','',(" " + "{:<15}".format("Diskname") + "Path"))
            for k in disks:
                output = (" " + "{:<15}".format(k) + disks[k])
                print(output)
                self.logger.write_to_log('result_to_show','','',output)
        else:
            if js.check_key('Disk', disk):
                output = (disk, ":", js.get_data('Disk').get(disk))
                print(output)
                self.logger.write_to_log('result_to_show','','',output)
            else:
                print("Fail! Can't find " + disk)
                self.logger.write_to_log('result_to_show','','',"Fail! Can't find %s"%disk)


    def create_host(self,host, iqn):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Host name:", host)
        print("iqn:", iqn)
        if js.check_key('Host', host):
            print("Fail! The Host " + host + " already existed.")
            return False
        else:
            js.creat_data("Host", host, iqn)
            print("Create success!")
            self.logger.write_to_log('result_to_show','','','Create success!')
            return True

    def show_host(self,host):
        js = iscsi_json.JSON_OPERATION(self.logger)
        if host == 'all' or host is None:
            hosts = js.get_data("Host")
            print(" " + "{:<15}".format("Hostname") + "Iqn")
            print(" " + "{:<15}".format("---------------") + "---------------")
            for k in hosts:
                print(" " + "{:<15}".format(k) + hosts[k])
        else:
            if js.check_key('Host', host):
                print(host, ":", js.get_data('Host').get(host))
            else:
                print("Fail! Can't find " + host)
                return False
        return True

    def delete_host(self,host):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Delete the host <", host, "> ...")
        if js.check_key('Host', host):
            if js.check_value('HostGroup', host):
                print(
                    "Fail! The host in ... hostgroup, Please delete the hostgroup first.")
                return False
            else:
                js.delete_data('Host', host)
                print("Delete success!")
                return True
        else:
            print("Fail! Can't find " + host)
            return False

    def create_diskgroup(self,diskgroup, disk):
        js = iscsi_json.JSON_OPERATION(self.logger)
        # print("Diskgroup name:", diskgroup)
        # print("Disk name:", disk)
        if js.check_key('DiskGroup', diskgroup):
            print(
                "Fail! The DiskGroup " +
                diskgroup +
                " already existed.")
            self.logger.write_to_log('result_to_show','','',(
                "Fail! The DiskGroup " +
                diskgroup +
                " already existed."))
            return False
        else:
            t = True
            for i in disk:
                if js.check_key('Disk', i) == False:
                    t = False
                    print("Fail! Can't find " + i)
                    self.logger.write_to_log('resutl_to_show','','',("Fail! Can't find " + i))
            if t:
                js.creat_data('DiskGroup', diskgroup, disk)
                print("Create success!")
                self.logger.write_to_log('result_to_show','','','Create success!')
                return True
            else:
                print("Fail! Please give the true name.")
                self.logger.write_to_log('result_to_show','','','Fail! Please give the true name.')
                return False

    def show_diskgroup(self,dg):
        js = iscsi_json.JSON_OPERATION(self.logger)
        if dg == 'all' or dg is None:
            print("Diskgroup:")
            diskgroups = js.get_data("DiskGroup")
            for k in diskgroups:
                print(" " + "---------------")
                print(" " + k + ":")
                for v in diskgroups[k]:
                    print("     " + v)
        else:
            if js.check_key('DiskGroup', dg):
                print(dg + ":")
                for k in js.get_data('DiskGroup').get(dg):
                    print(" " + k)
            else:
                print("Fail! Can't find " + dg)

    def delete_diskgroup(self,dg):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Delete the diskgroup <", dg, "> ...")
        if js.check_key('DiskGroup', dg):
            if js.check_value('Map', dg):
                print("Fail! The diskgroup already map,Please delete the map")
            else:
                js.delete_data('DiskGroup', dg)
                print("Delete success!")
        else:
            print("Fail! Can't find " + dg)

    def create_hostgroup(self,hostgroup, host):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Hostgroup name:", hostgroup)
        print("Host name:", host)
        if js.check_key('HostGroup', hostgroup):
            print(
                "Fail! The HostGroup " +
                hostgroup +
                " already existed.")
            return False
        else:
            t = True
            for i in host:
                if js.check_key('Host', i) == False:
                    t = False
                    print("Fail! Can't find " + i)
            if t:
                js.creat_data('HostGroup', hostgroup, host)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")
                return False

    def show_hostgroup(self,hg):
        js = iscsi_json.JSON_OPERATION(self.logger)
        if hg == 'all' or hg is None:
            print("Hostgroup:")
            hostgroups = js.get_data("HostGroup")
            for k in hostgroups:
                print(" " + "---------------")
                print(" " + k + ":")
                for v in hostgroups[k]:
                    print("     " + v)
        else:
            if js.check_key('HostGroup', hg):
                print(hg + ":")
                for k in js.get_data('HostGroup').get(hg):
                    print(" " + k)
            else:
                print("Fail! Can't find " + hg)

    def delete_hostgroup(self,hg):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Delete the hostgroup <", hg, "> ...")
        if js.check_key('HostGroup', hg):
            if js.check_value('Map', hg):
                print("Fail! The hostgroup already map,Please delete the map")
            else:
                js.delete_data('HostGroup', hg)
                print("Delete success!")
        else:
            print("Fail! Can't find " + hg)

    def create_map(self, map, hg, dg):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Map name:", map)
        print("Hostgroup name:", hg)
        print("Diskgroup name:", dg)
        if js.check_key('Map', map):
            print("The Map \"" + map + "\" already existed.")
            return False
        elif js.check_key('HostGroup', hg) == False:
            print("Can't find " + hg)
            return False
        elif js.check_key('DiskGroup', dg) == False:
            print("Can't find " + dg)
            return False
        else:
            if js.check_value('Map', dg):
                print("The diskgroup already map")
                return False
            else:
                crmdata = self.crm_up(js)
                if crmdata:
                    mapdata = self.map_data(
                        js, crmdata, hg, dg)
                    if self.map_crm_c(mapdata):
                        js.creat_data('Map', map, [hg, dg])
                        print("Create success!")
                        return True
                    else:
                        return False
                else:
                    return False

    def show_map(self,map):
        js = iscsi_json.JSON_OPERATION(self.logger)
        if map == 'all' or map is None:
            print("Map:")
            maps = js.get_data("Map")
            for k in maps:
                print(" " + "---------------")
                print(" " + k + ":")
                for v in maps[k]:
                    print("     " + v)
        else:
            if js.check_key('Map', map):
                print(map + ":")
                maplist = js.get_data('Map').get(map)
                print(' ' + maplist[0] + ':')
                for i in js.get_data('HostGroup').get(maplist[0]):
                    print('     ' + i + ': ' + js.get_data('Host').get(i))
                print(' ' + maplist[1] + ':')
                for i in js.get_data('DiskGroup').get(maplist[1]):
                    print('     ' + i + ': ' + js.get_data('Disk').get(i))
            else:
                print("Fail! Can't find " + map)

    def delete_map(self,map):
        js = iscsi_json.JSON_OPERATION(self.logger)
        print("Delete the map <", map, ">...")
        if js.check_key('Map', map):
            print(
                js.get_data('Map').get(
                    map),
                "will probably be affected ")
            resname = self.map_data_d(js, map)
            if self.map_crm_d(resname):
                js.delete_data('Map', map)
                print("Delete success!")
        else:
            print("Fail! Can't find " + map)