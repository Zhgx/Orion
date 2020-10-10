# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
import json
import subprocess
from flask_cors import *
import iscsi_interaction


def data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


class HostCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            host_iqn = request.args.items()
            dict_host_iqn = dict(host_iqn) 
            str_cmd = "python3 vtel_client_main.py iscsi host create %s %s" % (dict_host_iqn["Host_Name"], dict_host_iqn["Host_iqn"])
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class HostGroupCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            HostGroup = request.args.items()
            dict_HostGroup = dict(HostGroup)
            host = dict_HostGroup['Host'].replace(',', ' ') 
            str_cmd = "python3 vtel_client_main.py iscsi hostgroup create %s %s" % (dict_HostGroup["HostGroup_Name"], host)
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class DiskGroupCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            diskgroup = request.args.items()
            dict_diskgroup = dict(diskgroup) 
            disk = dict_diskgroup['Disk'].replace(',', ' ')
            str_cmd = "python3 vtel_client_main.py iscsi diskgroup create %s %s" % (dict_diskgroup["DiskGroup_Name"], disk)
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class MapCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            map_create = request.args.items()
            dict_map_create = dict(map_create) 
            str_cmd = "python3 vtel_client_main.py iscsi map create %s -hg %s -dg %s " % (dict_map_create["Map_Name"], dict_map_create["Host_Group"], dict_map_create["Disk_Group"])
            result = subprocess.getoutput(str_cmd)
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
        return data("map获取值成功")

    
class AllMapResult(views.MethodView):

    def get(self):
        return data(MAP_RESULT)
