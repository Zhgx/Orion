import log


class TestLog:

    def setup_class(self):
        self.log = log.Log('test', '1603872339')

    def test_logger_input(self):
        assert self.log.logger_input() != None

    def test_write_to_log(self):
        assert self.log.write_to_log('t1','t2','d1','d2','data') == None
