# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, jsonify, render_template, request, make_response, views
import VersaTELSocket as vst
import json
from flask_cors import *
import Process
global lvm
global sp
global node_create
global node_num


def data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


class nodeView(views.MethodView):

    def get(self):
        pc = Process.Process_data()
        nodedict = pc.process_data_node()
        return data(nodedict)

    
resource_data = {'data': [{'resource': 'res_a', 'mirror_way': 1, 'size': '12MiB', 'device_name': '/dev/drbd1000', 'used': 'Unused', 'mirror_way_son': [{'node_name': 'ubuntu', 'stp_name': 'pool_a', 'drbd_role': 'secondary', 'status': 'UpToDate'}]}, {'resource': 'res_b', 'mirror_way': 1, 'size': '12MiB', 'device_name': '/dev/drbd1001', 'used': 'Unused', 'mirror_way_son': [{'node_name': 'ubuntu', 'stp_name': 'pool_a', 'drbd_role': 'secondary', 'status': 'UpToDate'}]}, {'resource': 'res_c', 'mirror_way': 1, 'size': '12MiB', 'device_name': '/dev/drbd1002', 'used': 'Unused', 'mirror_way_son': [{'node_name': 'ubuntu', 'stp_name': 'pool_a', 'drbd_role': 'secondary', 'status': 'UpToDate'}]}, {'resource': 'res_d', 'mirror_way': 1, 'size': '12MiB', 'device_name': '/dev/drbd1003', 'used': 'Unused', 'mirror_way_son': [{'node_name': 'ubuntu', 'stp_name': 'pool_a', 'drbd_role': 'secondary', 'status': 'UpToDate'}]}, {'resource': 'res_e', 'mirror_way': 1, 'size': '12MiB', 'device_name': '/dev/drbd1004', 'used': 'Unused', 'mirror_way_son': [{'node_name': 'ubuntu', 'stp_name': 'pool_a', 'drbd_role': 'secondary', 'status': 'UpToDate'}]}]}
class resourceView(views.MethodView):  
    def get(self):
        return data(resource_data)

    
class storagepoolView(views.MethodView):  

    def get(self):
        pc = Process.Process_data()
        spdict = pc.process_data_stp()
        return data(spdict)

    
class iSCSIView(views.MethodView):  

    def get(self):
        str_cmd = "python3 vtel.py iscsi show js" 
        str_cmd = str_cmd.encode()
        CLI_result = vst.conn(str_cmd)
        return data(CLI_result)


class LINSTORView(views.MethodView):

    def get(self):
        global lvm
        global sp
        global node_create
        global node_num

        pc = Process.Process_data()
        lvm = pc.get_option_lvm()
        sp = pc.get_option_sp()
        node_create = pc.get_option_node()
        node_num = pc.get_option_nodenum()
        return 'Test'


class lvmView(views.MethodView):  

    def get(self):
        global lvm
        return data(lvm)

 
class spView(views.MethodView):  

    def get(self):
        global sp
        return data(sp)

    
class nodecreateView(views.MethodView):  

    def get(self):
        global node_create
        return data(node_create)


class nodenumView(views.MethodView):  

    def get(self):
        global node_num
        return data(node_num)

