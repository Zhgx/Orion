import subprocess


def create_ip(name, ip, netmask='24'):
    cmd = f'crm cof primitive {name} IPaddr2 params ip={ip} cidr_netmask={netmask}'
    cmd_result = subprocess.getoutput(cmd)
    print(cmd_result)


def create_pb(name, ip, port='3260', action='block'):
    """

    :param name:
    :param ip:
    :param port:
    :param action: block/unblock
    :return:
    """
    if not action in ['block', 'unblock']:
        raise TypeError('action参数输入错误：block/unblock')

    cmd = f'crm cof primitive {name} portblock params ip={ip} portno={port} protocol=tcp action={action} op monitor timeout=20 interval=20'
    cmd_result = subprocess.getoutput(cmd)
    print(cmd_result)




# create_ip('test_1','10.203.1.152')

# create_pb('test_1_block','10.203.1.152')


import time

def execute_crm_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    output = None
    while True:
        if p.poll() is not None:
            break
        if p.stderr:
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
    elif len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
    elif out == b'':  # 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}

    if output:
        return output
    else:
        print('ex')


p = subprocess.Popen('python3 vtel.py iscsi pt m vip -ip 10.203.1.75 -p 3261',stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
p.stdin.write('y'.encode())
out, err = p.communicate()
print(out.decode())