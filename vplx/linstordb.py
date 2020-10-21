# coding:utf-8
import execute as ex
import sundry as s
import sqlite3
import sys


class DataIsEmpty(Exception):
    pass

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




class LinstorDB(Database):
    """
    Get the output of LINSTOR through the command, use regular expression to get and process it into a list,
    and insert it into the newly created memory database.
    """
    # 连接数据库,创建光标对象

    def __init__(self):
        super().__init__(':memory:')
        self.cur = self.db.cursor()

    def build_table(self):
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


        self.cur.execute(crt_ntb_sql)
        self.cur.execute(crt_rtb_sql)
        self.cur.execute(crt_sptb_sql)
        self.insert_linstor_data()
        self.db.commit()




    def insert_linstor_data(self):
        insert_stb_sql = '''
            insert into storagepooltb
            (
                StoragePool,
                Node,
                Driver,
                PoolName,
                FreeCapacity,
                TotalCapacity,
                SupportsSnapshots,
                State
                )
            values(?,?,?,?,?,?,?,?)
            '''

        insert_rtb_sql = '''
            insert into resourcetb
            (
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
            values(?,?,?,?,?,?,?,?,?)
            '''
        insert_ntb_sql = '''insert into nodetb(Node,NodeType,Addresses,State)values(?,?,?,?)'''


        linstor = ex.Linstor()
        node = linstor.get_linstor_data('linstor --no-color --no-utf8 n l')
        res = linstor.get_linstor_data('linstor --no-color --no-utf8 r lv')
        sp = linstor.get_linstor_data('linstor --no-color --no-utf8 sp l')
        self.insert_data(insert_ntb_sql, node,'nodetb')
        self.insert_data(insert_rtb_sql, res,'resourcetb')
        self.insert_data(insert_stb_sql, sp,'storagepooltb')

    @s.deco_db_insert
    def insert_data(self, sql, list_data,tablename):
        for i in range(len(list_data)):
            if not list_data[i]:
                s.prt_log('数据错误，无法插入数据表',2)
            self.cur.execute(sql, list_data[i])
