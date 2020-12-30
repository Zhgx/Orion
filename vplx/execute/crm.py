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


    def get_crm_conf(self):
        cmd = 'crm configure show | cat'
        result = execute_crm_cmd(cmd)
        if result:
            return result['rst']
        else:
            s.handle_exception()

    def get_resource_data(self):
        # 用来匹配的原数据，allowed_initiators=""，有时有双引号，有时候没有，无法确定，然后多个iqn是怎么样的
        re_logical = re.compile(
            r'primitive (\w*) iSCSILogicalUnit \\\s\tparams\starget_iqn="([a-zA-Z0-9.:-]*)"\simplementation=lio-t\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators="?([a-zA-Z0-9.: -]+)"?[\s\S.]*?meta target-role=(\w*)')
        result = s.re_findall(re_logical, self.crm_conf_data)
        return result

    # [name, IP, netmask]
    def get_vip(self):
        re_vip = re.compile(
            r'primitive\s(\S+)\sIPaddr2.*\s*params\sip=([0-9.]+)\scidr_netmask=(\d+)')
        result = s.re_findall(re_vip, self.crm_conf_data)
        data = {}
        return result

    # [('p_iscsi_portblock_off', '192.168.7.5', '3260', 'unblock'),]
    def get_portblock(string):
        re_portblock = re.compile(
            r'primitive\s(\S+)\sportblock.*\s*params\sip=([0-9.]+)\sportno=(\d+).*action=(\w+)')
        result = re_portblock.findall(string)
        return result


    #[('vip', '10.203.1.75', '24')]
    #[('t_test', 'iqn.2020-04.feixitek.com:versaplx00', '10.203.1.75', '3260')]

    # [name, target IQN, VIP, port]
    def get_target(self):
        re_target = re.compile(
            r'primitive\s(\S+)\siSCSITarget.*\s*params\siqn="(\S+)"\s.*portals="([0-9.]+):(\d+)"')
        result = s.re_findall(re_target, self.crm_conf_data)
        print(result)
        return result

    # def get_vip_data(self):
    #     re_vip = re.compile(
    #         r'primitive\s(\w*)\sIPaddr2\s\\\s*\w*\sip=([0-9.]*)\s\w*=(\d*)\s')
    #     result = s.re_findall(re_vip, self.crm_conf_data)
    #     return result
    #
    # def get_target_data(self):
    #     re_target = re.compile(
    #         r'primitive\s(\w*)\s\w*\s\\\s*params\siqn="([a-zA-Z0-9.:-]*)"\s[a-z=-]*\sportals="([0-9.]*):\d*"\s\\')
    #     result = s.re_findall(re_target, self.crm_conf_data)
    #     return result

    # 获取并更新crm信息
    def update_crm_conf(self):
        # crm_config_status = obj_crm.get_crm_data()
        if 'ERROR' in self.crm_conf_data:
            s.prt_log("Could not perform requested operations, are you root?",1)
        else:
            js = iscsi_json.JsonOperation()
            # res = self.get_resource_data()
            vip = self.get_vip()
            target = self.get_target()
            js.update_crm_conf(vip, target)
            return True

    def check_crm_conf(self):
        # 不允许ipaddr2,portblock单独存在，进行检查
        # 验证规则：找到ip，匹配是否有对应ip的portblock组（2个，block+unblock）
        vip = self.get_vip()
        vip = {'vip1':{'ip':'10.203.1.2'},'vip2':{'ip':'10.203.1.1'}}
        target = self.get_target()
        plock = {'_on':{'ip':'10.203.1.2','port':'3260','type':'block'},'_off':{'ip':'10.203.1.2','port':'3260','type':'unblock'}}
        #plock
        # 测试创建block，用一样的ip，不一样的端口，一样的端口，stderr和stdout

        # 考虑错误时的数据，哪里的数据不对？

        dict_err = {}
        for vip,vip_data in vip.items():
            for plock,plock_data in plock.items():
                plock_num = 0
                if vip_data['ip'] == plock_data['ip']:
                    plock_data +=1

                if plock_num !=2:
                    return False




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

    # 通过 crm st 获取resource状态
    def get_res_status(self, crm_res):
        cmd = f'crm res list | grep {crm_res}'
        result = execute_crm_cmd(cmd)
        if 'Started' in result['rst']:
            return True
        elif 'Stopped' in result['rst']:
            return False
        else:
            pass

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

    def check_crm_res(self, crm_res, type):
        # 可替换掉get_res_status，这个比较严谨
        if type == 'ipaddr2':
            re_ = f'{crm_res}\s*\(ocf::heartbeat:IPaddr2\):\s*(\w*)'
        elif type == 'target':
            re_ = f'{crm_res}\s*\(ocf::heartbeat:iSCSITarget\):\s*(\w*)'
        else:
            # 抛出参数异常
            raise TypeError('type参数输入错误:ipaddr2/target')

        cmd_result = execute_crm_cmd(f'crm res list | grep {crm_res}')
        re_status = re.compile(re_)
        status = re_status.search(cmd_result['rst'])
        if status:
            if status.groups()[0] == 'Started':
                return True
            else:
                return False
        else:
            return None

    # 多次通过 crm st 检查resource状态，状态为started时返回True，检查5次都为stopped 则返回None
    def checkout_status_start(self, res):
        n = 0
        while n < 5:
            n += 1
            if self.get_res_status(res):
                s.prt_log(f'the resource {res} is Started', 0)
                return True
            else:
                time.sleep(1)
        s.prt_log(f'the resource {res} is Stopped', 1)

    # 多次通过 crm st 检查resource状态，状态为stop时返回True，检查5次都不为stopped 则返回None
    def checkout_status_stop(self, res):
        n = 0
        while n < 5:
            n += 1
            if self.get_res_status(res) == False:
                s.prt_log(f'the resource {res} is Stopped', 0)
                return True
            else:
                time.sleep(1)
        s.prt_log(f"the resource {res} can't Stopped", 1)

    # 停用res
    def stop_res(self, res):
        cmd = f'crm res stop {res}'
        result = execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            s.prt_log("crm res stop fail",1)

    # 删除resource步骤
    def delete_res(self, res):
        if self.stop_res(res):
            if self.checkout_status_stop(res):
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
            re_str = re.compile(rf'INFO: hanging colocation:co_{res} deleted\nINFO: hanging order:or_{res} deleted\n')
            if s.re_search(re_str, output):
                s.prt_log(f"delete colocation:co_{res}, order:or_{res} success", 0)
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


#
# class Portal():
#     def __init__(self):
#         self.dict_rollback = {}
#
#     def create(self, name, ip, port=3260 ,netmask=24):
#         if not self._check_name(name):
#             print(f'{name}不符合规范')
#             return
#         if not self._check_IP(ip):
#             print(f'{ip}不符合规范')
#             return
#         if not self._check_port(port):
#             print(f'{port}不符合规范，范围：3260-65535')
#             return
#         if not self._check_netmask(netmask):
#             print(f'{netmask}不符合规范，范围：0-32')
#             return
#
#         try:
#             obj_ipadrr = Ipadrr2()
#             obj_ipadrr.create(name,ip,netmask)
#             self.dict_rollback.update({'create_ipaddr2':name})
#
#             obj_portblock = PortBlockGroup()
#             obj_portblock.create(f'{name}_prtblk_on',ip,port,action='block')
#             self.dict_rollback.update({'create_block':f'{name}_prtblk_on'})
#             obj_portblock.create(f'{name}_prtblk_off',ip,port,action='unblock')
#             self.dict_rollback.update({'create_unblock': f'{name}_prtblk_off'})
#
#             obj_colocation = Colocation()
#             obj_colocation.create(f'col_{name}_prtblk_on',f'{name}_prtblk_on', name)
#             obj_colocation.create(f'col_{name}_prtblk_off', f'{name}_prtblk_off', name)
#
#             obj_order = Order()
#             obj_order.create(f'or_{name}_prtblk_on',name, f'{name}_prtblk_on')
#
#         except Exception as ex:
#             # 记录异常信息
#             # self.logger.write_to_log('DATA', 'DEBUG', 'exception', '', str(traceback.format_exc()))
#             # 回滚
#             # 执行顺序有没有要求？
#             print('进行回滚操作')
#             for operation,res in self.dict_rollback.items():
#                 if operation == 'create_block' or 'create_unblock':
#                     obj_portblock.delete(res)
#                 elif operation == 'create_ipaddr2':
#                     obj_ipadrr.delete(res)
#
#         # 验证
#         status = self._check_status(name)
#
#         if status == 'OK':
#             self.js = iscsi_json.JsonOperation
#             self.js.update_data('Portal', name, {'ip': ip, 'port': port,'netmask':netmask,'target':[]})
#         elif status == 'NETWORK_ERROR':
#             obj_ipadrr.delete(name)
#             obj_portblock.delete(f'{name}_prtblk_on')
#             obj_portblock.delete(f'{name}_prtblk_off')
#             s.prt_log('由于设置的IP地址网段有误或有其他网络问题，此portal无法正常创建，请重新配置', 1)
#
#
#
#
#
#     def delete(self, name):
#         pass
#
#
#     def modify(self, name, ip, port):
#         pass
#
#
#     def show(self):
#         pass
#
#
#     def _check_name(self, name):
#         re_name = re.compile(r'^[a-zA-Z]\w*$')
#         result = re_name.match(name)
#         # 添加从JSON中验证这个Name有没有被portal使用
#         return True if result else False
#
#     def _check_IP(self, ip):
#         re_ip = re.compile(
#             r'^((2([0-4]\d|5[0-5]))|[1-9]?\d|1\d{2})(\.((2([0-4]\d|5[0-5]))|[1-9]?\d|1\d{2})){3}$')
#         result = re_ip.match(ip)
#         # 添加从JSON中验证这个IP有没有被portal使用
#         return True if result else False
#
#     def _check_port(self, port):
#         if not isinstance(port,int):
#             return False
#         return True if 3260<=port<=65535 else False
#
#     def _check_netmask(self, netmask):
#         if not isinstance(netmask, int):
#             return False
#         return True if 0 <= netmask <= 32 else False
#
#     def _check_status(self, name):
#         """
#
#         :param name: portal name
#         :return:
#         """
#         obj_crm = CRMConfig()
#         status = obj_crm.check_crm_res(name, type='ipaddr2')
#         if status is True:
#             s.prt_log('创建成功',1)
#             return 'OK'
#         elif status is False:
#             failed_actions = obj_crm.get_failed_actions(name)
#             if failed_actions == 0:
#                 return 'NETWORK_ERROR'
#             elif failed_actions:
#                 s.prt_log(failed_actions,1)
#                 return 'OTHER_ERROR'
#             else:
#                 s.prt_log('未知错误,请进行检查',1)
#                 return 'UNKNOWN_ERROR'
#         else:
#             s.prt_log(f'{name}没有被成功创建，请检查',1)
#             return 'FAIL'




class Ipaddr2():
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
        result = obj_crm.delete_res(name)
        if not result:
            raise consts.CmdError
        else:
            print('删除ipaddr2成功')




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
        result = obj_crm.delete_res(name)
        if not result:
            raise consts.CmdError
        else:
            print(f'删除{name}成功')


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












