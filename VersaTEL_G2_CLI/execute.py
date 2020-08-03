# coding=utf-8
import re
import subprocess
import time
import iscsi_json
import consts
from collections import OrderedDict



def re_findall(re_string, tgt_string):
    re_login = re.compile(re_string)
    re_result = re_login.findall(tgt_string)
    return re_result

def re_search(re_string,tgt_stirng):
    re_ = re.compile(re_string)
    re_result = re_.search(tgt_stirng).group()
    return re_result


def execute_linstor_cmd(cmd,timeout=60):
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
    # result = Stor.re_sort(output)
    # return result # resouce的创建需要原始结果，这里返回'SUC'/'WAR'/'ERR'



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
    out,err = p.communicate()
    if len(out) > 0:
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output
    if len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
        return output
    if out == b'':# 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output


def get_cmd(ssh_obj, unique_str, cmd, oprt_id):
    logger = consts.get_glo_log()
    global RPL
    RPL = 'no'
    if RPL == 'no':
        logger.write_to_log('F', 'DATA', 'STR', unique_str, '', oprt_id)
        logger.write_to_log('T', 'OPRT', 'cmd', 'ssh', oprt_id, cmd)
        result_cmd = ssh_obj.execute_command(cmd)
        logger.write_to_log('F', 'DATA', 'cmd', 'ssh', oprt_id, result_cmd)
        return result_cmd
    elif RPL == 'yes':
        pass



class TimeoutError(Exception):
    pass

class CRM():
    def __init__(self):
        self.logger = consts.get_glo_log()

    # 正则匹配crm conf 数据
    def re_crm_data(self, crmdatas):
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

    def get_crm_data(self):
        cmd = 'crm configure show'
        result = execute_crm_cmd(cmd)
        print("do crm configure show")
        if result:
            return result['rts']


    def create_crm_res(self,res,target_iqn,lunid,path,initiator):

        script = f'crm conf primitive {res}  iSCSILogicalUnit params ' \
            f'target_iqn= "{target_iqn}" ' \
            f'implementation=lio-t ' \
            f'lun="{lunid}" ' \
            f'path="{path}" ' \
            f'allowed_initiators="{initiator}"' \
            f'op start timeout=40 interval=0 ' \
            f'op stop timeout=40 interval=0 ' \
            f'op monitor timeout=40 interval=15 ' \
            f'meta target-role=Stopped'

        result = execute_crm_cmd(script)
        if result['sts']:
            print("Create iSCSILogicalUnit success")
            return True
        else:
            return False

    # def create_res(self, res, hostiqn, targetiqn):
    #     initiator = " ".join(hostiqn)
    #
    #     lunid = str(int(res[1][1:])) #根据disk后两位数作为lun id，从linstor lv l获取
    #
    #     script = f'crm conf primitive {res[0]}  iSCSILogicalUnit params ' \
    #         f'target_iqn= "{targetiqn}" ' \
    #         f'implementation=lio-t ' \
    #         f'lun="{lunid}" ' \
    #         f'path="{res[2]}" ' \
    #         f'allowed_initiators="{initiator}"' \
    #         f'op start timeout=40 interval=0 ' \
    #         f'op stop timeout=40 interval=0 ' \
    #         f'op monitor timeout=40 interval=15 ' \
    #         f'meta target-role=Stopped'
    #
    #     result = execute_crm_cmd(script)
    #     if result['sts']:
    #         print("Create iSCSILogicalUnit success")
    #         return True
    #     else:
    #         return False

    # 停用res
    def stop_res(self,res):
        cmd = f'cmr res stop {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            print("crm res stop fail")
            return False
    # 检查
    def checkout_status(self,res):
        n = 0
        while n < 10:
            n += 1
            if self.get_res_state(res):
                print(res + " is Started, Wait a moment...")
                time.sleep(1)
            else:
                print(res + " is Stopped")
                break
        else:
            print("Stop ressource " + res + " fail, Please try again.")
            return False

    def del_res(self, res):
        # crm res stop <LUN_NAME>
        if self.stop_res(res):
            if self.checkout_status(res) is not False:
                time.sleep(3)
                # crm conf del <LUN_NAME>
                cmd = f'crm conf del {res}'
                result = execute_crm_cmd(cmd)
                if result['sts']:
                    print("crm conf del " + res)
                    return True
                else:
                    print("crm delete fail")
                    return False

    def create_col(self, res, target):
        # crm conf colocation <COLOCATION_NAME> inf: <LUN_NAME> <TARGET_NAME>
        print("crm conf colocation co_" + res + " inf: " + res + " " + target)
        cmd = f'crm conf colocation co_{res} inf: {res} {target}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            print("set coclocation")
            return True
        else:
            return False

    def create_order(self, res, target):
        # crm conf order <ORDER_NAME1> <TARGET_NAME> <LUN_NAME>
        print("crm conf order or_" + res + " " + target + " " + res)

        cmd = f'cmr conf order or_{res} {target} {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            print("set order")
            return True
        else:
            return False

    def start_res(self, res):
        # crm res start <LUN_NAME>
        print("crm res start " + res)
        cmd = f'crm res start {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            return False

    def get_res_state(self, res):
        crm_show = self.get_crm_data()
        re_result = self.re_crm_data(crm_show)
        for s in re_result[0]:
            # [[], [], [('t_test', 'iqn.2020-06.com.example:test-max-lun', '10.203.1.199')]]
            if s[0] == res:
                if s[-1] == 'Stopped':
                    return False
                else:
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

    def refine_thinlv(self,str):
        all_lv = str.splitlines()
        list_thinlv = []
        re_ = re.compile(
            r'\s*(\S*)\s*(\S*)\s*\S*\s*(\S*)\s*\S*\s*\S*\s*\S*\s*?')
        for one in all_lv:
            if 'twi' in one:
                thinlv_one = re_.findall(one)
                list_thinlv.append(list(thinlv_one[0]))
        return list_thinlv

    def refine_vg(self,str):
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

    def judge_result(self,result):
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


    def print_execute_result(self,cmd):
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
    def linstor_delete_rd(self,res):
        cmd = 'linstor rd d %s' % res
        result = subprocess.check_output(cmd, shell=True)


    def linstor_delete_vd(self,res):
        cmd = 'linstor vd d %s' % res
        result = subprocess.check_output(cmd, shell=True)

    def linstor_create_rd(self,res):
        cmd_rd = 'linstor rd c %s' % res
        output = execute_linstor_cmd(cmd_rd)
        result = self.judge_result(output)
        print(result)
        if result is True:
            return True
        else:
            print('FAIL')
            return result

    def linstor_create_vd(self,res, size):
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
    def create_res_auto(self,res, size, num):
        cmd = 'linstor r c %s --auto-place %d' % (res, num)
        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            output = execute_linstor_cmd(cmd)
            result = self.judge_result(output)
            if result is True:
                print('SUCCESS')
                return True
            else:
                print('FAIL')
                self.linstor_delete_rd(res)
                return result
        else:
            print('The resource already exists')
            return ('The resource already exists')


    def create_res_manual(self,res,size,node,sp):
        flag = OrderedDict()

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
                    flag.update(dict_fail)

            except TimeoutError as e:
                flag.update({node_one: 'Execution creation timeout'})
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
            if len(flag.keys()) == len(node):
                self.linstor_delete_rd(res)
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
                for node, cause in flag.items():
                    print(node, ':', cause)
                return flag
            else:
                return True

        # When sp is not one, it is equal to the number of nodes
        else:
            for node_one, sp_one in zip(node, sp):
                cmd = 'linstor resource create %s %s --storage-pool %s' % (node_one, res, sp_one)
                execute_(cmd)
            if len(flag.keys()) == len(node):
                self.linstor_delete_rd(res)
            # whether_delete_rd()
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
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
                    flag.update(dict_fail)
            except TimeoutError as e:
                flag.update({node_one: 'Execution creation timeout'})
                print('%s created timeout on node %s, the operation has been cancelled' % (res, node_one))

        def print_fail_node():
            if len(flag.keys()):
                print('Creation failure on', *flag.keys(), sep=' ')
                return flag
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
        result = execute_linstor_cmd(cmd)
        jud_result = Stor.re_sort(str(result))
        if jud_result == 'WAR':
            print(result)
        # 发生ERROR的情况
        if jud_result == 'ERR':
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
        elif jud_result == 'SUC':
            print('SUCCESS')
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
            pass
            # self.logger.write_to_log('result_to_show','','',str(traceback.format_exc()))

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
        else:
            return self.print_execute_result(cmd)

    # 删除node
    def delete_node(self,node):
        cmd = 'linstor node delete %s' % node
        return self.print_execute_result(cmd)



class Iscsi():
    def __init__(self):
        self.logger = consts.get_glo_log()


    # 获取并更新crm信息
    def get_lastest_crm(self):
        obj_crm = CRM()
        crm_config_status = obj_crm.get_crm_data()
        if 'ERROR' in crm_config_status:
            print("Could not perform requested operations, are you root?")
            return False
        else:
            js = iscsi_json.JSON_OPERATION()
            redata = obj_crm.re_crm_data(crm_config_status)
            js.update_crm_conf(redata)
            return redata

    # # 获取创建map所需的数据
    # def map_data(self, js, crmdata, hg, dg):
    #     mapdata = {}
    #     hostiqn = []
    #     for h in js.get_data('HostGroup').get(hg):
    #         iqn = js.get_data('Host').get(h)
    #         hostiqn.append(iqn)
    #     mapdata.update({'host_iqn': hostiqn})
    #     disk = js.get_data('DiskGroup').get(dg)
    #     linstor_cmd_result = execute_crm_cmd('linstor --no-color --no-utf8 r lv')
    #     linstorlv = Linstor.refine_linstor(linstor_cmd_result['rts'])
    #     diskd = {}
    #     for d in linstorlv:
    #         for i in disk:
    #             if i in d:
    #                 diskd.update({d[1]: [d[4], d[5]]})
    #     mapdata.update({'disk': diskd})
    #     mapdata.update({'target': crmdata[2]})
    #     return mapdata

    # 获取删除map所需的数据
    def map_data_d(self, js, mapname):
        dg = js.get_data('Map').get(mapname)[1]
        disk = js.get_data('DiskGroup').get(dg)
        return disk


    def map_crm_c_(self,hg,dg):
        # def create_crm_res(self, res, target_iqn, lunid, path, initiator):
        obj_crm = CRM()
        js = iscsi_json.JSON_OPERATION()

        # 根据hg去收集hostiqn
        hostiqn = []
        for h in js.get_data('HostGroup').get(hg):
            iqn = js.get_data('Host').get(h)
            hostiqn.append(iqn)
        initiator = " ".join(hostiqn)


        # 根据dg去收集res
        disk_all = js.get_data('DiskGroup').get(dg)
        linstor_cmd_result = execute_linstor_cmd('linstor --no-color --no-utf8 r lv')
        linstorlv = Linstor.refine_linstor(linstor_cmd_result)
        # res ,lunid ,path
        linstor_res_list = []
        for res in linstorlv:
            for disk_one in disk_all:
                if disk_one in res:
                    linstor_res_list.append([res[1],res[4],res[5]]) # 取Resource,MinorNr,DeviceName

        # 收集收集target_iqn
        crmdata = self.get_lastest_crm()  # 格式：[[],[],[]]
        if not crmdata:
            return
        tgt_all = crmdata[2]
        target = tgt_all[0]
        targetiqn = tgt_all[1]

        # 执行创建和启动
        for i in linstor_res_list:
            res,minor_nr,path = i
            lunid = minor_nr[-2:] #lun id 取自MinorNr的后两位数字
            if obj_crm.create_crm_res(res,targetiqn,lunid,path,initiator):
                c = obj_crm.create_col(res[0],target)
                o = obj_crm.create_order(res[0],target)
                s = obj_crm.start_res(res[0])
                if c and o and s:
                    print('create colocation and order success:', res)
                else:
                    print("create colocation and order fail")
                    return False
            else:
                print('create resource Fail!')
                return False
        return True


    # # 调用crm创建map
    # def map_crm_c(self, mapdata):
    #     cd = CRM()
    #     target = mapdata['target'][0]
    #     targetiqn = mapdata['target'][1]
    #     for disk in mapdata['disk']:
    #         res = [
    #             disk,# Resource
    #             mapdata['disk'].get(disk)[0], # MinorNr
    #             mapdata['disk'].get(disk)[1]] # DeviceName
    #         if cd.create_res(res, mapdata['host_iqn'], targetiqn):
    #             c = cd.create_col(res[0],target)
    #             o = cd.create_order(res[0],target)
    #             s = cd.start_res(res[0])
    #             if c and o and s:
    #                 print('create colocation and order success:', disk)
    #             else:
    #                 print("create colocation and order fail")
    #                 return False
    #         else:
    #             print('create resource Fail!')
    #             return False
    #     return True

    # 调用crm删除map
    def map_crm_d(self, resname):
        cd = CRM()
        crm_config_statu = cd.get_crm_data()
        if 'ERROR' in crm_config_statu:
            print("Could not perform requested operations, are you root?")
            return False
        else:
            for disk in resname:
                if cd.del_res(disk):
                    print("delete ", disk)
                else:
                    return False
            return True


    def show_disk(self,disk):
        js = iscsi_json.JSON_OPERATION()
        data = execute_linstor_cmd('linstor --no-color --no-utf8 r lv')
        linstorlv = Linstor.refine_linstor(data)
        disks = {}
        for d in linstorlv:
            disks.update({d[1]: d[5]})
        js.update_data('Disk', disks)
        if disk == 'all' or disk is None:
            print(" " + "{:<15}".format("Diskname") + "Path")
            print(" " + "{:<15}".format("---------------") + "---------------")
            for k in disks:
                output = (" " + "{:<15}".format(k) + disks[k])
                print(output)
        else:
            if js.check_key('Disk', disk):
                output = (disk, ":", js.get_data('Disk').get(disk))
                print(output)
            else:
                print("Fail! Can't find " + disk)


    def create_host(self,host, iqn):
        js = iscsi_json.JSON_OPERATION()
        print("Host name:", host)
        print("iqn:", iqn)
        if js.check_key('Host', host):
            print("Fail! The Host " + host + " already existed.")
            return False
        else:
            js.add_data("Host", host, iqn)
            print("Create success!")
            return True

    def show_host(self,host):
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
        # print("Diskgroup name:", diskgroup)
        # print("Disk name:", disk)
        if js.check_key('DiskGroup', diskgroup):
            print(
                "Fail! The DiskGroup " +
                diskgroup +
                " already existed.")
            return False
        else:
            t = True
            for i in disk:
                if js.check_key('Disk', i) == False:
                    t = False
                    print("Fail! Can't find " + i)
            if t:
                js.add_data('DiskGroup', diskgroup, disk)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")
                return False

    def show_diskgroup(self,dg):
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
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
                js.add_data('HostGroup', hostgroup, host)
                print("Create success!")
                return True
            else:
                print("Fail! Please give the true name.")
                return False

    def show_hostgroup(self,hg):
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()
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
                self.map_crm_c_(hg,dg)


    def show_map(self,map):
        js = iscsi_json.JSON_OPERATION()
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
        js = iscsi_json.JSON_OPERATION()

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