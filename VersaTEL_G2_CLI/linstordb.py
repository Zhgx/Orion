# coding:utf-8
import traceback

from functools import wraps
import sqlite3
import execute as ex
import consts
import sundry as s


class LinstorDB():
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

    def __init__(self):
        # linstor.db
        self.con = sqlite3.connect("linstordb.db", check_same_thread=False)
        self.cur = self.con.cursor()


    def build_table(self,type='linstor'):
        self.cur.execute(self.crt_ntb_sql)
        self.cur.execute(self.crt_rtb_sql)
        self.cur.execute(self.crt_sptb_sql)
        if type == 'all':
            self.cur.execute(self.crt_vgtb_sql)
            self.cur.execute(self.crt_thinlvtb_sql)
            self.insert_lvm_data()
        self.insert_linstor_data()
        self.con.commit()



    def insert_lvm_data(self):
        lvm = ex.LVM()
        vg = lvm.refine_vg()
        thinlv = lvm.refine_thinlv()
        self.insert_data(self.replace_vgtb_sql, vg)
        self.insert_data(self.replace_thinlvtb_sql, thinlv)


    def insert_linstor_data(self):
        linstor = ex.Linstor()
        node = linstor.get_linstor_data('linstor --no-color --no-utf8 n l')
        res = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        sp = linstor.get_linstor_data('linstor --no-color --no-utf8 sp l')
        self.insert_data(self.replace_ntb_sql, node)
        self.insert_data(self.replace_rtb_sql, res)
        self.insert_data(self.replace_stb_sql, sp)

    # 删除表，现不使用
    def drop_tb(self):
        tables_sql = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        self.cur.execute(tables_sql)
        tables = self.cur.fetchall()
        for table in tables:
            drp_sql = f'drop table if exists {table}'
            self.cur.execute(drp_sql)
        self.con.commit()

    # 插入数据
    @s.sql_insert_decorator
    def insert_data(self, sql, list_data):
        for i in range(len(list_data)):
            list_data[i].insert(0, i + 1)
            self.cur.execute(sql, list_data[i])


    def data_base_dump(self):
        cur = self.cur
        con = self.con
        self.build_table('all')
        SQL_script = con.iterdump()
        cur.close()
        return "\n".join(SQL_script)


class CollectData():
    """
    Provide a data interface to retrieve specific data in the LINSTOR database.
    """

    def __init__(self):
        self.linstor_db = LinstorDB()
        self.linstor_db.build_table()
        self.cur = self.linstor_db.cur

    # 获取表单行数据的通用方法
    def sql_fetch_one(self, sql):
        self.cur.execute(sql)
        date_set = self.cur.fetchone()
        return date_set

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        return list(date_set)

    # Return all data of node table

    def select_data(self):
        # sql = f'SELECT {",".join(data)} FROM {table} WHERE {limit}'
        sql = f'SELECT * FROM nodetb inner join resourcetb on nodetb.Node = resourcetb.Node inner join storagepooltb on resourcetb.StoragePool = storagepooltb.StoragePool'
        return self.sql_fetch_all(sql)


    def _select_nodetb_all(self):
        select_sql = "SELECT Node,NodeType,Addresses,State FROM nodetb"
        return self.sql_fetch_all(select_sql)

    # The node name of the incoming data, and return its information in the
    # node table
    def _select_nodetb_one(self, node):
        select_sql = f"SELECT Node,NodeType,Addresses,State FROM nodetb WHERE  Node = '{node}'"
        return self.sql_fetch_one(select_sql)

    def _select_res_num(self, node):
        select_sql = f"SELECT COUNT(Resource) FROM resourcetb WHERE  Node = '{node}'"
        return self.sql_fetch_one(select_sql)

    def _select_stp_num(self, node):
        select_sql = f"SELECT COUNT(Node) FROM storagepooltb WHERE Node = '{node}'"
        return self.sql_fetch_one(select_sql)

    def _select_resourcetb(self, node):
        select_sql = f"SELECT DISTINCT Resource,StoragePool,Allocated,DeviceName,InUse,State FROM resourcetb WHERE Node = '{node}'"
        return self.sql_fetch_all(select_sql)

    # resource
    def _get_resource(self):
        res_used = []
        result = []
        sql_res_all = "SELECT DISTINCT Resource,Allocated,DeviceName,InUse FROM resourcetb"
        res_all = self.sql_fetch_all(sql_res_all)

        sql_res_inuse = "SELECT DISTINCT Resource,Allocated,DeviceName,InUse FROM resourcetb WHERE InUse = 'InUse'"
        in_use = self.sql_fetch_all(sql_res_inuse)

        for i in in_use:
            res_used.append(i[0])

        for res in res_all:
            if res[3] == 'InUse':
                result.append(res)
            if res[0] not in res_used and res[3] == 'Unused':
                result.append(res)

        return result

    def _get_mirro_way(self, res):
        select_sql = f"SELECT COUNT(Resource) FROM resourcetb WHERE Resource = '{res}'"
        return self.sql_fetch_one(select_sql)

    def _get_mirror_way_son(self, res):
        select_sql = f"SELECT Node,StoragePool,InUse,State FROM resourcetb WHERE Resource = '{res}'"
        return self.sql_fetch_all(select_sql)

    # storagepool
    # 查询storagepooltb全部信息
    def _select_storagepooltb(self):
        select_sql = "SELECT StoragePool,Node,Driver,PoolName,FreeCapacity,TotalCapacity,SupportsSnapshots,State FROM storagepooltb"
        return self.sql_fetch_all(select_sql)

    def _res_sum(self, node, stp):
        select_sql = f"SELECT COUNT(DISTINCT Resource) FROM resourcetb WHERE Node = '{node}' AND StoragePool = '{stp}'"
        num = self.sql_fetch_one(select_sql)
        return num[0]

    def _res(self, stp):
        select_sql = f"SELECT Resource,Allocated,DeviceName,InUse,State FROM resourcetb WHERE StoragePool = '{stp}'"
        return self.sql_fetch_all(select_sql)

    def _node_num_of_storagepool(self, stp):
        select_sql = f"SELECT COUNT(Node) FROM storagepooltb WHERE StoragePool = '{stp}'"
        num = self.sql_fetch_one(select_sql)
        return num[0]

    def _node_name_of_storagepool(self, stp):
        select_sql = f"SELECT Node FROM storagepooltb WHERE StoragePool = '{stp}'"
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
        if n:
            node, node_type, addr, status = n
            res_num = self._select_res_num(node)[0]
            stp_num = self._select_stp_num(node)[0]
            list = [node, node_type, res_num, stp_num, addr, status]
            return tuple(list)
        else:
            return []

    def process_data_node_specific(self, node):
        date_list = []
        for res_data in self._select_resourcetb(node):
            date_list.append(list(res_data))
        return date_list

    def process_data_resource_all(self):
        date_list = []
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


# coo = CollectData()
