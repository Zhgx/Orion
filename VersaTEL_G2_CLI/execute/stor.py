# coding=utf-8
import re
import consts
import sundry as s
import sys
import linstordb
from execute.lvm import LVM

class TimeoutError(Exception):
    pass


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
            messege_war = Stor.get_war_mes(result)
            return {'sts':1,'rst':messege_war}
        elif re_suc.search(result):
            return {'sts':0,'rst:':result}
        elif re_war.search(result):
            messege_war = Stor.get_war_mes(result)
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


    """storagepool操作"""
    # 创建storagepool
    def create_storagepool_lvm(self, node, stp, vg):
        obj_lvm = LVM()
        if not obj_lvm.is_vg_exists(vg):
            s.prt_log(f'Volume group:"{vg}" does not exist',1)
            return
        cmd = f'linstor storage-pool create lvm {node} {stp} {vg}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    def create_storagepool_thinlv(self, node, stp, tlv):
        obj_lvm = LVM()
        if not obj_lvm.is_thinlv_exists(tlv):
            s.prt_log(f'Thin logical volume:"{tlv}" does not exist',1)
            return
        cmd = f'linstor storage-pool create lvmthin {node} {stp} {tlv}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    # 删除storagepool -- ok
    def delete_storagepool(self, node, stp):
        cmd = f'linstor storage-pool delete {node} {stp}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)


    def show_all_sp(self,no_color='no'):
        collector = linstordb.CollectData()
        if no_color == 'no':
            data = s.color_data(collector.process_data_stp_all)()
        else:
            data = collector.process_data_stp_all()
        header = ['stp_name','node_name','res_num','driver','pool_name','free_size','total_size','snapshots','status']
        table = s.show_linstor_data(header, data)
        s.prt_log(table,0)


    def show_one_sp(self,sp,no_color='no'):
        collector = linstordb.CollectData()
        node_num = collector._node_num_of_storagepool(sp)
        node_name = collector._node_name_of_storagepool(sp)
        if node_num == 0:
            s.prt_log('The storagepool does not exist',1)
        else:
            info = f'The storagepool name for {node_num} nodes is {sp},they are {node_name}.'
            print(info)
            if no_color == 'no':
                data = s.color_data(collector.process_data_stp_specific)(sp)
            else:
                data = collector.process_data_stp_specific(sp)
            header = ['res_name', 'size', 'device_name', 'used', 'status']
            table = s.show_linstor_data(header, data)
            result = '\n'.join([info, str(table)])
            s.prt_log(result,0)


    """node操作"""
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
            output = s.execute_cmd(cmd)
            result = self.judge_result(output)
            if result:
                if result['sts'] == 0:
                    s.prt_log('SUCCESS', 0)
                elif result['sts'] == 1:
                    s.prt_log(f"SUCCESS\n{result['rst']}", 1)
                elif result['sts'] == 2:
                    s.prt_log(f"FAIL\n{result['rst']}", 1)
                else:
                    s.prt_log(f"FAIL\n{result['rst']}", 2)

    # 删除node
    def delete_node(self, node):
        cmd = f'linstor node delete {node}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    def show_all_node(self, no_color='no'):
        collecter = linstordb.CollectData()
        if no_color == 'no':
            data = s.color_data(collecter.process_data_node_all)()
        else:
            data = collecter.process_data_node_all()
        header = ["node", "node type", "res num", "stp num", "addr", "status"]
        table = s.show_linstor_data(header, data)
        s.prt_log(table,0)

    def show_one_node(self, node, no_color='no'):
        collecter = linstordb.CollectData()
        info = "node:%s\nnodetype:%s\nresource num:%s\nstoragepool num:%s\naddr:%s\nstatus:%s" % collecter.process_data_node_one(
            node)
        if no_color == 'no':
            data_node = s.color_data(collecter.process_data_node_specific)(node)
            data_stp = s.color_data(collecter.process_data_stp_all_of_node)(node)
        else:
            data_node = collecter.process_data_node_specific(node)
            data_stp = collecter.process_data_stp_all_of_node(node)

        header_node = ['res_name', 'stp_name', 'size', 'device_name', 'used', 'status']
        header_stp = ['stp_name', 'node_name', 'res_num', 'driver', 'pool_name', 'free_size', 'total_size', 'snapshots',
                      'status']
        table_node = s.show_linstor_data(header_node, data_node)
        table_stp = s.show_linstor_data(header_stp, data_stp)
        result = '\n'.join([info, str(table_node), str(table_stp)])
        s.prt_log(result,0)



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
            output = s.get_cmd_result(sys._getframe().f_code.co_name,cmd,s.create_oprt_id())
            result = self.judge_result(output)
            if result:
                if result['sts'] == 2:
                    s.prt_log(Stor.get_war_mes(result),1)
                if result['sts'] == 0:
                    s.prt_log(f'Resource {res} was successfully created on Node {node}',0)
                    return {}
                elif result['sts'] == 1:
                    s.prt_log(f'Resource {res} was successfully created on Node {node}',0)
                    return {}
                elif result['sts'] == 3:
                    fail_cause = Stor.get_err_detailes(result['rst'])
                    dict_fail = {node: fail_cause}
                    return dict_fail

        except TimeoutError:
            result = f'{res} created timeout on node {node}, the operation has been cancelled'
            s.prt_log(result,2)
            return {node:'Execution creation timeout'}


    # 创建resource相关
    def linstor_delete_rd(self, res):
        cmd = f'linstor rd d {res}'
        s.execute_cmd(cmd)

    def linstor_create_rd(self, res):
        cmd = f'linstor rd c {res}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                return True
            else:
                print('FAIL')
                return result


    def linstor_create_vd(self, res, size):
        cmd = f'linstor vd c {res} {size}'
        output = s.execute_cmd(cmd)
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
            output = s.execute_cmd(cmd)
            result = self.judge_result(output)
            if result:
                if result['sts'] == 0:
                    s.prt_log('SUCCESS', 0)
                    return True
                elif result['sts'] == 1:
                    s.prt_log(f"SUCCESS\n{result['rst']}", 1)
                    return True
                elif result['sts'] == 2:
                    self.linstor_delete_rd(res)
                    s.prt_log(f"FAIL\n{result['rst']}", 1)
                    return result
                else:
                    self.linstor_delete_rd(res)
                    s.prt_log(f"FAIL\n{result['rst']}", 2)
                    return result

        else:
            s.prt_log('The resource already exists',0)
            return ('The resource already exists')


    def create_res_manual(self, res, size, node, sp):
        dict_all_fail = {}
        dict_args = self.collect_args(node,sp)

        if self.linstor_create_rd(res) is True and self.linstor_create_vd(res, size) is True:
            pass
        else:
            s.prt_log('The resource already exists',0)
            return ('The resource already exists')

        for node_one,sp_one in dict_args.items():
            dict_one_result = self.execute_create_res(res,node_one,sp_one)
            dict_all_fail.update(dict_one_result)

        if len(dict_all_fail.keys()) == len(node):
            self.linstor_delete_rd(res)
        if len(dict_all_fail.keys()):
            fail_info = (f"Creation failure on {' '.join(dict_all_fail.keys())}\n")
            for node, cause in dict_all_fail.items():
                fail_cause = f"{node}:{cause}\n"
                fail_info = fail_info + fail_cause
            s.prt_log(fail_info,2)
            return dict_all_fail
        else:
            return True

    # 添加mirror（自动）
    def add_mirror_auto(self, res, num):
        cmd = f'linstor r c {res} --auto-place {num}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    def add_mirror_manual(self, res, node, sp):
        dict_all_fail = {}
        dict_args = self.collect_args(node,sp)

        for node_one,sp_one in dict_args.items():
            dict_one_result = self.execute_create_res(res,node_one,sp_one)
            dict_all_fail.update(dict_one_result)

        if len(dict_all_fail.keys()):
            fail_info = (f"Creation failure on {' '.join(dict_all_fail.keys())}\n")
            for node, cause in dict_all_fail.items():
                fail_cause = f"{node}:{cause}\n"
                fail_info = fail_info + fail_cause
            s.prt_log(fail_info,2)
            return dict_all_fail
        else:
            return True

    # 创建resource --diskless
    def create_res_diskless(self, node, res):
        cmd = f'linstor r c {node} {res} --diskless'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    # 删除resource,指定节点
    def delete_resource_des(self, node, res):
        cmd = f'linstor resource delete {node} {res}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    # 删除resource，全部节点
    def delete_resource_all(self, res):
        cmd = f'linstor resource-definition delete {res}'
        output = s.execute_cmd(cmd)
        result = self.judge_result(output)
        if result:
            if result['sts'] == 0:
                s.prt_log('SUCCESS', 0)
            elif result['sts'] == 1:
                s.prt_log(f"SUCCESS\n{result['rst']}", 1)
            elif result['sts'] == 2:
                s.prt_log(f"FAIL\n{result['rst']}", 1)
            else:
                s.prt_log(f"FAIL\n{result['rst']}", 2)

    def show_all_res(self,no_color='no'):
        collecter = linstordb.CollectData()
        if no_color == 'no':
            data = s.color_data(collecter.process_data_resource_all)()
        else:
            data = collecter.process_data_resource_all()

        header = ["resource", "mirror_way", "size", "device_name", "used"]
        table = s.show_linstor_data(header,data)
        s.prt_log(table,0)


    def show_one_res(self,res,no_color='no'):
        collecter = linstordb.CollectData()
        info = ("resource:%s\nmirror_way:%s\nsize:%s\ndevice_name:%s\nused:%s" %collecter.process_data_resource_one(res))
        print(info)
        if no_color == 'no':
            data = s.color_data(collecter.process_data_resource_specific)(res)
        else:
            data = collecter.process_data_resource_specific(res)
        header = ['node_name', 'stp_name', 'drbd_role', 'status']
        table = s.show_linstor_data(header,data)
        result = '\n'.join([info, str(table)])
        s.prt_log(result,0)