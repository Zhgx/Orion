#coding:utf-8
import socket
from functools import wraps

#Connect to the socket server and transfer data, and finally close the connection.
def send_via_socket(data):
    ip = "127.0.0.1"
    port = 12144

    client = socket.socket()
    client.connect((ip,port))
    judge_conn = client.recv(8192).decode()
    print(judge_conn)
    client.send(b'database')
    client.recv(8192)
    client.sendall(data)
    client.recv(8192)
    client.send(b'exit')
    client.close()


def comfirm_del(func):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    @wraps(func)
    def wrapper(*args):
        cli_args = args[0]
        if cli_args.yes:
            func(*args)
        else:
            print('Are you sure you want to delete it? If yes, enter \'y/yes\'')
            answer = input()
            if answer in ['y', 'yes']:
                func(*args)
            else:
                print('Delete canceled')
    return wrapper