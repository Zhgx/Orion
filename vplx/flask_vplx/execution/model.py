# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
import json
import subprocess
from flask_cors import *
from execute import iscsi
import time
import log
import consts

def cors_data(data_dict):
    response = make_response(jsonify(data_dict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response
    
class HostCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            str_host = request.args.items()
            dict_host = dict(str_host)
            tid = dict_host['transaction_id']
            logger = consts.glo_log()
            logger.transaction_id = tid
            host = dict_host["host_name"]
            iqn = dict_host["host_iqn"]
            host_obj = iscsi.Host()
            print(host_obj.get_all_host())
            host_create_results = host_obj.create_host(host, iqn)
            if host_create_results == True:
                result = "create success"
            else:
                result = "create failed"
        return cors_data(result)

    
class HostGroupCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            hostgroup = request.args.items()
            dict_hostgroup = dict(hostgroup)
            tid = dict_hostgroup['transaction_id']
            logger = consts.glo_log()
            logger.transaction_id = tid
            host = dict_hostgroup['host'].split(',')
            host_group_name = dict_hostgroup["host_group_name"]
            host_group_obj = iscsi.HostGroup()
            host_group_create_results = host_group_obj.create_hostgroup(host_group_name, host)
            if host_group_create_results == True:
                result = "create success"
            else:
                result = "create failed"
        return cors_data(result)

    
class DiskGroupCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            diskgroup = request.args.items()
            dict_diskgroup = dict(diskgroup) 
            tid = dict_diskgroup['transaction_id']
            logger = consts.glo_log()
            logger.transaction_id = tid
            disk = dict_diskgroup['disk'].split(',')
            disk_group_name = dict_diskgroup["disk_group_name"]
            disk_group_obj = iscsi.DiskGroup()
            
            disk_group_create_results = disk_group_obj.create_diskgroup(disk_group_name, disk)
            if disk_group_create_results == True:
                result = "create success"
            else:
                result = "create failed"
        return cors_data(result)

    
class MapCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            map = request.args.items()
            dict_map = dict(map)
            tid = dict_map['transaction_id']
            logger = consts.glo_log()
            logger.transaction_id = tid
            map_name = dict_map["map_name"]
            host_group_name = dict_map["host_group"]
            disk_group_name = dict_map["disk_group"] 
            map_obj = iscsi.Map()
            map_create_results = map_obj.create_map(map_name, host_group_name,disk_group_name)
            if map_create_results == True:
                result = "create success"
            else:
                result = "create failed"
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
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if update_host():
            return cors_data("0")
        else:
            return cors_data("1")

    
class AllHostResult(views.MethodView):

    def get(self):
        if not HOST_RESULT:
            
            update_host()
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
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if update_disk():
            return cors_data("0")
        else:
            return cors_data("1")

    
class AllDiskResult(views.MethodView):

    def get(self):
        if not DISK_RESULT:
            update_disk()
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
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if update_hg():
            return cors_data("0")
        else:
            return cors_data("1")


class AllHgResult(views.MethodView):
    
    def get(self):
        if not HOSTGROUP_RESULT:
            update_hg()
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
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if update_dg():
            return cors_data("0")
        else:
            return cors_data("1")

    
class AllDgResult(views.MethodView):

    def get(self):
        if not DISKGROUP_RESULT:
            update_dg() 
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
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if update_map():
            return cors_data("0")
        else:
            return cors_data("1")

    
class AllMapResult(views.MethodView):

    def get(self):
        if not MAP_RESULT:
           update_map() 
        return cors_data(MAP_RESULT)
