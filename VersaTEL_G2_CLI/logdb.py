import re
import os
import sqlite3
import consts

LOG_PATH = "./VersaTEL_G2_CLI.log"
LOG_FILE_NAME = 'VersaTEL_G2_CLI.log'

def prepare_db():
    db = LogDB()
    consts.set_glo_db(db)
    _fill_db_with_log()
    return db


def isFileExists(strfile):
    # 检查文件是否存在
    return os.path.isfile(strfile)

def _fill_db_with_log():
    id = (None,)
    re_ = re.compile(r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?\]?)\]\|',
                     re.DOTALL)

    db = consts.glo_db()
    all_log_data = _read_log_files()
    all_data = re_.findall(all_log_data)

    for data in all_data:
        data = id + data
        db.insert_data(data)

    db.con.commit()



def _read_log_files():
    all_data = ''
    if not isFileExists(LOG_PATH):
        print('no log file')
        return
    for file in _get_log_files(LOG_FILE_NAME):
        f = open('./' + file)
        data = f.read()
        all_data+=data
        f.close()
    return all_data


def _get_log_files(base_log_file):
    list_file = []
    all_file = (os.listdir('.'))
    for file in all_file:
        if base_log_file in file:
            list_file.append(file)
    list_file.sort(reverse=True)
    return list_file



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
        self._drop_table()
        self._create_table()

    def insert_data(self, data):
        self.cur.execute(self.insert_sql, data)

    def _create_table(self):
        self.cur.execute(self.create_table_sql)
        self.con.commit()

    def _drop_table(self):
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
        sql = f"SELECT data FROM logtable WHERE describe1 = 'cmd_input' and transaction_id = '{transaction_id}'"
        result = self.sql_fetch_one(sql)
        if result:
            result = eval(result)
            return {'tid':transaction_id, 'valid':result['valid'],'cmd':result['cmd']}
        # if result:
        #     args_type, cmd = self.sql_fetch_one(sql)
        #     return [{'tid':transaction_id,'type':args_type,'cmd':cmd}]


    def get_userinput_via_time(self, start_time, end_time):
        sql = f"SELECT transaction_id,data FROM logtable WHERE describe1 = 'cmd_input' and time >= '{start_time}' and time <= '{end_time}'"
        all_data = self.sql_fetch_all(sql)
        result_list = []
        for i in all_data:
            tid, user_input = i
            user_input = eval(user_input)
            dict_one = {'tid':tid, 'valid':user_input['valid'], 'cmd':user_input['cmd']}
            result_list.append(dict_one)

        return result_list

    # 需要修改
    def get_all_transaction(self):
        sql = "SELECT transaction_id,data FROM logtable WHERE describe1 = 'cmd_input'"
        all_data = self.sql_fetch_all(sql)
        result_list = []
        for i in all_data:
            tid, user_input = i
            user_input = eval(user_input)
            dict_one = {'tid':tid, 'valid':user_input['valid'], 'cmd':user_input['cmd']}
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

    def get_id(self, transaction_id, string,id_now):
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



    # for Regression Testing
    def get_refine_linstor_data(self,transaction_id):
        id_dict = self.get_id(transaction_id,'refine_linstor',consts.glo_log_id())
        result = self.get_oprt_result(id_dict['oprt_id'])['result']
        if result:
            return eval(result)