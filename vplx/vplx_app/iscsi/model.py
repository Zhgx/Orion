# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
from flask_cors import *
from execute import iscsi
import consts

def cors_data(data_dict):
    response = make_response(jsonify(data_dict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response



def get_request_data():
    if request.method == 'GET':
        str_data = request.args.items()
        dict_data = dict(str_data)
        tid = dict_data['tid']
        # 记录除了tid之后接收到的数据
        logger = consts.glo_log()
        logger.tid = tid
        consts.set_glo_log(logger)
        return dict_data

    
class HostCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        host = dict_data["host_name"]
        iqn = dict_data["host_iqn"]
        logger.write_to_log('OPRT', 'ROUTE', '/host/create', dict_data['ip'], dict_data)
        host_obj = iscsi.Host()
        host_create_results = host_obj.create_host(host, iqn)
        logger.write_to_log('DATA', 'RESULT', 'HostCreate', 'result', host_create_results)
        if host_create_results == True:
            result = "create success"
        else:
            result = "create failed"
        logger.write_to_log('DATA', 'RETURN', 'HostCreate', 'result', result)
        return cors_data(result)


    
class HostGroupCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        host = dict_data['host'].split(',')
        host_group_name = dict_data["host_group_name"]
        logger.write_to_log('OPRT', 'ROUTE', '/hg/create', dict_data['ip'], dict_data)
        host_group_obj = iscsi.HostGroup()
        host_group_create_results = host_group_obj.create_hostgroup(host_group_name, host)
        logger.write_to_log('DATA', 'RESULT', 'HostGroupCreate', 'result', host_group_create_results)
        if host_group_create_results == True:
            result = "create success"
        else:
            result = "create failed"
        logger.write_to_log('DATA', 'RETURN', 'HostGroupCreate', 'result', result)
        return cors_data(result)

    
class DiskGroupCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        disk = dict_data['disk'].split(',')
        logger.write_to_log('OPRT', 'ROUTE', '/dg/create', dict_data['ip'], dict_data)
        disk_group_name = dict_data["disk_group_name"]
        disk_group_obj = iscsi.DiskGroup()

        disk_group_create_results = disk_group_obj.create_diskgroup(disk_group_name, disk)
        logger.write_to_log('DATA', 'RESULT', 'DiskGroupCreate', 'result', disk_group_create_results)
        if disk_group_create_results == True:
            result = "create success"
        else:
            result = "create failed"
        logger.write_to_log('DATA', 'RETURN', 'DiskGroupCreate', 'result', result)
        return cors_data(result)

    
class MapCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        map_name = dict_data["map_name"]
        host_group_name = dict_data["host_group"]
        disk_group_name = dict_data["disk_group"]
        logger.write_to_log('OPRT', 'ROUTE', '/map/create', dict_data['ip'], dict_data)
        map_obj = iscsi.Map()
        map_create_results = map_obj.create_map(map_name, host_group_name,disk_group_name)
        logger.write_to_log('DATA', 'RESULT', 'MapCreate', 'result', map_create_results)
        if map_create_results == True:
            result = "create success"
        else:
            result = "create failed"
        logger.write_to_log('DATA', 'RETURN', 'MapCreate', 'result', result)
        return cors_data(result)


def get_tid():
    if request.method == 'GET':
        str_transaction_id = request.args.items()
        dict_transaction = dict(str_transaction_id)
        return dict_transaction["transaction_id"]

# host
HOST_RESULT = None
def update_host():
    global HOST_RESULT
   
    host = iscsi.Host()
    HOST_RESULT = host.get_all_host()
    
    return True

class OprtAllHost(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('OPRT', 'ROUTE', '/host/show/oprt', dict_data['ip'], '')
        if update_host():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHost', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHost', 'result', '1')
            return cors_data("1")

    
class AllHostResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('DATA', 'ROUTE', '/host/show/data', dict_data['ip'], '')
        if not HOST_RESULT:
            update_host()
        logger.write_to_log('DATA', 'RETURN', 'AllHostResult', 'result', HOST_RESULT)
        return cors_data(HOST_RESULT)


# disk   
DISK_RESULT = None
def update_disk():
    global DISK_RESULT
    
    disk = iscsi.Disk()
    DISK_RESULT = disk.get_all_disk()
    return True

class OprtAllDisk(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('OPRT', 'ROUTE', '/disk/show/oprt', dict_data["ip"], '')
        if update_disk():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDisk', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDisk', 'result', '1')
            return cors_data("1")

    
class AllDiskResult(views.MethodView):
    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('DATA', 'ROUTE', '/disk/show/data', dict_data["ip"], '')
        if not DISK_RESULT:
            update_disk()
        logger.write_to_log('DATA', 'RETURN', 'AllDiskResult', 'result', DISK_RESULT)
        return cors_data(DISK_RESULT)


# hostgroup
HOSTGROUP_RESULT = None
def update_hg():
    global HOSTGROUP_RESULT
    
    host_group = iscsi.HostGroup()
    HOSTGROUP_RESULT = host_group.get_all_hostgroup()
    return True



class OprtAllHg(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('OPRT', 'ROUTE', '/hg/show/oprt', dict_data['ip'], '')
        if update_hg():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHg', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHg', 'result', '1')
            return cors_data("1")


class AllHgResult(views.MethodView):
    
    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('DATA', 'ROUTE', '/hg/show/data', dict_data['ip'], '')
        if not HOSTGROUP_RESULT:
            update_hg()
        logger.write_to_log('DATA', 'RETURN', 'AllHgResult', 'result', HOSTGROUP_RESULT)
        return cors_data(HOSTGROUP_RESULT)

    
# diskgroup
DISKGROUP_RESULT = None

def update_dg():
    global DISKGROUP_RESULT
    
    disk_group = iscsi.DiskGroup()
    DISKGROUP_RESULT = disk_group.get_all_diskgroup()
    return True


class OprtAllDg(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('OPRT', 'ROUTE', '/dg/show/oprt', dict_data['ip'], '')
        if update_dg():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDg', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDg', 'result', '1')
            return cors_data("1")

    
class AllDgResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('DATA', 'ROUTE', '/dg/show/data', dict_data['ip'], '')
        if not DISKGROUP_RESULT:
            update_dg()
        logger.write_to_log('DATA', 'RETURN', 'AllDgResult', 'result',DISKGROUP_RESULT)
        return cors_data(DISKGROUP_RESULT)
    
    
# map
MAP_RESULT = None

def update_map():
    global MAP_RESULT
    
    map = iscsi.Map()
    MAP_RESULT = map.get_all_map()
    return True



class OprtAllMap(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('OPRT', 'ROUTE', '/map/show/oprt', dict_data['ip'], '')
        if update_map():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllMap', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllMap', 'result', '1')
            return cors_data("1")

    
class AllMapResult(views.MethodView):


    def get(self):
        dict_data = get_request_data()
        logger = consts.glo_log()
        logger.write_to_log('DATA', 'ROUTE', '/map/show/data', dict_data['ip'], '')
        if not MAP_RESULT:
           update_map()
        logger.write_to_log('DATA', 'RETURN', 'AllMapResult', 'result', MAP_RESULT)
        return cors_data(MAP_RESULT)
