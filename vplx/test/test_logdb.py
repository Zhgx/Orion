import logdb
import consts


def test_prepare_db():
    logdb.prepare_db()
    assert consts.glo_db() != None


def test_isFileExists():
    assert logdb.isFileExists('logdb.py') == True


def test_fill_db_with_log():
    assert logdb._fill_db_with_log() == None


def test_read_log_files():
    assert logdb._read_log_files() != None


def test_get_log_files():
    assert logdb._get_log_files('logDB.db') != None


class TestLogDB:

    def setup_class(self):
        self.log = logdb.LogDB()
        self.tid = '1603872339'

    def test_drop_table(self):
        assert self.log._drop_table() == None

    def test_create_table(self):
        assert self.log._create_table() == None

    def test_insert_data(self):
        # data = ('2020/10/28 16:05:39', self.tid, 'test', 'DATA', 'STR', 'cmd_input', '', '8033629173')
        data = ('2020/10/28 16:05:39', self.tid, 'test', 'DATA', 'STR', 'cmd_input', '6311017008',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        sql = f'SELECT data FROM logtable'
        getdata = self.log.sql_fetch_one(sql)
        assert eval(getdata) == {'cmd': 'stor -h', 'valid': '1'}

    def test_sql_fetch_one(self):
        sql = f'SELECT * FROM logtable'
        assert self.log.sql_fetch_one(sql) != None

    def test_sql_fetch_all(self):
        sql = f'SELECT * FROM logtable'
        # sql = f"SELECT data, describe1 FROM logtable WHERE transaction_id='1603872339'"
        assert self.log.sql_fetch_all(sql) != None

    def test_get_userinput_via_tid(self):
        assert self.log.get_userinput_via_tid(self.tid) == {'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}

    def test_get_userinput_via_time(self):
        star_time = '2020/10/1 10:00:00'
        end_time = '2020/11/1 17:00:00'
        assert self.log.get_userinput_via_time(star_time, end_time) == [
            {'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}]

    def test_get_all_transaction(self):
        assert self.log.get_all_transaction() == [{'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}]

    def test_get_oprt_result(self):
        assert self.log.get_oprt_result('6311017008') == {'result': "{'valid': '1', 'cmd': 'stor -h'}",
                                                          'time': '2020/10/28 16:05:39'}

    def test_get_id(self):
        assert self.log.get_id(self.tid, 'cmd_input') == {'db_id': 1, 'oprt_id': "{'valid': '1', 'cmd': 'stor -h'}",
                                                          'time': '2020/10/28 16:05:39'}

    def test_get_anwser(self):
        data = ('2020/01/28 16:05:39', '1603872111', 'test', 'DATA', 'STR', 'confirm deletion', 'confirm deletion',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        assert self.log.get_anwser('1603872111') == ('2020/01/28 16:05:39', "{'valid': '1', 'cmd': 'stor -h'}")

    def test_get_cmd_output(self):
        data = ('2020/01/29 16:05:39', '1603872222', 'test', 'INFO', 'STR', 'output', 'output',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        assert self.log.get_cmd_output('1603872222') == ('2020/01/29 16:05:39', "{'valid': '1', 'cmd': 'stor -h'}")
