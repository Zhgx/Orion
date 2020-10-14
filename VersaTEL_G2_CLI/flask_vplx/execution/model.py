# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
import json
import subprocess
from flask_cors import *
import iscsi_interaction
from execute import iscsi
import time


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
            host = dict_host["Host_Name"]
            iqn = dict_host["Host_iqn"]
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
            host = dict_hostgroup['Host'].split(',')
            host_group_name = dict_hostgroup["HostGroup_Name"]
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
            disk = dict_diskgroup['Disk'].split(',')
            disk_group_name = dict_diskgroup["DiskGroup_Name"]
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
            map_name = dict_map["Map_Name"]
            host_group_name = dict_map["Host_Group"]
            disk_group_name = dict_map["Disk_Group"] 
            map_obj = iscsi.Map()
            map_create_results = map_obj.create_map(map_name, host_group_name,disk_group_name)
            if map_create_results == True:
                result = "create success"
            else:
                result = "create failed"
        return cors_data(result)


# host
HOST_RESULT = None
def update_host():
    global HOST_RESULT
    js = iscsi_interaction.JsonConfig()
    HOST_RESULT = js.provide_all_host()
    return HOST_RESULT

class OprtAllHost(views.MethodView):

    def get(self):
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
    js = iscsi_interaction.JsonConfig()
    DISK_RESULT = js.provide_all_disk()
    return DISK_RESULT

class OprtAllDisk(views.MethodView):

    def get(self):
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
    js = iscsi_interaction.JsonConfig()
    HOSTGROUP_RESULT = js.provide_all_hostgroup()
    return HOSTGROUP_RESULT



class OprtAllHg(views.MethodView):

    def get(self):
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
    js = iscsi_interaction.JsonConfig()
    DISKGROUP_RESULT = js.provide_all_diskgroup()
    return DISKGROUP_RESULT


class OprtAllDg(views.MethodView):

    def get(self):
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
    js = iscsi_interaction.JsonConfig()
    MAP_RESULT = js.provide_all_map()
    return MAP_RESULT



class OprtAllMap(views.MethodView):

    def get(self):
        
        if updata_map():
            return cors_data("0")
        else:
            return cors_data("1")

    
class AllMapResult(views.MethodView):

    def get(self):
        if not MAP_RESULT:
           update_map() 
        return cors_data(MAP_RESULT)
