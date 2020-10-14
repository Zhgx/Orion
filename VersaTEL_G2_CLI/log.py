# coding:utf-8
import logging
import logging.handlers
import logging.config
import consts

path = '/home/samba/VersaTEL_G3_Code/VersaTEL_G2_CLI/'


class MyLoggerAdapter(logging.LoggerAdapter):
    """
    实现一个LoggerAdapter的子类，重写process()方法。
    其中对于kwargs参数的操作应该是先判断其本身是否包含extra关键字，如果包含则不使用默认值进行替换；
    如果kwargs参数中不包含extra关键字则取默认值。
    """
    def process(self, msg, kwargs):
        if 'extra' not in kwargs:
            kwargs["extra"] = self.extra
        return msg, kwargs


class Log(object):
    fmt = logging.Formatter("%(asctime)s [%(transaction_id)s] [%(username)s] [%(type1)s] [%(type2)s] [%(describe1)s] [%(describe2)s] [%(data)s]|",datefmt = '[%Y/%m/%d %H:%M:%S]')
    handler_input = logging.handlers.RotatingFileHandler(filename=f'VersaTEL_G2_CLI.log',mode='a',maxBytes=10*1024*1024,backupCount=5)
    handler_input.setFormatter(fmt)
    def __init__(self,username,transaction_id):
        self.username = username
        self.transaction_id = transaction_id


    def logger_input(self):
        logger_cli = logging.getLogger('vtel_cli')
        logger_cli.addHandler(self.handler_input)
        logger_cli.setLevel(logging.DEBUG)
        # %(asctime)s - [%(username)s] - [%(type)s] - [%(describe1)s] - [%(describe2)s] - [%(data)s]
        extra_dict = {
            "username": "USERNAME",
            "transaction_id": "",
            "type1": "TYPE1",
            "type2": "TYPE2",
            "describe1": "",
            "describe2": "",
            "data": ""}
        # 获取一个自定义LoggerAdapter类的实例
        logger = MyLoggerAdapter(logger_cli, extra_dict)
        return logger


    # write to log file
    def write_to_log(self,type1,type2,describe1,describe2,data):
        logger_cli = self.logger_input()

        if consts.glo_log_switch() == 'no':
            logger_cli.logger.removeHandler(self.handler_input)
        # InputLogger.logger.removeHandler(self.handler_input)
        logger_cli.debug(
            '',
            extra={
                'username': self.username,
                'transaction_id': self.transaction_id,
                'type1':type1,
                'type2': type2,
                'describe1': describe1,
                'describe2': describe2,
                'data': data})