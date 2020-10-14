# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
import json
import subprocess
from flask_cors import *
import iscsi_interaction
from execute import iscsi


def data(datadict):
    response = make_response(jsonify(datadict))
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
            host_create_results = host_obj.create_host(host, iqn)
            if host_create_results == True:
                result = "create success"
            else:
                result = "create failed"
        return data(result)

    
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
        return data(result)

    
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
        return data(result)

    
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
        return data(result)


# host
global HOST_RESULT


class OprtAllHost(views.MethodView):

    def get(self):
        global HOST_RESULT
        js = iscsi_interaction.JsonFile()
        HOST_RESULT = js.provide_all_host()
        
        return data("host获取值成功")

    
class AllHostResult(views.MethodView):

    def get(self):
        return data(HOST_RESULT)


# disk   
global DISK_RESULT


class OprtAllDisk(views.MethodView):

    def get(self):
        global DISK_RESULT
        js = iscsi_interaction.JsonFile()
        DISK_RESULT = js.provide_all_disk()
        return data("disk获取值成功")

    
class AllDiskResult(views.MethodView):

    def get(self):
        return data(DISK_RESULT)


# hostgroup
global HOSTGROUP_RESULT


class OprtAllHg(views.MethodView):

    def get(self):
        global HOSTGROUP_RESULT
        js = iscsi_interaction.JsonFile()
        HOSTGROUP_RESULT = js.provide_all_hostgroup()
        return data("hostgroup获取值成功")


class AllHgResult(views.MethodView):
    
    def get(self):
        return data(HOSTGROUP_RESULT)

    
# diskgroup
global DISKGROUP_RESULT


class OprtAllDg(views.MethodView):

    def get(self):
        global DISKGROUP_RESULT
        js = iscsi_interaction.JsonFile()
        DISKGROUP_RESULT = js.provide_all_diskgroup()
        return data("diskgroup获取值成功")

    
class AllDgResult(views.MethodView):

    def get(self):
        return data(DISKGROUP_RESULT)
    
    
# map
global MAP_RESULT


class OprtAllMap(views.MethodView):

    def get(self):
        global MAP_RESULT
        js = iscsi_interaction.JsonFile()
        MAP_RESULT = js.provide_all_map()
        if not MAP_RESULT:
            MAP_RESULT = "暂未创建Map"
        return data("map获取值成功")

    
class AllMapResult(views.MethodView):

    def get(self):
              
        return data(MAP_RESULT)
