# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, jsonify, render_template, request, make_response, views
import json
from flask_cors import *
import process
import log


def cors_data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response

 
def get_tid():
    str_transaction_id = request.args.items()
    dict_transaction_id = dict(transaction_id)
    return dict_transaction["transaction_id"]

 
RESOURCEDICT = None


class OprtResource(views.MethodView):  

    def get(self):
        global RESOURCEDICT
        if request.method == 'GET':
            tid = get_tid()
            log.set_web_logger(tid)
            pc = process.Process_data()
            RESOURCEDICT = pc.process_data_resource()
        return cors_data("数据获取成功")

    
class ResourceResult(views.MethodView):  

    def get(self):
        if not RESOURCEDICT:
            pc = process.Process_data()
            RESOURCEDICT = pc.process_data_resource()
        return cors_data(RESOURCEDICT)

