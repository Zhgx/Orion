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


class RollBack():
    """
    装饰器，记录执行进行操作CRM资源名，提供方法rollback可以回滚执行操作的操作
    """
    dict_rollback = {'IPaddr2':{}, 'PortBlockGroup':{} , 'ISCSITarget':{}}
    def __init__(self, func):
        self.func = func
        self.type,self.oprt = func.__qualname__.split('.')

    def __call__(self, *args, **kwargs):
        if self.func(self, *args, **kwargs):
            self.dict_rollback[self.type].update({args[0]:self.oprt})

    @classmethod
    def rollback(cls,ip,port,netmask):
        # 目前只用于Portal的回滚，之后Target的回滚可以根据需要增加一个判断类型的参数
        print("程序中途错误，开始进行资源回滚")
        print("需要回滚的资源：",cls.dict_rollback)
        cls.rb_ipaddr2(cls,ip,port,netmask)
        cls.rb_block(cls,ip,port,netmask)
        cls.rb_target(cls,ip,port,netmask)
        print("回滚结束")

    # 回滚完之后考虑做一个对crm配置的检查？跟name相关的资源如果还存在，进行提示？

    def rb_ipaddr2(self,ip,port,netmask):
        if self.dict_rollback['IPaddr2']:
            obj_ipaddr2 = IPaddr2()
            # 实际上应该不可能需要循环
            for name, oprt in self.dict_rollback['IPaddr2'].items():
                if oprt == 'create':
                    obj_ipaddr2.delete(name)
                elif oprt == 'delete':
                    obj_ipaddr2.create(name,ip,netmask)
                elif oprt == 'modify':
                    obj_ipaddr2.modify(name,ip)


    def rb_block(self,ip,port,netmask):
        if self.dict_rollback['PortBlockGroup']:
            obj_block = PortBlockGroup()
            for name,oprt in self.dict_rollback['PortBlockGroup'].items():
                if oprt == 'create':
                    obj_block.delete(name)
                elif oprt == 'delete':
                    action = 'block'
                    if name.split('_')[2] == 'off':
                        action = 'unblock'
                    obj_block.create(name,ip,port,action)
                elif oprt == 'modify':
                    obj_block.modify(name,ip,port)


    def rb_target(self,ip,port,netmask):
        if self.dict_rollback['ISCSITarget']:
            obj_target = ISCSITarget()
            for name,oprt in self.dict_rollback['ISCSITarget'].items():
                if oprt == 'modify':
                    obj_target.modify(name,ip,port)


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

        for vip_name,vip_data in list(vip.items()):
            dict_portal.update({vip_name:{'status':'ERROR'}}) #error/normal
            for pb_name,pb_data in list(portblock.items()):
                if vip_data['ip'] == pb_data['ip']:
                    dict_portal[vip_name].update({pb_name:pb_data['type']})
                    del portblock[pb_name]
            if len(dict_portal[vip_name]) == 3:
                if 'block' and 'unblock' in dict_portal[vip_name].values():
                    dict_portal[vip_name]['status'] = 'NORMAL'
        if portblock:
            s.prt_log(f'{",".join(portblock.keys())}没有对应的VIP，请进行处理',2)
        list_portal = [] # portal如果没有block和unblock，则会加进这个列表

        for portal_name,portal_data in list(dict_portal.items()):
            if portal_data['status'] == 'ERROR':
                list_portal.append(portal_name)
        if list_portal:
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

    def check(self):
        """
        进行Portal/iSCSITarget的创建时候，需要进行的所有检查，不通过则中断程序
        :return: None
        """
        vip = self.get_vip()
        portblock = self.get_portblock()
        target = self.get_target()
        self.check_portal_component(vip,portblock)
        self.check_env_sync(vip,portblock,target)


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


    def get_failed_actions(self, res):
        # 检查crm整体状态，但是目前好像只是用于提取vip的错误信息
        exitreason = None
        cmd_result = execute_crm_cmd('crm st | cat')
        re_error = re.compile(
            f"\*\s({res})\w*\son\s(\S*)\s'(.*)'\s.*exitreason='(.*)',")
        result = re_error.findall(cmd_result)
        if result:
            if result[0][3] == '[findif] failed':
                exitreason = 0
            else:
                exitreason = result
        return exitreason

    def get_crm_res_status(self, res, type):
        """
        获取crm res的状态
        :param res:
        :param type:
        :return: string
        """
        if not type in ['IPaddr2','iSCSITarget','portblock','iSCSILogicalUnit']:
            raise ValueError('参数type传入有误，必须为IPaddr2,iSCSITarget,portblock,iSCSILogicalUnit其中一个')

        cmd_result = execute_crm_cmd(f'crm res list | grep {res}')
        re_status = f'{res}\s*\(ocf::heartbeat:{type}\):\s*(\w*)'
        status = s.re_search(re_status,cmd_result['rst'],output_type='groups')
        if status:
            if status[0] == 'Started':
                return 'STARTED'
            else:
                return 'NOT_STARTED'

    def checkout_status(self, res, type, expect_status, times=5):
        """
        检查crm res的状态
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


    def stop_res(self, res):
        # 执行停用res
        cmd = f'crm res stop {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            s.prt_log(f"Stop {res} fail",1)


    def execute_delete(self, res):
        # 执行删除res
        cmd = f'crm conf del {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log(f"Delete {res} success", 0)
            return True
        else:
            output = result['rst']
            re_str = re.compile(rf'INFO: hanging colocation:.*? deleted\nINFO: hanging order:.*? deleted\n')
            if s.re_search(re_str, output):
                s.prt_log(f"Delete {res} success(including colocation and order)", 0)
                return True
            else:
                return False

    #
    def delete_res(self, res, type):
        # 删除一个crm res，完整的流程
        if self.stop_res(res):
            if self.checkout_status(res,type,'NOT_STARTED'):
                if self.execute_delete(res):
                    return True
        s.prt_log(f"Delete {res} fail",1)

    # 创建resource相关配置，no
    def create_set(self, res, target):
        if self.create_col(res, target):
            if self.create_order(res, target):
                s.prt_log(f'create colocation:co_{res}, order:or_{res} success', 0)
                return True
            else:
                s.prt_log("create order fail", 1)
        else:
            s.prt_log("create colocation fail", 1)

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

    @RollBack
    def create(self,name,ip,netmask):
        cmd = f'crm cof primitive {name} IPaddr2 params ip={ip} cidr_netmask={netmask}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print('创建ipaddr2成功')
            return True

    @RollBack
    def delete(self,name):
        obj_crm = CRMConfig()
        result = obj_crm.delete_res(name,type='IPaddr2')
        if not result:
            raise consts.CmdError
        else:
            print('删除ipaddr2成功')
            return True

    @RollBack
    def modify(self,name,ip):
        cmd = f'crm cof set {name}.ip {ip}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            # 创建失败，输出原命令报错信息
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print('修改IPaddr2的IP成功')
            return True



class PortBlockGroup():
    # 需不需要block的限制关系？创建完block之后才能创建unblock？
    def __init__(self):
        self.block = None
        self.unblock = None

    @RollBack
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
            print(f'创建 {name} 成功')
            return True


    @RollBack
    def delete(self,name):
        obj_crm = CRMConfig()
        result = obj_crm.delete_res(name,type='portblock')
        if not result:
            raise consts.CmdError
        else:
            print(f'删除 {name} 成功')
            return True


    @RollBack
    def modify(self,name,ip,port):
        cmd_ip = f'crm cof set {name}.ip {ip}'
        cmd_port = f'crm cof set {name}.portno {port}'
        cmd_result_ip = execute_crm_cmd(cmd_ip)
        cmd_result_port = execute_crm_cmd(cmd_port)
        if not cmd_result_ip['sts'] or not cmd_result_port['sts']:
            s.prt_log(cmd_result_ip['rst'],1)
            s.prt_log(cmd_result_port['rst'], 1)
            raise consts.CmdError
        else:
            print(f'修改 {name} IP和Port成功')
            return True



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
            return True



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
            return True



class ISCSITarget():
    def __init__(self):
        pass

    @RollBack
    def modify(self,name,ip,port):
        print('开始修改iSCSITarget')

        cmd = f'crm cof set {name}.portals {ip}:{port}'
        cmd_result = execute_crm_cmd(cmd)
        if not cmd_result['sts']:
            s.prt_log(cmd_result['rst'],1)
            raise consts.CmdError
        else:
            print(f'修改 {name} 成功')
            return True



# class ISCSILogicalUnit():
#     def __init__(self):
#         pass
#
#
#
#     def create_crm_res(self,res,target):
#         pass
#
#
#
#     def create_crm_res(self, res, target_iqn, lunid, path, initiator):
#         cmd = f'crm conf primitive {res} iSCSILogicalUnit params ' \
#             f'target_iqn="{target_iqn}" ' \
#             f'implementation=lio-t ' \
#             f'lun={lunid} ' \
#             f'path={path} ' \
#             f'allowed_initiators="{initiator}" ' \
#             f'op start timeout=40 interval=0 ' \
#             f'op stop timeout=40 interval=0 ' \
#             f'op monitor timeout=40 interval=15 ' \
#             f'meta target-role=Stopped'
#         result = execute_crm_cmd(cmd)
#         if result['sts']:
#             s.prt_log("create iSCSILogicalUnit success",0)
#             return True
#
#
#     def create(self,name,target):
#         pass
#
#
#     def create_set(self, res, target):
#         if self.create_col(res, target):
#             if self.create_order(res, target):
#                 s.prt_log(f'create colocation:co_{res}, order:or_{res} success', 0)
#                 return True
#             else:
#                 s.prt_log("create order fail", 1)
#         else:
#             s.prt_log("create colocation fail", 1)
#
#     def create_col(self, res, target):
#         cmd = f'crm conf colocation co_{res} inf: {res} {target}'
#         result = execute_crm_cmd(cmd)
#         if result['sts']:
#             s.prt_log("set coclocation success",0)
#             return True
#
#     def create_order(self, res, target):
#         cmd = f'crm conf order or_{res} {target} {res}'
#         result = execute_crm_cmd(cmd)
#         if result['sts']:
#             s.prt_log("set order success",0)
#             return True
#
#     def create_res(self, res, list_iqn):
#         obj_crm = CRMConfig()
#         # 取DeviceName后四位数字，减一千作为lun id
#         path = self.js.get_data('Disk')[res]
#         lunid = int(path[-4:]) - 1000
#         initiator = ' '.join(list_iqn)
#         # 创建iSCSILogicalUnit
#         if obj_crm.create_crm_res(res, self.target_iqn, lunid, path, initiator):
#             self.list_res_created.append(res)
#             # 创建order，colocation
#             if obj_crm.create_set(res, self.target_name):
#                 # 尝试启动资源，成功失败都不影响创建
#                 obj_crm.start_res(res)
#                 obj_crm.checkout_status(res,'iSCSILogicalUnit','STARTED')
#             else:
#                 for i in self.list_res_created:
#                     obj_crm.delete_res(i,'iSCSILogicalUnit')
#                 return False
#         else:
#             s.prt_log('Fail to create iSCSILogicalUnit', 1)
#             for i in self.list_res_created:
#                 obj_crm.delete_res(i,'iSCSILogicalUnit')
#             return False













