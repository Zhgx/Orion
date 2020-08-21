# coding=utf-8
import re
import time
import iscsi_json
import consts
import sundry as s
import sys



class CRMData():
    def __init__(self):
        self.crm_conf_data = self.get_crm_conf()

    def get_crm_conf(self):
        cmd = 'crm configure show'
        result = s.execute_crm_cmd(cmd)
        if result:
            return result['rst']

    def get_resource_data(self):
        # 用来匹配的原数据，allowed_initiators=""，有时有双引号，有时候没有，无法确定，然后多个iqn是怎么样的
        re_logical = re.compile(
            r'primitive (\w*) iSCSILogicalUnit \\\s\tparams\starget_iqn="([a-zA-Z0-9.:-]*)"\simplementation=lio-t\slun=(\d*)\spath="([a-zA-Z0-9/]*)"\sallowed_initiators=([a-zA-Z0-9.: -]+)[\s\S.]*?meta target-role=(\w*)')
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
            s.prt_log("Could not perform requested operations, are you root?",1)
        else:
            js = iscsi_json.JSON_OPERATION()
            res = self.get_resource_data()
            vip = self.get_vip_data()
            target = self.get_target_data()
            js.update_crm_conf(res, vip, target)
            return True


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
        result = s.execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("Create iSCSILogicalUnit success",0)
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
        result = s.execute_crm_cmd(cmd)
        if result['sts']:
            return True
        else:
            s.prt_log("crm res stop fail",1)


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
            s.prt_log("Does not meet expectations, please try again.",1)

    def delete_crm_res(self, res):
        # crm res stop <LUN_NAME>
        if self.stop_res(res):
            if self.checkout_status(res,10,'Stopped'):
                time.sleep(3)
                cmd = f'crm conf del {res}'
                result = s.execute_crm_cmd(cmd)
                if result:
                    output = result['rst']
                    re_str = re.compile(rf'INFO: hanging colocation:co_{res} deleted\nINFO: hanging order:or_{res} deleted\n')
                    if s.re_search(re_str,output):
                        s.prt_log(f"crm conf del {res}",0)
                        return True
                    else:
                        s.prt_log(f"crm delete fail",1)

    def create_col(self, res, target):
        # crm conf colocation <COLOCATION_NAME> inf: <LUN_NAME> <TARGET_NAME>
        cmd = f'crm conf colocation co_{res} inf: {res} {target}'
        result = s.execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("set coclocation success",0)
            return True

    def create_order(self, res, target):
        # crm conf order <ORDER_NAME1> <TARGET_NAME> <LUN_NAME>
        cmd = f'crm conf order or_{res} {target} {res}'
        result = s.execute_crm_cmd(cmd)
        if result['sts']:
            s.prt_log("set order success",0)
            return True

    def start_res(self, res):
        # crm res start <LUN_NAME>
        cmd = f'crm res start {res}'
        result = s.execute_crm_cmd(cmd)
        if result['sts']:
            return True
