import re
import os
import sqlite3

list_cmd = []


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



class LogDB():
    create_table_sql = '''
    create table if not exists logtable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time DATE(30),
        user varchar(20),
        type varchar(20),
        transaction_id varchar(20),
        describe1 TEXT,
        describe2 TEXT,
        data TEXT
        );'''

    insert_sql = '''
    replace into logtable
    (
        id,
        time,
        user,
        type,
        transaction_id,
        describe1,
        describe2,
        data
        )
    values(?,?,?,?,?,?,?,?)
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
        date_set = self.cur.fetchone()
        return date_set

    # 获取表全部数据的通用方法
    def sql_fetch_all(self, sql):
        cur = self.cur
        cur.execute(sql)
        date_set = cur.fetchall()
        return list(date_set)


    def get_userinput_from_tid(self, transaction_id):
        sql = "SELECT data FROM logtable WHERE type = 'user_input' and transaction_id = '%s'" % transaction_id
        return self.sql_fetch_one(sql)[0]

    def get_userinput_from_time(self, start_time, end_time):
        sql = "SELECT data FROM logtable WHERE type = 'user_input' and time >= '%s' and time <= '%s'" % (
        start_time, end_time)
        return self.sql_fetch_all(sql)

    def get_result_from_tid(self, transaction_id):
        sql = "SELECT data FROM logtable WHERE type = 'result_to_show' and transaction_id = '%s'"%(transaction_id)
        return self.sql_fetch_all(sql)[0]

    def get_result_from_time(self,start_time,end_time):
        sql = "SELECT data FROM logtable WHERE type = 'result_to_show' and time >= '%s' and time <= '%s'"%(start_time,end_time)
        return self.sql_fetch_all(sql)

    def produce_logdb(self):
        log_path = "./CLI.log"
        logfilename = 'VersaTEL_G2_CLI.log'
        id = (None,)
        re_ = re.compile(r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?\]?)\]', re.DOTALL)
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


