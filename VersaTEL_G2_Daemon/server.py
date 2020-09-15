#coding:utf-8
import socketserver,socket,subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
import log
import traceback
import sundry as s
import threading



host_port = 12144
# host_ip = get_host_ip()
host_ip = '10.203.1.76'
byteData = b'null'
tid = '0'

def socket_send(client,data,logger):
    oprt_id = s.create_oprt_id()
    logger.write_to_log('DATA', 'SOCKET', 'send', '', oprt_id)
    logger.write_to_log('OPRT', 'SOCKET', 'send', oprt_id, '')
    client.send(data)
    logger.write_to_log('DATA', 'SOCKET', 'send', oprt_id, data)


def socket_sendall(client,data,logger):
    oprt_id = s.create_oprt_id()
    logger.write_to_log('DATA', 'SOCKET', 'sendall', '', oprt_id)
    logger.write_to_log('OPRT', 'SOCKET', 'sendall', oprt_id, '')
    client.sendall(data)
    logger.write_to_log('DATA', 'SOCKET', 'sendall', oprt_id, data)


def socket_recv(client,logger):
    oprt_id = s.create_oprt_id()
    logger.write_to_log('DATA', 'SOCKET', 'recv', '', oprt_id)
    logger.write_to_log('OPRT', 'SOCKET', 'recv', oprt_id, '')
    data = client.recv(8192)
    logger.write_to_log('DATA','SOCKET','recv',oprt_id,data)
    return data


def execute_cmd(cmd,logger):
    oprt_id = s.create_oprt_id()
    logger.write_to_log('DATA', 'STR', 'execute_cmd', '', oprt_id)
    logger.write_to_log('OPRT', 'CMD', 'execute_cmd', oprt_id, cmd)
    result = subprocess.run(cmd, shell=True)
    logger.write_to_log('DATA', 'CMD', 'execute_cmd', oprt_id, result)



#Obtain local IP, this IP is needed for socket connection.
def get_host_ip(logger):
    try:
        oprt_id = s.create_oprt_id()
        obj_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.write_to_log('DATA', 'SOCKET', 'send', '', oprt_id)
        logger.write_to_log('OPRT','SOCKET','connect',oprt_id,'')
        obj_socket.connect(('8.8.8.8', 80))
        logger.write_to_log('DATA', 'SOCKET', 'connect', oprt_id, '8.8.8.8,80')
        ip = obj_socket.getsockname()[0]
    except Exception:
        logger.write_to_log('DATA', 'DEBUG', 'exception','',str(traceback.format_exc()))
        return '127.0.0.0'
    finally:
        oprt_id = s.create_oprt_id()
        logger.write_to_log('DATA', 'SOCKET', 'close', '', oprt_id)
        logger.write_to_log('OPRT','SOCKET','close',oprt_id,'')
        obj_socket.close()
        logger.write_to_log('DATA', 'SOCKET', 'close', oprt_id, 'close socket connection')
    return ip



class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        global byteData
        global tid
        if tid == '0':
            self.request.send(b'start to connect')
        else:
            self.request.send(tid.encode())
        tid_num = self.request.recv(8192)
        if tid_num != b'no tid':
            tid = tid_num.decode()

        logger = log.Log('username', tid)
        if tid == '0000':
            logger.close_log()

        socket_send(self.request,('%s connection succeeded' % host_ip).encode(),logger)

        while True:
            data = socket_recv(self.request,logger).decode()
            print ('recv:',data)
            if data=='exit':
                tid = '0'
                break
            elif 'CLIcommands' in data:
                socket_send(self.request,b'data',logger)
                ex_cmd = socket_recv(self.request,logger).decode()
                execute_cmd(ex_cmd,logger)
                data_len = str(len(byteData))
                socket_sendall(self.request,data_len.encode(),logger)
                socket_recv(self.request,logger)
                socket_sendall(self.request,byteData,logger)
            elif 'database' in data:
                socket_send(self.request,b'ok',logger)
                sql_script = socket_recv(self.request,logger)
                print('recv','data')
                byteData = sql_script
                socket_send(self.request,b'over',logger)
            else:
                pass



def connect_self():
    client = socket.socket()
    try:
        client.connect((host_ip,host_port))
        data = client.recv(8192)  # 接开始连接
        client.send(b'0000')
        client.recv(8192)
        client.send(b'exit')

        if data:
            logger = log.Log('username', '0000')
            logger.write_to_log('STATUS','SOCKET','server','','safe')
            logger.close_log()
    except ConnectionRefusedError:
        logger = log.Log('username', '0000')
        logger.write_to_log('STATUS', 'SOCKET', 'server', '', 'connect error')
        logger.close_log()


# def check_daemon_status():
#     scheduler = BlockingScheduler()
#     job = connect_self
#     scheduler.add_job(job,'interval',seconds=1)
#     scheduler.start()

def start_up_server():
    server = socketserver.ThreadingTCPServer((host_ip, host_port), MyTCPHandler)
    server.serve_forever()



# def start_server():
#     thread_start_up = threading.Thread(target=start_up_server)
#     thread_check = threading.Thread(target=check_daemon_status)
#     thread_start_up.start()
#     thread_check.start()



if __name__ == '__main__':
    start_up_server()


