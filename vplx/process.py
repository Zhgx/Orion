# coding:utf-8
# coding:utf-8

import sqlite3
import linstordb
import consts
import sundry
import log
import sys


queries = {
    'SELECT': 'SELECT %s FROM %s WHERE %s',
    'SELECT_ALL': 'SELECT %s FROM %s',
    'SELECT_COUNT': 'SELECT COUNT(%s) FROM %s WHERE %s',
    'INSERT': 'INSERT INTO %s VALUES(%s)',
    'UPDATE': 'UPDATE %s SET %s WHERE %s',
    'DELETE': 'DELETE FROM %s where %s',
    'DELETE_ALL': 'DELETE FROM %s',
    'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
    'DROP_TABLE': 'DROP TABLE if exists %s'}

class Database():

    def __init__(self, data_file):
        self.db = sqlite3.connect(data_file, check_same_thread=False)
        self.data_file = data_file

    def free(self, cursor):
        cursor.close()

    # def write(self, query, values=None):
    #     cursor = self.db.cursor()
    #     if values is not None:
    #         cursor.execute(query, list(values))
    #     else:
    #         cursor.execute(query)
    #     self.db.commit()
    #     return cursor

    def read(self, query, values=None):
        cursor = self.db.cursor()
        if values is not None:
            cursor.execute(query, list(values))
        else:
            cursor.execute(query)
        return cursor


    def fet_all(self,cursor):
        return cursor.fetchall()

    def fet_one(self,cursor):
        return cursor.fetchone()


    def select(self, tables, *args, **kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT'] % (vals, locs, conds)
        return self.read(query,subs)

    def select_all(self, tables, *args):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        query = queries['SELECT_ALL'] % (vals, locs)
        return self.read(query)

    def select_count(self,tables,*args,**kwargs):
        vals = ','.join([l for l in args])
        locs = ','.join(tables)
        conds = ' and '.join(['%s=?' % k for k in kwargs])
        subs = [kwargs[k] for k in kwargs]
        query = queries['SELECT_COUNT'] % (vals, locs, conds)
        cursor = self.read(query, subs)
        return cursor.fetchone()[0]


    # def insert(self, table_name, *args):
    #     values = ','.join(['?' for l in args])
    #     query = queries['INSERT'] % (table_name, values)
    #     return self.write(query, args)

    # def update(self, table_name, set_args, **kwargs):
    #     updates = ','.join(['%s=?' % k for k in set_args])
    #     conds = ' and '.join(['%s=?' % k for k in kwargs])
    #     vals = [set_args[k] for k in set_args]
    #     subs = [kwargs[k] for k in kwargs]
    #     query = queries['UPDATE'] % (table_name, updates, conds)
    #     return self.write(query, vals + subs)
    #
    # def delete(self, table_name, **kwargs):
    #     conds = ' and '.join(['%s=?' % k for k in kwargs])
    #     subs = [kwargs[k] for k in kwargs]
    #     query = queries['DELETE'] % (table_name, conds)
    #     return self.write(query, subs)
    #
    # def delete_all(self, table_name):
    #     query = queries['DELETE_ALL'] % table_name
    #     return self.write(query)
    #
    #
    # def drop_table(self, table_name):
    #     query = queries['DROP_TABLE'] % table_name
    #     self.free(self.write(query))


    def disconnect(self):
        self.db.close()




class Process_data():
    def __init__(self):
        db = linstordb.LinstorDB()
        # 生成数据库
        db.build_table()
        self.cur = db.cur

    # 获取表单行数据的通用方法
    def sql_fetch_one(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchone()
        if len(date_set) == 1:
            return date_set[0]
        else:
            return list(date_set)

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        return date_set

    # 选项node数据
    def get_option_node(self):
        def get_online_node():
            select_sql = "SELECT Node FROM nodetb WHERE State = 'Online'"
            return self.sql_fetch_all(select_sql)

        list_node = get_online_node()  # E.g:[('klay1',), ('klay2',)]
        list_result = []
        for node in list_node:
            dict_one = {'key_node':node[0]}
            list_result.append(dict_one)
        return list_result

    # 选项sp数据
    def get_option_sp(self):

        def get_online_node():
            select_sql = "SELECT Node FROM nodetb WHERE State = 'Online'"
            return self.sql_fetch_all(select_sql)

        def get_ok_sp(node):
            select_sql = "SELECT Storagepool FROM storagepooltb WHERE Node = \'%s\' " \
                         "and FreeCapacity is not null and State = 'Ok'" % node
            return self.sql_fetch_all(select_sql)

        list_node = get_online_node()
        list_result = []
        for node in list_node:
            list_sp = get_ok_sp(node)
            list_result_sp = []
            for sp in list_sp:
                dict_sp = {'key_sp':sp}
                list_result_sp.append(dict_sp)
            dict_one = {'NodeName':node, 'Spool':list_result_sp}
            list_result.append(dict_one)
        return list_result

    # 选项lvm/thinlv数据
    def get_option_lvm(self):
        sql_vg = "SELECT VG FROM vgtb"
        sql_thinlv = "SELECT LV FROM thinlvtb"

        vg = self.sql_fetch_all(sql_vg)
        thinlv = self.sql_fetch_all(sql_thinlv)

        list_vg = []
        list_thinlv = []
        for vg_one in vg:
            dict_vg = {"cityName": vg_one}
            list_vg.append(dict_vg)

        for thinlv_one in thinlv:
            dict_thinlv = {"cityName": thinlv_one}
            list_thinlv.append(dict_thinlv)

        dict_all = {"lvm": list_vg, "thin_lvm": list_thinlv}
        return dict_all



    # 选项node num数据
    def get_option_nodenum(self,):

        def get_node_num():
            select_sql = "SELECT COUNT(Node) FROM nodetb"
            return self.sql_fetch_one(select_sql)

        num_node = int(get_node_num()) + 1
        list_result = []
        for i in range(1, num_node):
            dict_one = {'key_nodenum':i}
            list_result.append(dict_one)
        return list_result

    # node表格格式
    def process_data_node(self):
        # cur = self.linstor_db.cur
        cur = self.cur
        date = []

        sql_count_node = "select count(Node) from nodetb"
        sql_node = lambda id:"select Node,NodeType,Addresses,State from nodetb where id = %s" % id
        sql_count_res = lambda id:"SELECT COUNT(Resource) FROM resourcetb WHERE Node IN (SELECT Node FROM nodetb WHERE id = %s)" % id
        sql_count_stp = lambda id:"SELECT COUNT(Node) FROM storagepooltb WHERE Node IN (SELECT Node FROM nodetb WHERE id = %s)" % id
        sql_res = lambda id:"SELECT Resource,StoragePool,Allocated,DeviceName,InUse,State FROM resourcetb WHERE Node IN ((SELECT Node FROM nodetb WHERE id = %s))" % id

        node_num = self.sql_fetch_one(sql_count_node)

        # 通用的select
        for i in range(1, (node_num + 1)):
            node, nodetype, addr, status = self.sql_fetch_one(sql_node(i))
            res_num = self.sql_fetch_one(sql_count_res(i))
            stp_num = self.sql_fetch_one(sql_count_stp(i))
            print("res_num:", res_num)
            print("stp_num:", stp_num)
            list_resdict = []
            for res in self.sql_fetch_all(sql_res(i)):
                res_name, stp_name, size, device_name, used, status = res
                dic = {"res_name": res_name, "stp_name": stp_name, "size": size, "device_name": device_name,
                       "used": used, "status": status}
                list_resdict.append(dic)
            # for #返回res_num 对应的几个resource信息，
            date_ = {"node": node,
                     "node_type": nodetype,
                     "res_num": str(res_num),
                     "stp_num": str(stp_num),
                     "addr": addr,
                     "status": status,
                     "res_num_son": list_resdict}
            date.append(date_)
        dict = {"data": date}
        cur.close()
        return dict

    # resourece表格格式
    def process_data_resource(self):
        cur = self.cur
        date = []

        sql_mirror_way_num = lambda rn: "SELECT COUNT(Resource) FROM resourcetb WHERE Resource = \'%s\' " % rn
        sql_mirror_way = lambda rn: "SELECT Node,StoragePool,InUse,State FROM resourcetb WHERE Resource = \'%s\' " % rn

        def _get_resource():
            res = []
            sql_resource_all = "SELECT distinct Resource,Allocated,DeviceName,InUse FROM resourcetb "
            sql_resource_inuse = "SELECT distinct Resource,Allocated,DeviceName,InUse FROM resourcetb WHERE InUse = 'InUse'"
            res_all = self.sql_fetch_all(sql_resource_all)
            res_inuse = self.sql_fetch_all(sql_resource_inuse)
            for i in res_inuse:
                res.append(i[0])
            for i in res_all:
                if i[0] in res and i[3] == 'Unused':
                    res_all.remove(i)
            return res_all

        for i in _get_resource():
            if i[1]:
                resource, size, device_name, used = i
                mirror_way_num = self.sql_fetch_one(sql_mirror_way_num(str(i[0])))
                list_resdict = []
                for res_one in self.sql_fetch_all(sql_mirror_way(str(i[0]))):
                    node_name, stp_name, drbd_role, status = list(res_one)
                    if drbd_role == u'InUse':
                        drbd_role = u'primary'
                    elif drbd_role == u'Unused':
                        drbd_role = u'secondary'
                    dic = {"node_name": node_name, "stp_name": stp_name, "drbd_role": drbd_role, "status": status}
                    list_resdict.append(dic)
                date_one = {"resource": resource,
                            "mirror_way": mirror_way_num,
                            "size": size,
                            "device_name": device_name,
                            "used": used,
                            "mirror_way_son": list_resdict}
                date.append(date_one)
        dict = {"data": date}
        cur.close()
        return dict

    # storage pool表格格式
    def process_data_stp(self):
        # linstor_db = Linst_db()
        cur = self.cur
        date = []

        sql_stp = "SELECT StoragePool,Node,Driver,PoolName,FreeCapacity,TotalCapacity,SupportsSnapshots,State FROM storagepooltb"
        sql_res_num = lambda node, stp: "SELECT COUNT(DISTINCT Resource) FROM resourcetb WHERE Node = \'%s\' AND StoragePool = \'%s\'" % (
        node, stp)
        sql_res = lambda node, stp: "SELECT Resource,Allocated,DeviceName,InUse,State FROM resourcetb WHERE Node = \'%s\' AND StoragePool = \'%s\'" % (
        node, stp)

        for i in self.sql_fetch_all(sql_stp):
            stp_name, node_name, driver, pool_name, free_size, total_size, snapshots, stp_status = i
            res_num = self.sql_fetch_one(sql_res_num(str(node_name), str(stp_name)))
            list_resdict = []
            for res in self.sql_fetch_all(sql_res(str(node_name), str(stp_name))):
                res_name, size, device_name, used, res_status = res
                dic = {"res_name": res_name, "size": size, "device_name": device_name, "used": used, "status": res_status}
                list_resdict.append(dic)

            # 返回res_num 对应的几个resource信息，
            date_ = {"stp_name": stp_name,
                     "node_name": node_name,
                     "res_num": str(res_num),
                     "driver": driver,
                     "pool_name": pool_name,
                     "free_size": free_size,
                     "total_size": total_size,
                     "snapshots": snapshots,
                     "status": stp_status,
                     "res_name_son": list_resdict}
            date.append(date_)
        dict = {"data": date}
        cur.close()
        return dict



pc = Process_data()
pc.process_data_node()
pc.process_data_stp()
