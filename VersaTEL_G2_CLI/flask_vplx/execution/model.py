# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
import json
import subprocess
from flask_cors import *
import iscsi_interaction
import time
import consts


def data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response

global TEANSACTION_ID_RESULT

class TransactionId(views.MethodView):

    def get(self):
        global TEANSACTION_ID_RESULT
        if request.method == 'GET':
            print('get_id_start')
            consts._init()
            transaction_id = request.args.items()
            dict_transaction = dict(transaction_id)
            transaction_id_result = dict_transaction["transactionid"]
            consts.set_glo_tsc_id(transaction_id_result)
            print("transaction_id:",transaction_id_result) 
            hint = "success"
        return data(hint)
    
class HostCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            host = request.args.items()
            dict_host = dict(host) 
            str_cmd = "python3 vtel_client_main.py iscsi host create %s %s" % (dict_host["Host_Name"], dict_host["Host_iqn"])
            result = subprocess.getoutput(str_cmd)
        return data(result)

    
class HostGroupCreate(views.MethodView):

    def get(self):
        if request.method == 'GET':
            hostgroup = request.args.items()
            dict_hostgroup = dict(hostgroup)
            host = dict_hostgroup['Host'].replace(',', ' ') 
            str_cmd = "python3 vtel_client_main.py iscsi hostgroup create %s %s" % (dict_hostgroup["HostGroup_Name"], host)
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
            map = request.args.items()
            dict_map = dict(map) 
            str_cmd = "python3 vtel_client_main.py iscsi map create %s -hg %s -dg %s " % (dict_map["Map_Name"], dict_map["Host_Group"], dict_map_create["Disk_Group"])
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
