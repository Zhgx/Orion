import subprocess
import time


def execute_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
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
    out,err = p.communicate()
    # if len(out) > 0:
    #     output = {'sts': 1, 'rst': out}
    #     return output
    # if len(err) > 0:
    #     output = {'sts': 0, 'rst': err}
    #     return output
    # if out == '':
    #     output = {'sts': 1, 'rst': out}
    #     return output

    if out:
        out = out.decode()
        return out
    elif err:
        err = err.decode()
        return err


#
cmd = 'linstor n l'

print(execute_cmd(cmd))

cmd = 'linstor rd c res_test'

print(execute_cmd(cmd))

# cmd = 'linstor rd d res_test'
# ex_cmd(cmd)
