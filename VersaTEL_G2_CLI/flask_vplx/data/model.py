# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, jsonify, render_template, request, make_response,views
import json
from flask_cors import *
import process

def data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response
 
global RESOURCEDICT
class OprtResource(views.MethodView):  
    def get(self):
        global RESOURCEDICT
        pc = Process.Process_data()
        RESOURCEDICT = pc.process_data_resource()
        return data("数据获取成功")
    
class ResourceResult(views.MethodView):  
    def get(self):
        return data(RESOURCEDICT)

