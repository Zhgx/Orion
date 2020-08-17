# coding:utf-8
import socket
import signal
import time
import os
import getpass
import traceback
import re
import prettytable
import sys
from random import shuffle
import subprocess
from functools import wraps
import colorama as ca

import consts
import execute


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
            self.logger.write_to_log('DATA','debug','exception','', str(traceback.format_exc()))
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


def create_transaction_id():
    return int(time.time())

def create_oprt_id():
    time_stamp = str(create_transaction_id())
    str_list = list(time_stamp)
    shuffle(str_list)
    return ''.join(str_list)

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



def show_data(list_header,dict_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if dict_data:
        for i,j in dict_data.items():
            data_one = [i,(' '.join(j) if isinstance(j,list) == True else j)]
            table.add_row(data_one)
    else:
        pass
    print(table)
    return table

def show_data_map(list_header,dict_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if dict_data:
        # {map1:[hg1,dg1] => [map1,hg1,dg1]}
        for i, j in dict_data.items():
            j.insert(0,i)
            table.add_row(j)
    else:
        pass
    print(table)
    return table


def show_linstor_data(list_header,list_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if list_data:
        for i in list_data:
            table.add_row(i)
    else:
        pass
    print(table)
    return table


def change_pointer(new_id):
    consts.set_glo_log_id(new_id)


def execute_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    output = p.stdout.read().decode()
    return output


def execute_crm_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    out, err = p.communicate()
    if len(out) > 0:
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output
    if len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
        return output
    if out == b'':  # 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output


def get_cmd_result(unique_str, cmd, oprt_id):
    logger = consts.glo_log()
    RPL = consts.glo_rpl()
    if RPL == 'no':
        logger.write_to_log('DATA', 'STR', unique_str, '', oprt_id)
        logger.write_to_log('OPRT', 'cmd', '', oprt_id, cmd)
        result_cmd = execute_cmd(cmd)
        logger.write_to_log('DATA', 'cmd', '', oprt_id, result_cmd)
        return result_cmd
    elif RPL == 'yes':
        logdb = consts.glo_db()
        db_id, oprt_id = logdb.get_oprt_id(consts.glo_tsc_id(), unique_str)

        result_cmd = logdb.get_cmd_result(oprt_id)
        if db_id:
            change_pointer(db_id)
        return result_cmd


def get_crm_cmd_result(unique_str, cmd, oprt_id):
    logger = consts.glo_log()
    RPL = consts.glo_rpl()
    if RPL == 'no':
        logger.write_to_log('DATA', 'STR', unique_str, '', oprt_id)
        logger.write_to_log('OPRT', 'cmd', 'iscsi', oprt_id, cmd)
        result_cmd = execute_crm_cmd(cmd)
        logger.write_to_log('DATA', 'cmd', 'iscsi', oprt_id, result_cmd)
        return result_cmd
    elif RPL == 'yes':
        logdb = consts.glo_db()
        db_id, oprt_id = logdb.get_oprt_id(consts.glo_tsc_id(), unique_str)
        result_cmd = logdb.get_cmd_result(oprt_id)
        if result_cmd:
            result = eval(result_cmd)
        else:
            result = None
        if db_id:
            change_pointer(db_id)
        return result


def prt(str, level=0, warning_level=0):
    if isinstance(warning_level, int):
        warning_str = '*' * warning_level
    else:
        warning_str = ''
    rpl = consts.glo_rpl()

    if rpl == 'no':
        print(str)

    else:
        if warning_level == 'exception':
            print(' exception infomation '.center(105, '*'))
            print(str)
            print(f'{" exception infomation ":*^105}', '\n')
            return

        db = consts.glo_db()
        time = db.get_time_via_str(consts.glo_tsc_id(), str)
        if not time:
            time = ''

        print(f'{warning_str:<4}Re:{time:<20}{warning_str:>4}')

        if level == 0:
            print(str)
        else:
            print(f'RE:{time:<20}{warning_str:<4}'
                  f'{str}')


def prt_log(str, level, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    logger = consts.glo_log()
    rpl = consts.glo_rpl()
    if rpl == 'yes':
        db = consts.glo_db()
        oprt_id = db.get_oprt_id_via_db_id(consts.glo_tsc_id(), consts.glo_log_id())
        prt(str + f'.oprt_id:{oprt_id}', level, warning_level)
    elif rpl == 'no':
        prt(str, level, warning_level)

    if warning_level == 0:
        logger.write_to_log('INFO', 'info', 'finish','',str)
    elif warning_level == 1:
        logger.write_to_log('INFO', 'warning', 'fail', '', str)
    elif warning_level == 2:
        logger.write_to_log('INFO', 'error', 'exit', '', str)
        # print(f'{"":-^{format_width}}','\n')
        # sys.exit()


def pwe(str, level, warning_level):
    rpl = consts.glo_rpl()
    prt_log(str, level, warning_level)

    if warning_level == 2:
        if rpl == 'no':
            sys.exit()
        else:
            raise consts.ReplayExit



def color_data(func):
    """
    装饰器，给特定的linstor数据进行着色
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args):
        status_true = ['UpToDate', 'Online', 'Ok', 'InUse']
        data = func(*args)
        for lst in data:
            if lst[-1] in status_true:
                lst[-1] = ca.Fore.GREEN + lst[-1] + ca.Style.RESET_ALL
            else:
                lst[-1] = ca.Fore.RED + lst[-1] + ca.Style.RESET_ALL
        return data
    return wrapper