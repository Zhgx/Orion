import socket
import log
from apscheduler.schedulers.blocking import BlockingScheduler


ip_port = ('10.203.1.76',12144)
judge_len = 8192



def check_daemon_status(job):
    scheduler = BlockingScheduler()
    scheduler.add_job(job,'interval',minutes=5)
    scheduler.start()



def connect_self():
    logger = log.Log('username', '0000')
    client = socket.socket()
    try:
        client.connect(ip_port)
        data = client.recv(8192)  # 接开始连接
        client.send(b'0000')
        client.recv(8192)
        client.send(b'exit')
        if data:
            logger.write_to_log('STATUS','SOCKET','server','','safe')
    except ConnectionRefusedError:
        logger.write_to_log('STATUS', 'SOCKET', 'server', '', 'connect error')



if __name__ == '__main__':
    check_daemon_status(connect_self)