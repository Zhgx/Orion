#coding:utf-8
import socket

#Get the ip address of this machine
def get_host_ip():
    try:
        obj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        obj_socket.connect(('8.8.8.8', 80))
        ip = obj_socket.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        obj_socket.close()
    return ip

#Connect to the socket server and transfer data, and finally close the connection.
def socket_send_result(data):
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


