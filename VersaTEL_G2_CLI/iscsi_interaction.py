# coding=utf-8
import consts
import log
import sys
import sundry as s
from execute.iscsi import Disk
from execute.iscsi import Host
from execute.iscsi import HostGroup
from execute.iscsi import DiskGroup
from execute.iscsi import Map


class JsonFile(object):

    def __init__(self):
        consts._init()
        username = s.get_username()
        transaction_id = sys.argv[-1] if '-gui' in sys.argv else s.create_transaction_id()
        logger = log.Log(username, transaction_id)
        consts.set_glo_log(logger)

    def provide_all_disk(self):
        disk = Disk()
        return disk.get_all_disk()

    def provide_all_host(self):
        host = Host()
        return host.get_all_host()

    def provide_all_diskgroup(self):
        dg = DiskGroup()
        return dg.get_all_diskgroup()

    def provide_all_hostgroup(self):
        hg = HostGroup()
        return hg.get_all_hostgroup()

    def provide_all_map(self):
        map = Map()
        return map.get_all_map()


if __name__ == '__main__':
    pass
