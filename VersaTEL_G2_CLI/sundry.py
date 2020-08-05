# coding:utf-8
import socket
import signal
import time
import os
import getpass
import traceback
import re

# Connect to the socket server and transfer data, and finally close the
# connection.
def send_via_socket(data):
    ip = "10.203.1.151"
    port = 12144

    client = socket.socket()
    client.connect((ip, port))
    judge_conn = client.recv(8192).decode()
    print(judge_conn)
    client.send(b'database')
    client.recv(8192)
    client.sendall(data)
    client.recv(8192)
    client.send(b'exit')
    client.close()

def record_exception(func):
    """
    Decorator
    Get exception, throw the exception after recording
    :param func:Command binding function
    """
    def wrapper(self,*args):
        try:
            return func(self,*args)
        except Exception as e:
            self.logger.write_to_log('result_to_show', 'ERR', '', str(traceback.format_exc()))
            raise e
    return wrapper

def comfirm_del(type):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        def wrapper(self,*args):
            cli_args = args[0]
            if cli_args.yes:
                func(self,*args)
            else:
                print(
                    'Are you sure you want to delete this %s? If yes, enter \'y/yes\'' %
                    type)
                answer = input()
                if answer in ['y', 'yes']:
                    self.logger.write_to_log('Delete Comfirm', '', '', 'y/yes')
                    func(self,*args)
                else:
                    self.logger.write_to_log('result_to_show','','','Delete canceled')
                    print('Delete canceled')
        return wrapper
    return decorate






def timeout(seconds,error_message = 'Funtion call timed out'):
    def decorated(func):
        def _handled_timeout(signum,frame):
            raise TimeoutError(error_message)

        def wrapper(*args,**kwargs):
            signal.signal(signal.SIGALRM, _handled_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args,**kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorated


def get_transaction_id():
    return int(time.time())

def get_username():
    return getpass.getuser()

def get_hostname():
    return socket.gethostname()

# Get the path of the program
def get_path():
    return os.getcwd()


def re_findall(re_string, tgt_string):
    re_ = re.compile(re_string)
    re_result = re_.findall(tgt_string)
    return re_result


def re_search(re_string, tgt_stirng):
    re_ = re.compile(re_string)
    re_result = re_.search(tgt_stirng).group()
    return re_result