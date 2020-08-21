import re
import os
import sqlite3
import consts

list_cmd = []


def prepare_db():
    db = LogDB()
    db.produce_logdb()
    consts.set_glo_db(db)


def isFileExists(strfile):
    # 检查文件是否存在
    return os.path.isfile(strfile)


def get_target_file(filename):
    list_file = []
    file_last = None
    all_file = (os.listdir('.'))
    for file in all_file:
        if filename in file:
            list_file.append(file)
    list_file.sort(reverse=True)
    return list_file


#[2020/08/06 16:55:51] [vinceshen] [user_input] [1596704151] [/Users/vinceshen/Desktop/vt2_replay/VersaTEL_G3_Code/VersaTEL_G2_CLI] [] [vtel_client_main.py re -t 1596703839]
class LogDB():
    create_table_sql = '''
    create table if not exists logtable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time DATE(30),
        transaction_id varchar(20),
        username varchar(20),
        type1 TEXT,
        type2 TEXT,
        describe1 TEXT,
        describe2 TEXT,
        data TEXT
        );'''

    insert_sql = '''
    replace into logtable
    (
        id,
        time,
        transaction_id,
        username,
        type1,
        type2,
        describe1,
        describe2,
        data
        )
    values(?,?,?,?,?,?,?,?,?)
    '''


    drop_table_sql = "DROP TABLE if exists logtable "

    def __init__(self):
        self.con = sqlite3.connect("logDB.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self.drop_tb()
        self.cur.execute(self.create_table_sql)
        self.con.commit()

    def insert(self, data):
        self.cur.execute(self.insert_sql, data)

    def drop_tb(self):
        self.cur.execute(self.drop_table_sql)
        self.con.commit()

    # 获取表单行数据的通用方法
    def sql_fetch_one(self, sql):
        self.cur.execute(sql)
        data_set = self.cur.fetchone()
        if data_set:
            if len(data_set) == 1:
                return data_set[0]
            else:
                return data_set
        else:
            return data_set

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        return list(date_set)


    def get_userinput_via_tid(self, transaction_id):
        sql = f"SELECT describe2,data FROM logtable WHERE describe1 = 'cmd_input' and transaction_id = '{transaction_id}'"
        result = self.sql_fetch_one(sql)
        if result:
            args_type, cmd = self.sql_fetch_one(sql)
            return [{'tid':transaction_id,'type':args_type,'cmd':cmd}]


    def get_userinput_via_time(self, start_time, end_time):
        sql = f"SELECT transaction_id,describe2,data FROM logtable WHERE describe1 = 'cmd_input' and time >= '{start_time}' and time <= '{end_time}'"
        all_data = self.sql_fetch_all(sql)
        result_list = []
        for i in all_data:
            tid, args_type, cmd = i
            dict_one = {'tid':tid, 'type':args_type, 'cmd':cmd}
            result_list.append(dict_one)
        return result_list

    def get_all_transaction(self):
        sql = "SELECT transaction_id,describe2,data FROM logtable WHERE describe1 = 'cmd_input'"
        all_data = self.sql_fetch_all(sql)
        result_list = []
        for i in all_data:
            tid, args_type, cmd = i
            dict_one = {'tid':tid, 'type':args_type, 'cmd':cmd}
            result_list.append(dict_one)
        return result_list


    def get_oprt_result(self, oprt_id):
        sql = f"SELECT time,data FROM logtable WHERE type1 = 'DATA' and describe2 = '{oprt_id}'"
        # sql = f"SELECT time,data FROM logtable WHERE type1 = 'DATA' and type2 = 'cmd' and describe2 = '{oprt_id}'"
        if oprt_id:
            result = self.sql_fetch_one(sql)
            if result:
                time, data = self.sql_fetch_one(sql)
                return {'time': time, 'result': data}
            else:
                return {'time':'','result':''}
        else:
            return {'time': '', 'result': ''}

    def get_id(self, transaction_id, string):
        id_now = consts.glo_log_id()
        sql = f"SELECT time,id,data FROM logtable WHERE describe1 = '{string}' and type2 = 'STR' and id > {id_now} and transaction_id = '{transaction_id}'"
        result = self.sql_fetch_one(sql)
        if result:
            time,db_id,oprt_id = result
            return {'time':time,'db_id':db_id,'oprt_id':oprt_id}
        else:
            return {'time':'','db_id':'','oprt_id':''}

    def get_anwser(self,transaction_id):
        sql = f"SELECT time,data FROM logtable WHERE transaction_id = '{transaction_id}' and describe2 = 'confirm deletion'"
        result = self.sql_fetch_one(sql)
        if result:
            return result
        else:
            return ('','')

    def get_cmd_output(self,transaction_id):
        id_now = consts.glo_log_id()
        sql = f"SELECT time,data FROM logtable WHERE describe2 = 'output' and type1 = 'INFO' and transaction_id = '{transaction_id}' and id > {id_now}"
        result = self.sql_fetch_one(sql)
        if result:
            return result
        else:
            return ('','')

    def produce_logdb(self):
        log_path = "./VersaTEL_G2_CLI.log"
        logfilename = 'VersaTEL_G2_CLI.log'
        id = (None,)
        re_ = re.compile(r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?\]?)\]\|', re.DOTALL)
        if not isFileExists(log_path):
            print('no file')
            return

        for file in get_target_file(logfilename):
            f = open('./' + file)
            content = f.read()
            file_data = re_.findall(content)

            for data_one in file_data:
                data = id + data_one
                self.insert(data)

            f.close()
        self.con.commit()


#
# logdb = LogDB()
#
# logdb.produce_logdb()
# # print(logdb.get_userinput_via_tid('1596779465'))
# all_list = logdb.get_all_transaction()
#
# for i in all_list:
#     if i[0]:
#         print(i)
#     else:
#         print('不符合条件')