# coding:utf-8
import traceback
import colorama as ca
import prettytable as pt
from functools import wraps
import sqlite3
import threading
import execute as ex
import log


class LINSTORDB():
    """
    Get the output of LINSTOR through the command, use regular expression to get and process it into a list,
    and insert it into the newly created memory database.
    """

    # LINSTOR表
    crt_sptb_sql = '''
    create table if not exists storagepooltb(id integer primary key,
        StoragePool varchar(20),
        Node varchar(20),
        Driver varchar(20),
        PoolName varchar(20),
        FreeCapacity varchar(20),
        TotalCapacity varchar(20),
        SupportsSnapshots varchar(20),
        State varchar(20)
        );'''

    crt_rtb_sql = '''
    create table if not exists resourcetb(
        id integer primary key,
        Node varchar(20),
        Resource varchar(20),
        Storagepool varchar(20),
        VolumeNr varchar(20),
        MinorNr varchar(20),
        DeviceName varchar(20),
        Allocated varchar(20),
        InUse varchar(20),
        State varchar(20)
        );'''

    crt_ntb_sql = '''
    create table if not exists nodetb(
        id integer primary key,
        Node varchar(20),
        NodeType varchar(20),
        Addresses varchar(20),
        State varchar(20)
        );'''

    crt_vgtb_sql = '''
        create table if not exists vgtb(
        id integer primary key,
        VG varchar(20),
        VSize varchar(20),
        VFree varchar(20)
        );'''

    crt_thinlvtb_sql = '''
        create table if not exists thinlvtb(
        id integer primary key,
        LV varchar(20),
        VG varchar(20),
        LSize varchar(20)
        );'''

    replace_stb_sql = '''
    replace into storagepooltb
    (
        id,
        StoragePool,
        Node,
        Driver,
        PoolName,
        FreeCapacity,
        TotalCapacity,
        SupportsSnapshots,
        State
        )
    values(?,?,?,?,?,?,?,?,?)
    '''

    replace_rtb_sql = '''
        replace into resourcetb
        (
            id,
            Node,
            Resource,
            StoragePool,
            VolumeNr,
            MinorNr,
            DeviceName,
            Allocated,
            InUse,
            State
            )
        values(?,?,?,?,?,?,?,?,?,?)
    '''

    replace_ntb_sql = '''
        replace into nodetb
        (
            id,
            Node,
            NodeType,
            Addresses,
            State
            )
        values(?,?,?,?,?)
    '''

    replace_vgtb_sql = '''
        replace into vgtb
        (
            id,
            VG,
            VSize,
            VFree
            )
        values(?,?,?,?)
    '''

    replace_thinlvtb_sql = '''
        replace into thinlvtb
        (
            id,
            LV,
            VG,
            LSize
            )
        values(?,?,?,?)
    '''
    # 连接数据库,创建光标对象

    def __init__(self,logger):
        # linstor.db
        self.con = sqlite3.connect(":memory:", check_same_thread=False)
        self.cur = self.con.cursor()
        self.logger = logger

    # 执行获取数据，删除表，创建表，插入数据
    def rebuild_linstor_tb(self):
        self.cur.execute(self.crt_sptb_sql)  # 检查是否存在表，如不存在，则新创建表
        self.cur.execute(self.crt_rtb_sql)
        self.cur.execute(self.crt_ntb_sql)
        self.con.commit()
        self.get_output()
        self.con.commit()

    def rebuild_all_tb(self):
        # self.drop_tb()
        self.create_tb()
        self.exc_get_vg()
        self.exc_get_thinlv()
        self.get_output()
        self.con.commit()

    def get_output(self):
        thread_all = []
        cmds = ['linstor --no-color --no-utf8 n l',
         'linstor --no-color --no-utf8 r lv',
         'linstor --no-color --no-utf8 sp l']
        sql = [self.replace_ntb_sql,
               self.replace_rtb_sql,
               self.replace_stb_sql]

        for cmd,sql in zip(cmds,sql):
            thread_ins_data = threading.Thread(target=self.thread_get_linstor,args=(cmd,sql))
            thread_all.append(thread_ins_data)

        # threading
        # thread_ins_node = threading.Thread(target=self.thread_get_linstor,args=(cmds[0]))
        # thread_ins_res = threading.Thread(target=self.thread_get_res())
        # thread_ins_sp = threading.Thread(target=self.thread_get_sp())
        #
        # threads = [thread_ins_node,thread_ins_res,thread_ins_sp]

        for i in range(len(thread_all)):
            thread_all[i].start()
        for i in range(len(thread_all)):
            thread_all[i].join()

    def exc_get_vg(self):
        obj_lvm = ex.LVM(self.logger)
        vg = obj_lvm.refine_vg(obj_lvm.get_vg())
        self.insert_data(self.replace_vgtb_sql, vg)

    def exc_get_thinlv(self):
        obj_lvm = ex.LVM(self.logger)
        thinlv = obj_lvm.refine_thinlv(obj_lvm.get_thinlv())
        self.insert_data(self.replace_thinlvtb_sql, thinlv)

    def thread_get_linstor(self,cmd,sql):
        actuator = ex.LINSTOR(self.logger)
        linstor = actuator.refine_linstor(actuator.get_linstor(cmd))
        self.insert_data(sql,linstor)
    #
    # def thread_get_node(self):
    #     node = ex.LINSTOR.refine_linstor(ex.LINSTOR.get_linstor('linstor --no-color --no-utf8 n l'))
    #     self.insert_data(self.replace_ntb_sql, node)
    #
    # def thread_get_res(self):
    #     res = ex.LINSTOR.refine_linstor(ex.LINSTOR.get_res())
    #     self.insert_data(self.replace_rtb_sql, res)
    #
    # def thread_get_sp(self):
    #     sp = ex.LINSTOR.refine_linstor(ex.LINSTOR.get_sp())
    #     self.insert_data(self.replace_stb_sql, sp)

    # 创建表

    def create_tb(self):
        self.cur.execute(self.crt_vgtb_sql)
        self.cur.execute(self.crt_thinlvtb_sql)
        self.cur.execute(self.crt_sptb_sql)  # 检查是否存在表，如不存在，则新创建表
        self.cur.execute(self.crt_rtb_sql)
        self.cur.execute(self.crt_ntb_sql)
        self.con.commit()

    # 删除表，现不使用
    def drop_tb(self):
        tables_sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        self.cur.execute(tables_sql)
        tables = self.cur.fetchall()
        for table in tables:
            drp_sql = "drop table if exists %s" % table
            self.cur.execute(drp_sql)
        self.con.commit()

    def insert_data(self, sql, list_data):
        for i in range(len(list_data)):
            list_data[i].insert(0, i + 1)
            self.cur.execute(sql, list_data[i])
            self.logger.write_to_log('LISNTORDB_insert_data', 'sql_insert_data', '', list_data[i])


    def data_base_dump(self):
        cur = self.cur
        con = self.con
        self.rebuild_all_tb()
        SQL_script = con.iterdump()
        cur.close()
        return "\n".join(SQL_script)


class DataProcess():
    """
    Provide a data interface to retrieve specific data in the LINSTOR database.
    """

    def __init__(self,logger):
        self.linstor_db = LINSTORDB(logger)
        self.linstor_db.rebuild_linstor_tb()
        self.cur = self.linstor_db.cur
        self.logger = logger

    # 获取表单行数据的通用方法
    def sql_fetch_one(self, sql):
        self.cur.execute(sql)
        date_set = self.cur.fetchone()
        self.logger.write_to_log('sql_fetch_one',sql,'',date_set)
        return date_set

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        self.logger.write_to_log('sql_fetch_all', sql, '', list(date_set))
        return list(date_set)

    # Return all data of node table

    def _select_nodetb_all(self):
        select_sql = "SELECT Node,NodeType,Addresses,State FROM nodetb"
        return self.sql_fetch_all(select_sql)

    # The node name of the incoming data, and return its information in the
    # node table
    def _select_nodetb_one(self, node):
        select_sql = "SELECT Node,NodeType,Addresses,State FROM nodetb WHERE  Node = \'%s\'" % node
        return self.sql_fetch_one(select_sql)

    def _select_res_num(self, node):
        select_sql = "SELECT COUNT(Resource) FROM resourcetb WHERE  Node = \'%s\'" % node
        return self.sql_fetch_one(select_sql)

    def _select_stp_num(self, node):
        select_sql = "SELECT COUNT(Node) FROM storagepooltb WHERE Node = \'%s\'" % node
        return self.sql_fetch_one(select_sql)

    def _select_resourcetb(self, node):
        select_sql = "SELECT DISTINCT Resource,StoragePool,Allocated,DeviceName,InUse,State FROM resourcetb WHERE Node = \'%s\'" % node
        return self.sql_fetch_all(select_sql)

    # resource
    def _get_resource(self):
        res = []
        sql_res_all = "SELECT DISTINCT Resource,Allocated,DeviceName,InUse FROM resourcetb"
        res_all = self.sql_fetch_all(sql_res_all)

        sql_res_inuse = "SELECT DISTINCT Resource,Allocated,DeviceName,InUse FROM resourcetb WHERE InUse = 'InUse'"
        in_use = self.sql_fetch_all(sql_res_inuse)

        for i in in_use:
            res.append(i[0])

        for i in res_all:
            if i[0] in res and i[3] == 'Unused':
                res_all.remove(i)
        return res_all

    def _get_mirro_way(self, res):
        select_sql = "SELECT COUNT(Resource) FROM resourcetb WHERE Resource = \'%s\'" % res
        return self.sql_fetch_one(select_sql)

    def _get_mirror_way_son(self, res):
        select_sql = "SELECT Node,StoragePool,InUse,State FROM resourcetb WHERE Resource = \'%s\'" % res
        return self.sql_fetch_all(select_sql)

    # storagepool
    # 查询storagepooltb全部信息
    def _select_storagepooltb(self):
        select_sql = '''SELECT
            StoragePool,
            Node,
            Driver,
            PoolName,
            FreeCapacity,
            TotalCapacity,
            SupportsSnapshots,
            State
            FROM storagepooltb
            '''
        return self.sql_fetch_all(select_sql)

    def _res_sum(self, node, stp):
        select_sql = "SELECT COUNT(DISTINCT Resource) FROM resourcetb WHERE Node = '{}' AND StoragePool = '{}'".format(
            node, stp)
        num = self.sql_fetch_one(select_sql)
        return num[0]

    def _res(self, stp):
        select_sql = "SELECT Resource,Allocated,DeviceName,InUse,State FROM resourcetb WHERE StoragePool = \'%s\'" % stp
        return self.sql_fetch_all(select_sql)

    def _node_num_of_storagepool(self, stp):
        select_sql = "SELECT COUNT(Node) FROM storagepooltb WHERE StoragePool = \'%s\'" % stp
        num = self.sql_fetch_one(select_sql)
        return num[0]

    def _node_name_of_storagepool(self, stp):
        select_sql = "SELECT Node FROM storagepooltb WHERE StoragePool = \'%s\'" % stp
        date_set = self.sql_fetch_all(select_sql)
        if len(date_set) == 1:
            names = date_set[0][0]
        else:
            names = [n[0] for n in date_set]
        return names

    def process_data_node_all(self):
        date_list = []
        for i in self._select_nodetb_all():
            node, node_type, addr, status = i
            res_num = self._select_res_num(node)[0]
            stp_num = self._select_stp_num(node)[0]
            list_one = [node, node_type, res_num, stp_num, addr, status]
            date_list.append(list_one)
        self.cur.close()
        return date_list

    # 置顶文字
    def process_data_node_one(self, node):
        n = self._select_nodetb_one(node)
        node, node_type, addr, status = n
        res_num = self._select_res_num(node)[0]
        stp_num = self._select_stp_num(node)[0]
        list = [node, node_type, res_num, stp_num, addr, status]
        return tuple(list)

    def process_data_node_specific(self, node):
        date_list = []
        for n in self._select_resourcetb(node):
            res_name, stp_name, size, device_name, used, status = n
            list_one = [res_name, stp_name, size, device_name, used, status]
            date_list.append(list_one)
        return date_list

    def process_data_resource_all(self):
        date_list = []
        list_one = []
        for i in self._get_resource():
            if i[1]:  # 过滤size为空的resource
                resource, size, device_name, used = i
                mirror_way = self._get_mirro_way(str(i[0]))[0]
                list_one = [resource, mirror_way, size, device_name, used]
                date_list.append(list_one)
        self.cur.close()
        return date_list

    # 置顶文字
    def process_data_resource_one(self, resource):
        list_one = []
        for i in self._get_resource():
            if i[0] == resource:
                if i[1]:
                    resource, size, device_name, used = i
                    mirror_way = self._get_mirro_way(str(i[0]))[0]
                    list_one = [resource, mirror_way, size, device_name, used]
        return tuple(list_one)

    def process_data_resource_specific(self, resource):
        data_list = []
        for res_one in self._get_mirror_way_son(resource):
            node_name, stp_name, drbd_role, status = list(res_one)
            if drbd_role == u'InUse':
                drbd_role = u'primary'
            elif drbd_role == u'Unused':
                drbd_role = u'secondary'
            list_one = [node_name, stp_name, drbd_role, status]
            data_list.append(list_one)
        self.cur.close()
        return data_list

    def process_data_stp_all(self):
        date_list = []
        for i in self._select_storagepooltb():
            stp_name, node_name, driver, pool_name, free_size, total_size, snapshots, status = i
            res_num = self._res_sum(str(node_name), str(stp_name))
            list_one = [
                stp_name,
                node_name,
                res_num,
                driver,
                pool_name,
                free_size,
                total_size,
                snapshots,
                status]
            date_list.append(list_one)
        self.cur.close()
        return date_list

    def process_data_stp_all_of_node(self, node):
        date_list = []
        for i in self._select_storagepooltb():
            stp_name, node_name, driver, pool_name, free_size, total_size, snapshots, status = i
            res_num = self._res_sum(str(node_name), str(stp_name))
            if node_name == node:
                list_one = [
                    stp_name,
                    node_name,
                    res_num,
                    driver,
                    pool_name,
                    free_size,
                    total_size,
                    snapshots,
                    status]
                date_list.append(list_one)
        self.cur.close()
        return date_list

    def process_data_stp_specific(self, stp):
        date_list = []
        for res in self._res(stp):
            res_name, size, device_name, used, status = res
            list_one = [res_name, size, device_name, used, status]
            date_list.append(list_one)
        self.cur.close()
        return date_list


# 有颜色输出表格装饰器
def table_color(func):
    @wraps(func)
    def wrapper(*args):
        table = pt.PrettyTable()
        status_true = ['UpToDate', 'Online', 'Ok', 'InUse']
        data, table.field_names = func(*args)
        for lst in data:
            if lst[-1] in status_true:
                lst[-1] = ca.Fore.GREEN + lst[-1] + ca.Style.RESET_ALL
            else:
                lst[-1] = ca.Fore.RED + lst[-1] + ca.Style.RESET_ALL
        for i in data:
            table.add_row(i)
        print(table)
        return table
    return wrapper

# 无颜色输出表格装饰器


def table(func):
    @wraps(func)
    def wrapper(*args):
        table = pt.PrettyTable()
        data, table.field_names = func(*args)
        for i in data:
            table.add_row(i)
        print(table)
        return table
    return wrapper


class OutputData(DataProcess):
    def __init__(self,logger):
        DataProcess.__init__(self,logger)


    """Node视图
    """
    @table_color
    def node_all_color(self):
        data = super().process_data_node_all()
        header = ["node", "node type", "res num", "stp num", "addr", "status"]
        return data, header

    @table
    def node_all(self):
        data = super().process_data_node_all()
        header = ["node", "node type", "res num", "stp num", "addr", "status"]
        return data, header

    @table_color
    def node_one_color(self, node):
        data = super().process_data_node_specific(node)
        header = [
            'res_name',
            'stp_name',
            'size',
            'device_name',
            'used',
            'status']
        return data, header

    @table_color
    def node_stp_one_color(self, node):
        data = super().process_data_stp_all_of_node(node)
        header = [
            'stp_name',
            'node_name',
            'res_num',
            'driver',
            'pool_name',
            'free_size',
            'total_size',
            'snapshots',
            'status']
        return data, header

    @table
    def node_one(self, node):
        data = super().process_data_node_specific(node)
        header = [
            'res_name',
            'stp_name',
            'size',
            'device_name',
            'used',
            'status']
        return data, header

    @table
    def node_stp_one(self, node):
        data = super().process_data_stp_all_of_node(node)
        header = [
            'stp_name',
            'node_name',
            'res_num',
            'driver',
            'pool_name',
            'free_size',
            'total_size',
            'snapshots',
            'status']
        return data, header

    # 指定的node视图

    def show_node_one_color(self, node):

        try:
            info_first = (
                    "node:%s\nnodetype:%s\nresource num:%s\nstoragepool num:%s\naddr:%s\nstatus:%s" %
                    self.process_data_node_one(node))
            print(info_first)
            info_second = self.node_one_color(node)
            info_third = self.node_stp_one_color(node)
            result = '\n'.join([info_first, str(info_second), str(info_third)])
            self.logger.write_to_log('result_to_show','','',result)
        except TypeError:
            info_err = str(traceback.format_exc())
            self.logger.write_to_log('result_to_show','','',info_err)
            print('Node %s does not exist.' % node)

    def show_node_one(self, node):
        # node = args[0]
        try:
            info_first = (
                    "node:%s\nnodetype:%s\nresource num:%s\nstoragepool num:%s\naddr:%s\nstatus:%s" %
                    self.process_data_node_one(node))
            print(info_first)
            info_second = self.node_one(node)
            info_third = self.node_stp_one(node)
            result = '\n'.join([info_first, str(info_second), str(info_third)])
            self.logger.write_to_log('result_to_show','','',result)
        except TypeError:
            self.logger.write_to_log('result_to_show','','',str(traceback.format_exc()))
            print('Node %s does not exist.' % node)

    """Resource视图
    """
    @table_color
    def res_all_color(self):
        data = super().process_data_resource_all()
        header = ["resource", "mirror_way", "size", "device_name", "used"]
        return data, header

    @table
    def res_all(self):
        data = super().process_data_resource_all()
        header = ["resource", "mirror_way", "size", "device_name", "used"]
        return data, header

    @table_color
    def res_one_color(self, res):
        data = super().process_data_resource_specific(res)
        header = ['node_name', 'stp_name', 'drbd_role', 'status']
        return data, header

    @table
    def res_one(self, res):
        data = super().process_data_resource_specific(res)
        header = ['node_name', 'stp_name', 'drbd_role', 'status']
        return data, header

    def show_res_one_color(self, res):
        try:
            info_first = (
                "resource:%s\nmirror_way:%s\nsize:%s\ndevice_name:%s\nused:%s" %
                self.process_data_resource_one(res))
            print(info_first)
            info_second = self.res_one_color(res)
            result = '\n'.join([info_first, str(info_second)])
            self.logger.write_to_log('result_to_show','','',result)
        except TypeError:
            self.logger.write_to_log('result_to_show','','',str(traceback.format_exc()))
            print('Resource %s does not exist.' % res)

    def show_res_one(self, res):
        try:
            print(
                "resource:%s\nmirror_way:%s\nsize:%s\ndevice_name:%s\nused:%s" %
                self.process_data_resource_one(res))
            self.res_one(res)
        except TypeError:
            print('Resource %s does not exist.' % res)

    """stp视图
    """

    @table_color
    def sp_all_color(self):
        data = super().process_data_stp_all()
        header = [
            'stp_name',
            'node_name',
            'res_num',
            'driver',
            'pool_name',
            'free_size',
            'total_size',
            'snapshots',
            'status']
        return data, header

    @table
    def sp_all(self):
        data = super().process_data_stp_all()
        header = [
            'stp_name',
            'node_name',
            'res_num',
            'driver',
            'pool_name',
            'free_size',
            'total_size',
            'snapshots',
            'status']
        return data, header

    @table_color
    def sp_one_color(self, sp):
        data = super().process_data_stp_specific(sp)
        header = ['res_name', 'size', 'device_name', 'used', 'status']
        return data, header

    @table
    def sp_one(self, sp):
        data = super().process_data_stp_specific(sp)
        header = ['res_name', 'size', 'device_name', 'used', 'status']
        return data, header

    def show_sp_one_color(self, sp):
        node_num = self._node_num_of_storagepool(sp)
        node_name = self._node_name_of_storagepool(sp)
        if node_num == 0:
            print('The storagepool does not exist')
            self.logger.write_to_log('result_to_show', '', '', 'The storagepool does not exist')
        elif node_num == 1:
            info_first = (
                'Only one node (%s) exists in the storage pool named %s' %
                (node_name, sp))
            print(info_first)
            info_second = self.sp_one_color(sp)
            result = '\n'.join([info_first, str(info_second)])
            self.logger.write_to_log('result_to_show', '', '', result)
        else:
            node_name = ' and '.join(node_name)
            info_first = (
                'The storagepool name for %s nodes is %s,they are %s.' %
                (node_num, sp, node_name))
            print(info_first)
            info_second = self.sp_one_color(sp)
            result = '\n'.join([info_first, str(info_second)])
            self.logger.write_to_log('result_to_show','','',result)

    def show_sp_one(self, sp):
        node_num = self._node_num_of_storagepool(sp)
        node_name = self._node_name_of_storagepool(sp)
        if node_num == 0:
            print('The storagepool does not exist')
            self.logger.write_to_log('result_to_show', '', '', 'The storagepool does not exist')
        elif node_num == 1:
            info_first = (
                'Only one node (%s) exists in the storage pool named %s' %
                (node_name, sp))
            info_second = self.sp_one(sp)
            result = '\n'.join([info_first, str(info_second)])
            self.logger.write_to_log('result_to_show','','',result)
        else:
            node_name = ' and '.join(node_name)
            info_first = (
                'The storagepool name for %s nodes is %s,they are %s.' %
                (node_num, sp, node_name))
            info_second = self.sp_one(sp)
            result = '\n'.join([info_first, str(info_second)])
            self.logger.write_to_log('result_to_show','','',result)
