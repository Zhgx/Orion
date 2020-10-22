# coding:utf-8
# coding:utf-8

import sqlite3
import linstordb
import consts
import sundry
import log
import sys


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

