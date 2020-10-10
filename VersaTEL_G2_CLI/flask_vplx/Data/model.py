# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, jsonify, render_template, request, make_response,views
import VersaTELSocket as vst
import json
from flask_cors import *
import Process

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
        print("nodedict:",nodedict)
        return data(nodedict)
 
global resourcedict
class R_OP_View(views.MethodView):  
    def get(self):
        global resourcedict
        pc = Process.Process_data()
        resourcedict = pc.process_data_resource()
        return data("数据获取成功")
    
class R_D_View(views.MethodView):  
    def get(self):
        global resourcedict
        return data(resourcedict)

