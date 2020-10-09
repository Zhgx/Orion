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


class Host_create(views.MethodView):

    def get(self):
        if request.method == 'GET':
            host_iqn = request.args.items()
            dict_host_iqn = dict(host_iqn) 
            str_cmd = "python3 vtel_client_main.py iscsi host create %s %s" % (dict_host_iqn["Host_Name"], dict_host_iqn["Host_iqn"])
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class HostGroup_create(views.MethodView):

    def get(self):
        if request.method == 'GET':
            HostGroup = request.args.items()
            dict_HostGroup = dict(HostGroup)
            host = dict_HostGroup['Host'].replace(',', ' ') 
            str_cmd = "python3 vtel_client_main.py iscsi hostgroup create %s %s" % (dict_HostGroup["HostGroup_Name"], host)
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class DiskGroup_create(views.MethodView):

    def get(self):
        if request.method == 'GET':
            diskgroup = request.args.items()
            dict_diskgroup = dict(diskgroup) 
            disk = dict_diskgroup['Disk'].replace(',', ' ')
            str_cmd = "python3 vtel_client_main.py iscsi diskgroup create %s %s" % (dict_diskgroup["DiskGroup_Name"], disk)
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class Map_create(views.MethodView):

    def get(self):
        if request.method == 'GET':
            map_create = request.args.items()
            dict_map_create = dict(map_create) 
            str_cmd = "python3 vtel_client_main.py iscsi map create %s -hg %s -dg %s " % (dict_map_create["Map_Name"], dict_map_create["Host_Group"], dict_map_create["Disk_Group"])
            result = subprocess.getoutput(str_cmd)
        return data(result)

#host
global HOST_RESULT
class oprt_all_host(views.MethodView):
    global HOST_RESULT

    def get(self):
        js = iscsi_interaction.JsonFile()
        HOST_RESULT = js.provide_all_host()
        
        return data("host获取值成功")

    
class all_host_result(views.MethodView):
    global HOST_RESULT
    def get(self):
        return data(HOST_RESULT)
#disk   
global DISK_RESULT
class oprt_all_disk(views.MethodView):
    global DISK_RESULT

    def get(self):
        js = iscsi_interaction.JsonFile()
        DISK_RESULT = js.provide_all_disk()
        return data("disk获取值成功")

    
class all_disk_result(views.MethodView):

    def get(self):
        return data(DISK_RESULT)

#hostgroup
global HOSTGROUP_RESULT
class oprt_all_hg(views.MethodView):
    global HOSTGROUP_RESULT

    def get(self):
        js = iscsi_interaction.JsonFile()
        HOSTGROUP_RESULT = js.provide_all_hostgroup()
        return data("hostgroup获取值成功")

    
class all_hg_result(views.MethodView):

    def get(self):
        return data(HOSTGROUP_RESULT)
    
#diskgroup
global DISKGROUP_RESULT
class oprt_all_dg(views.MethodView):
    global DISKGROUP_RESULT

    def get(self):
        js = iscsi_interaction.JsonFile()
        DISKGROUP_RESULT = js.provide_all_diskgroup()
        return data("diskgroup获取值成功")

    
class all_dg_result(views.MethodView):

    def get(self):
        return data(DISKGROUP_RESULT)
    
    
#map
global MAP_RESULT
class oprt_all_map(views.MethodView):
    global MAP_RESULT

    def get(self):
        js = iscsi_interaction.JsonFile()
        MAP_RESULT = js.provide_all_map()
        return data("map获取值成功")

    
class all_map_result(views.MethodView):

    def get(self):
        return data(MAP_RESULT)
