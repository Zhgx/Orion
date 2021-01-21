import re
import os
import sqlite3
import traceback
import threading

import consts
import log


# LOG_PATH = '/var/log/vtel/'
LOG_PATH = "../vplx/"
LOG_FILE_NAME = 'cli.log'

def prepare_db():
    db = LogDB()
    consts.set_glo_db(db)
    _fill_db_with_log()


def isFileExists(strfile):
    # 检查文件是否存在
    return os.path.isfile(strfile)

def _fill_db_with_log():
    re_ = re.compile(r'\[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?)\] \[(.*?\]?)\]\|',
                     re.DOTALL)
    db = consts.glo_db()
    all_log_data = _read_log_files()
    all_data = re_.findall(all_log_data)
    for data in all_data:
        db.insert_data(data)
    db.con.commit()



def _read_log_files():
    all_data = ''
    if not isFileExists(LOG_PATH+LOG_FILE_NAME):
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
    all_file = (os.listdir(LOG_PATH))
    for file in all_file:
        if base_log_file in file:
            list_file.append(file)
    list_file.sort(reverse=True)
    return list_file



class LogDB():

    def __init__(self):
        self.con = sqlite3.connect("logDB.db", check_same_thread=False)
        self.cur = self.con.cursor()
        self._drop_table()
        self._create_table()

    def insert_data(self, data):
        insert_sql = '''
        insert into logtable
        (
            time,
            transaction_id,
            username,
            type1,
            type2,
            describe1,
            describe2,
            data
            )
        values(?,?,?,?,?,?,?,?)
        '''
        self.cur.execute(insert_sql, data)

    def _create_table(self):
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
        self.cur.execute(create_table_sql)
        self.con.commit()

    def _drop_table(self):
        drop_table_sql = "DROP TABLE if exists logtable"
        self.cur.execute(drop_table_sql)
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
        sql = f"SELECT time,id,data FROM logtable WHERE describe2 = 'output' and type1 = 'INFO' and transaction_id = '{transaction_id}' and id > {id_now}"
        result = self.sql_fetch_one(sql)
        if result:
            time,db_id,output = result
            return {'time':time,'db_id':db_id,'output':output}
        else:
            return {'time':'','db_id':'','output':''}



class Replay():
    _instance_lock = threading.Lock()
    replay_data = []


    def __init__(self):
        logger = log.Log()
        logger.log_switch = False


    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            with Replay._instance_lock:
                if not hasattr(cls, '_instance'):
                    Replay._instance = super().__new__(cls)
                    Replay._instance._parser = args
        return Replay._instance


    def replay_one(self,dict_input):
        if not dict_input:
            print('There is no command to replay')
            return
        print(f"\n-------------- transaction: {dict_input['tid']}  command: {dict_input['cmd']} --------------")
        consts.set_glo_tsc_id(dict_input['tid'])
        if dict_input['valid'] == '0':
            replay_args = self._parser.parse_args(dict_input['cmd'].split())
            try:
                replay_args.func(replay_args)
            except consts.ReplayExit:
                print('The transaction replay ends')
            except Exception:
                print(str(traceback.format_exc()))
        else:
            print(f"Command error: {dict_input['cmd']} , and cannot be executed")


    def replay_more(self,dict_input):
        print('* MODE : REPLAY *')
        print(f'transaction num : {len(dict_input)}')

        number_list = [str(i) for i in list(range(1,len(dict_input)+1))]
        for i in range(len(dict_input)):
            print(f"{i+1:<3} Transaction ID: {dict_input[i]['tid']:<12} CMD: {dict_input[i]['cmd']}")

        answer = ''
        while answer != 'exit':
            print('Please enter the number to execute replay, or "all", enter "exit" to exit：')
            answer = input()
            if answer in number_list:
                dict_cmd = dict_input[int(answer)-1]
                self.replay_one(dict_cmd)
                consts.set_glo_log_id(0)
            elif answer == 'all':
                for dict_cmd in dict_input:
                    self.replay_one(dict_cmd)
            elif answer != 'exit':
                print('Number error')


    def replay(self,args):
        consts.set_glo_rpl('yes')
        logdb.prepare_db()
        obj_logdb = consts.glo_db()
        if args.transactionid and args.date:
            print('Please specify only one type of data for replay')
            return
        elif args.transactionid:
            dict_cmd = obj_logdb.get_userinput_via_tid(args.transactionid)
            print('* MODE : REPLAY *')
            print(f'transaction num : 1')
            self.replay_one(dict_cmd)
        elif args.date:
            dict_cmd = obj_logdb.get_userinput_via_time(args.date[0],args.date[1])
            self.replay_more(dict_cmd)
        else:
            dict_cmd = obj_logdb.get_all_transaction()
            self.replay_more(dict_cmd)
        return dict_cmd




