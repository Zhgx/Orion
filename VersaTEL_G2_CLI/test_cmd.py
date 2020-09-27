import subprocess
import time
import re


def execute_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE, shell=True)
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
# #
# cmd = 'linstor n l'
#
# print(execute_cmd(cmd))
#
# cmd = 'linstor rd c res_test'
#
# print(execute_cmd(cmd))
#
# # cmd = 'linstor rd d res_test'
# # ex_cmd(cmd)


class LVM():
    def __init__(self):
        self.data_vg = self.get_vg()
        self.data_lv = self.get_thinlv()

    def get_vg(self):
        cmd = 'vgs'
        result = subprocess.check_output(cmd, shell=True)
        if result:
            return result.decode()

    def get_thinlv(self):
        cmd = 'lvs'
        result = subprocess.check_output(cmd, shell=True)
        if result:
            return result.decode()

    def refine_thinlv(self):
        all_lv = self.data_vg.splitlines()
        list_thinlv = []
        re_ = re.compile(
            r'\s*(\S*)\s*(\S*)\s*\S*\s*(\S*)\s*\S*\s*\S*\s*\S*\s*?')
        for one in all_lv:
            if 'twi' in one:
                thinlv_one = re_.findall(one)
                list_thinlv.append(list(thinlv_one[0]))
        return list_thinlv

    def refine_vg(self):
        all_vg = self.data_lv.splitlines()
        list_vg = []
        re_ = re.compile(
            r'\s*(\S*)\s*\S*\s*\S*\s*\S*\s*\S*\s*(\S*)\s*(\S*)\s*?')
        for one in all_vg[1:]:
            vg_one = re_.findall(one)
            list_vg.append(list(vg_one[0]))
        return list_vg

    def thinlv_exists(self):
        all_lv_list = self.data_lv.splitlines()[1:]
        print(all_lv_list)
        for one in all_lv_list:
            print(one)
            if 'drbdpool' and 'wi' in one:
                print(one)


import sqlite3


class DBtest():
    def __init__(self):
        # linstor.db
        self.con = sqlite3.connect("linstordb.db", check_same_thread=False)
        self.cur = self.con.cursor()

    def sql_fetch_all(self, sql):
        self.cur.execute(sql)
        date_set = self.cur.fetchall()
        return list(date_set)

    def select_data(self):
        # sql = f'SELECT {",".join(data)} FROM {table} WHERE {limit}'
        sql = f'SELECT nodetb.Node,storagepooltb.StoragePool,Resource,DeviceName FROM nodetb inner join resourcetb on nodetb.Node = resourcetb.Node inner join storagepooltb on resourcetb.StoragePool = storagepooltb.StoragePool'
        return self.sql_fetch_all(sql)


# import pprint
# db = DBtest()
# pprint.pprint(db.select_data())
