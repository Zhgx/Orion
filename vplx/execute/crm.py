# coding=utf-8
import re
import time
import iscsi_json
import sundry as s
import subprocess
import consts

@s.deco_cmd('crm')
def execute_crm_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    output = None
    while True:
        if p.poll() is not None:
            break
        if p.stderr:
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
    elif len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
    elif out == b'':  # 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}

    if output:
        return output
    else:
        s.handle_exception()

class CRMData():
    def __init__(self):
        self.crm_conf_data = self.get_crm_conf()
        self.vip = None
        self.portblock = None
        self.target = None
        if 'ERROR' in self.crm_conf_data:
            s.prt_log("Could not perform requested operations, are you root?",2)

    def get_crm_conf(self):
        cmd = 'crm configure show | cat'
        result = execute_crm_cmd(cmd)
        if result:
            return result['rst']
        else:
            s.handle_exception()

    # def get_resource_data(self):
    #     # 用来匹配的原数据，allowed_initiators=""，有时有双引号，有时候没有，无法确定，然后多个iqn是怎么样的
    #     re_logical = re.compile(
    #         r'primitive (\w*) iSCSILogicalUnit \\\s\tparams\starget_iqn="([a-zA-Z0-9.:-]*)"\simplementation=lio-t\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators="?([a-zA-Z0-9.: -]+)"?[\s\S.]*?meta target-role=(\w*)')
    #     result = s.re_findall(re_logical, self.crm_conf_data)
    #     return result

    def get_vip(self):
        re_vip = re.compile(
            r'primitive\s(\S+)\sIPaddr2.*\s*params\sip=([0-9.]+)\scidr_netmask=(\d+)')
        result = s.re_findall(re_vip, self.crm_conf_data)
        dict_vip = {}
        for vip in result:
            dict_vip.update({vip[0]:{'ip':vip[1],'netmask':vip[2]}})
        self.vip = dict_vip
        return dict_vip

    def get_portblock(self):
        re_portblock = re.compile(
            r'primitive\s(\S+)\sportblock.*\s*params\sip=([0-9.]+)\sportno=(\d+).*action=(\w+)')
        result = s.re_findall(re_portblock,self.crm_conf_data)
        dict_portblock = {}
        for portblock in result:
            dict_portblock.update({portblock[0]:{'ip':portblock[1],'port':portblock[2],'type':portblock[3]}})
        self.portblock = dict_portblock
        return dict_portblock

    def get_target(self):
        re_target = re.compile(
            r'primitive\s(\S+)\siSCSITarget.*\s*params\siqn="(\S+)"\s.*portals="([0-9.]+):(\d+)"')
        result = s.re_findall(re_target, self.crm_conf_data)
        dict_target = {}
        for target in result:
            dict_target.update({target[0]:{'target_iqn':target[1],'ip':target[2],'port':target[3]}})
        self.target = dict_target
        return dict_target

    def get_portal_data(self,vip_all,portblock_all,target_all):
        """
        获取现在CRM的环境下所有Portal的数据，
        :param vip_all: 目前CRM环境的所有vip数据
        :param portblock_all:目前CRM环境下的所有portblock数据
        :param target_all: 目前CRM环境下的所有target数据
        :return:
        """
        dict_portal = {}
        for vip in vip_all:
            dict_portal.update(
                {vip: {'ip': vip_all[vip]['ip'], 'port': '', 'netmask': vip_all[vip]['netmask'], 'target': []}})
            for portblock in portblock_all:
                if portblock_all[portblock]['ip'] == vip_all[vip]['ip']:
                    dict_portal[vip]['port'] = portblock_all[portblock]['port']
                    continue

            for target in target_all:
                if target_all[target]['ip'] == vip_all[vip]['ip']:
                    dict_portal[vip]['target'].append(target)

        return dict_portal



    def check_portal_component(self,vip,portblock):
        """
        对目前环境的portal组件(ipaddr,portblock）的检查，需满足：
        1.不存在单独的portblock
        2.已存在的ipaddr，必须有对应的portblock组（block，unblock）
        不满足条件时提示并退出
        :param vip_all: dict
        :param portblock_all: dict
        :return:None
        """
        dict_portal = {}
        for vip_name,vip_data in vip.items():
            dict_portal.update({vip_name:{},'status':'ERROR'}) #error/normal
            for pb_name,pb_data in portblock.items():
                if vip_data['ip'] == pb_data['ip']:
                    dict_portal[vip_name].update({pb_name:pb_data['type']})
                    del portblock[pb_name]
            if len(dict_portal[vip_name]) == 2:
                if 'block' and 'unblock' in dict_portal[vip_name].values():
                    dict_portal['status'] = 'NORMAL'
        if not portblock:
            s.prt_log(f'{",".join(portblock.keys())}没有对应的VIP，请进行处理',2)
        list_portal = [] # portal如果没有block和unblock，则会加进这个列表
        for portal_name,portal_data in dict_portal.items():
            if portal_data['status'] == 'ERROR':
                list_portal.append(portal_name)
        if not list_portal:
            s.prt_log(f'{",".join(list_portal)}这些portal无法正常使用，请进行处理',2)


    def check_env_sync(self,vip,portblock,target):
        """
        检查CRM环境与JSON配置文件所记录的Portal、Target的数据是否一致，不一致提示后退出
        :param vip_all:目前CRM环境的vip数据
        :param target_all:目前CRM环境的target数据
        :return:
        """
        js = iscsi_json.JsonOperation()
        crm_portal = self.get_portal_data(vip,portblock,target)
        json_portal = js.json_data['Portal']

        # 处理列表的顺序问题
        for portal_name,portal_data in crm_portal.items():
            portal_data['target'] = set(portal_data['target'])

        for portal_name,portal_data in json_portal.items():
            portal_data['target'] = set(portal_data['target'])


        if not crm_portal == json_portal:
            s.prt_log('Portal数据不一致，请检查后重试',2)
        if not target == js.json_data['Target']:
            s.prt_log('iSCSITarget数据不一致,请检查后重试',2)


class CRMConfig():
    def __init__(self):
        pass

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
            s.prt_log("create iSCSILogicalUnit success",0)
            return True

    # # 通过 crm st 获取resource状态
    # def get_res_status(self, crm_res):
    #     cmd = f'crm res list | grep {crm_res}'
    #     result = execute_crm_cmd(cmd)
    #     if 'Started' in result['rst']:
    #         return True
    #     elif 'Stopped' in result['rst']:
    #         return False
    #     else:
    #         pass

    def get_failed_actions(self, crm_res):
        # 检查crm整体状态，但是目前好像只是用于提取vip的错误信息
        exitreason = None
        cmd_result = execute_crm_cmd('crm st | cat')
        re_error = re.compile(
            f"\*\s({crm_res})\w*\son\s(\S*)\s'(.*)'\s.*exitreason='(.*)',")
        result = re_error.findall(cmd_result)
        if result:
            if result[0][3] == '[findif] failed':
                exitreason = 0
            else:
                exitreason = result
        return exitreason

    def get_crm_res_status(self, crm_res, type):
        if not type in ['IPaddr2','iSCSITarget','portblock','iSCSILogicalUnit']:
            raise ValueError('参数type传入有误，必须为IPaddr2,iSCSITarget,portblock,iSCSILogicalUnit其中一个')

        cmd_result = execute_crm_cmd(f'crm res list | grep {crm_res}')
        re_status = f'{crm_res}\s*\(ocf::heartbeat:{type}\):\s*(\w*)'
        status = s.re_search(re_status,cmd_result['rst'],output_type='groups')
        if status:
            if status[0] == 'Started':
                return 'STARTED'
            else:
                return 'NOT_STARTED'

    def checkout_status(self, res, type, expect_status, times=5):
        """
        检查res的状态
        :param res: 需要检查的资源
        :param type_res: 需要检查的资源类型
        :param times: 需要检查的次数
        :param expect_status: 预期状态
        :return: 返回True则说明是预期效果
        """
        n = 0
        while n < times:
            n += 1
            if self.get_crm_res_status(res,type) == expect_status:
                s.prt_log(f'The status of {res} is {expect_status} now.',0)
                return True
            else:
                time.sleep(1)
        else:
            s.prt_log("Does not meet expectations, please try again.", 1)


    # # 多次通过 crm st 检查resource状态，状态为started时返回True，检查5次都为stopped 则返回None
    # def checkout_status_start(self, res):
    #     n = 0
    #     while n < 5:
    #         n += 1
    #         if self.get_res_status(res):
    #             s.prt_log(f'the resource {res} is Started', 0)
    #             return True
    #         else:
    #             time.sleep(1)
    #     s.prt_log(f'the resource {res} is Stopped', 1)
    #
    # # 多次通过 crm st 检查resource状态，状态为stop时返回True，检查5次都不为stopped 则返回None
    # def checkout_status_stop(self, res):
    #     n = 0
    #     while n < 5:
    #         n += 1
    #         if self.get_res_status(res) == False:
    #             s.prt_log(f'the resource {res} is Stopped', 0)
    #             return True
    #         else:
    #             time.sleep(1)
    #     s.prt_log(f"the resource {res} can't Stopped", 1)

    # 停用res
    def stop_res(self, res):
        cmd = f'crm res stop {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            s.prt_log("crm res stop fail",1)

    # 删除resource步骤
    def delete_res(self, res, type):
        if self.stop_res(res):
            if self.checkout_status(res,type,'NOT_STARTED'):
                if self.delete_conf_res(res):
                    return True
        s.prt_log(f"{res} delete fail",1)

    # 创建resource相关配置
    def create_set(self, res, target):
        if self.create_col(res, target):
            if self.create_order(res, target):
                s.prt_log(f'create colocation:co_{res}, order:or_{res} success', 0)
                return True
            else:
                s.prt_log("create order fail", 1)
        else:
            s.prt_log("create colocation fail", 1)

    # 执行crm命令删除resource的配置
    def delete_conf_res(self, res):
        cmd = f'crm conf del {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log(f"delete resource success: {res}", 0)
            return True
        else:
            output = result['rst']
            re_str = re.compile(rf'INFO: hanging colocation:.*? deleted\nINFO: hanging order:.*? deleted\n')
            if s.re_search(re_str, output):
                s.prt_log(output, 0)
                return True
            else:
                s.prt_log(f"delete resource fail", 1)
                return False

    def create_col(self, res, target):
        cmd = f'crm conf colocation co_{res} inf: {res} {target}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("set coclocation success",0)
            return True

    def create_order(self, res, target):
        cmd = f'crm conf order or_{res} {target} {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("set order success",0)
            return True

    def start_res(self, res):
        s.prt_log(f"try to start {res}", 0)
        cmd = f'crm res start {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True

    # 刷新recourse状态，后续会用到
    def refresh(self):
        cmd = f'crm resource refresh'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("refresh",0)
            return True

    def change_initiator(self, res, iqns):
        iqns = ' '.join(iqns)
        cmd = f"crm config set {res}.allowed_initiators \"{iqns}\""
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log(f"Change {res} allowed_initiators success!",0)
            return True




class IPaddr2():
    def __init__(self):
        pass

    def create(self,name,ip,netmask):
        cmd = f'crm cof primitive {name} IPaddr2 params ip={ip} cidr_netmask={netmask}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print('创建ipaddr2成功')

    def delete(self,name):
        obj_crm = CRMConfig()
        result = obj_crm.delete_res(name,type='IPaddr2')
        if not result:
            raise consts.CmdError
        else:
            print('删除ipaddr2成功')


    def modify(self,name,ip):
        cmd = f'crm cof set {name}.ip {ip}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print('修改IPaddr2的IP成功')





class PortBlockGroup():
    # 需不需要block的限制关系？创建完block之后才能创建unblock？
    def __init__(self):
        self.block = None
        self.unblock = None

    def create(self,name,ip,port,action):
        """

        :param name:
        :param ip:
        :param port:
        :param action: block/unblock
        :return:
        """
        if not action in ['block','unblock']:
            raise TypeError('action参数输入错误：block/unblock')

        cmd = f'crm cof primitive {name} portblock params ip={ip} portno={port} protocol=tcp action={action} op monitor timeout=20 interval=20'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'创建{name}成功')


    def delete(self,name):
        obj_crm = CRMConfig()
        result = obj_crm.delete_res(name,type='portblock')
        if not result:
            raise consts.CmdError
        else:
            print(f'删除{name}成功')


    def modify_ip(self,name,ip):
        cmd = f'crm cof set {name}.ip {ip}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'修改{name}IP成功')

    def modify_port(self,name,port):
        cmd = f'crm cof set {name}.portno {port}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'修改{name}port成功')


class Colocation():
    def __init__(self):
        self.dict_rollback = consts.glo_rollback()

    def create(self,name,target1,target2):
        cmd = f'crm cof colocation {name} inf: {target1} {target2}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'创建{name}成功')



class Order():
    def __init__(self):
        pass


    def create(self,name, target1 ,target2):
        cmd = f'crm cof order {name} {target1} {target2}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'创建{name}成功')




class ISCSITarget():
    def __init__(self):
        pass


    def modify(self,name,ip,port):
        print('开始修改iSCSITarget')

        cmd = f'crm cof set {name}.portals {ip}:{port}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'修改{name}成功')










