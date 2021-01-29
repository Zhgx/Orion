import logdb
import consts


<<<<<<< HEAD
def test_prepare_db():
    """初始化 logdb"""
    logdb.prepare_db()
    assert consts.glo_db() != None

=======
>>>>>>> b78e6cb5f618d5ddec071cdb27972707d55b5a74

# 检查文件是否存在，存在返回True，否则返回False
def test_isFileExists():
    """检查文件是否存在，测试用例包括文件存/文件不存在"""
    # 存在
    assert logdb.isFileExists('logdb.py')
    # 不存在
    assert not logdb.isFileExists('XXXX.py')


def test_fill_db_with_log():
    """根据 log file 插入数据到 logdb"""
    assert logdb._fill_db_with_log() is None


def test_read_log_files():
    """测试能否成功读取 log 文件"中的数据"""
    # 读取成功则不为空字符
    assert logdb._read_log_files()
    # 读取失败


def test_get_log_files():
    """ 测试是否能成功获取 log 文件"""
    # 获取成功则不为空列表
    assert logdb._get_log_files('logDB.db')
    # 获取失败


class TestLogDB:

    def setup_class(self):
        self.log = logdb.LogDB()
        self.tid = '1603872339'

    def test_drop_table(self):
        """删除 logtable 数据库表"""
        sql = 'select count(*) from sqlite_master where type="table" and name = "logtable"'
        self.log._drop_table()
        assert self.log.cur.execute(sql).fetchone()[0] == 0

    def test_create_table(self):
        """创建 logtable 数据库表"""
        sql = 'select count(*) from sqlite_master where type="table" and name = "logtable"'
        self.log._create_table()
        assert self.log.cur.execute(sql).fetchone()[0] == 1

    def test_insert_data(self):
        """数据库插入数据"""
        # data = ('2020/10/28 16:05:39', self.tid, 'test', 'DATA', 'STR', 'cmd_input', '', '8033629173')
        data = ('2020/10/28 16:05:39', self.tid, 'test', 'DATA', 'STR', 'cmd_input', '6311017008',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        sql = f'SELECT data FROM logtable'
        getdata = self.log.sql_fetch_one(sql)
        assert eval(getdata) == {'cmd': 'stor -h', 'valid': '1'}

    def test_sql_fetch_one(self):
        """获取单一列数据"""
        sql = f'SELECT * FROM logtable'
        assert self.log.sql_fetch_one(sql) is not None

    def test_sql_fetch_all(self):
        """获取满足条件的全部数据列"""
        sql = f'SELECT * FROM logtable'
        # sql = f"SELECT data, describe1 FROM logtable WHERE transaction_id='1603872339'"
        assert self.log.sql_fetch_all(sql) is not None

    def test_get_userinput_via_tid(self):
        """通过 tid 获取用户操作"""
        assert self.log.get_userinput_via_tid(self.tid) == {'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}

    def test_get_userinput_via_time(self):
        """通过时间段获取用户操作"""
        star_time = '2020/10/1 10:00:00'
        end_time = '2020/11/1 17:00:00'
        assert self.log.get_userinput_via_time(star_time, end_time) == [
            {'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}]

    def test_get_all_transaction(self):
        """获取全部cmd_input类型的tid"""
        assert self.log.get_all_transaction() == [{'cmd': 'stor -h', 'tid': '1603872339', 'valid': '1'}]

    def test_get_oprt_result(self):
        """根据 oprt_id 获取 result"""
        assert self.log.get_oprt_result('6311017008') == {'result': "{'valid': '1', 'cmd': 'stor -h'}",
                                                          'time': '2020/10/28 16:05:39'}

    def test_get_id(self):
        """根据tid,describe1获取对应的time，db_id，opt_id"""
        assert self.log.get_id(self.tid, 'cmd_input') == {'db_id': 1, 'oprt_id': "{'valid': '1', 'cmd': 'stor -h'}",
                                                          'time': '2020/10/28 16:05:39'}

    def test_get_anwser(self):
        """根据tid获取对应的time，answer"""
        data = ('2020/01/28 16:05:39', '1603872111', 'test', 'DATA', 'STR', 'confirm deletion', 'confirm deletion',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        assert self.log.get_anwser('1603872111') == ('2020/01/28 16:05:39', "{'valid': '1', 'cmd': 'stor -h'}")

    def test_get_cmd_output(self):
        """根据tid获取对应的time，db_id,output"""
        data = ('2020/01/29 16:05:39', '1603872222', 'test', 'INFO', 'STR', 'output', 'output',
                "{'valid': '1', 'cmd': 'stor -h'}")
        self.log.insert_data(data)
        assert self.log.get_cmd_output('1603872222') == {'time': '2020/01/29 16:05:39', 'db_id': 3, 'output': "{'valid': '1', 'cmd': 'stor -h'}"}
        # assert self.log.get_cmd_output('1603872222') == ('2020/01/29 16:05:39', "{'valid': '1', 'cmd': 'stor -h'}")
