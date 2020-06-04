# coding:utf-8
import socket
from functools import wraps
import signal
import hashlib
import time

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


def comfirm_del(type):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args):
            cli_args = args[1]
            if cli_args.yes:
                func(*args)
            else:
                print(
                    'Are you sure you want to delete this %s? If yes, enter \'y/yes\'' %
                    type)
                answer = input()
                if answer in ['y', 'yes']:
                    func(*args)
                else:
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
    # data = str(time.time())
    # result = int(hashlib.sha256(data.encode('utf-8')).hexdigest(), 16) % (10**8)
    # return result

