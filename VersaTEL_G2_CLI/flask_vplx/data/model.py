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


def data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response

 
def get_tid():
    transaction_id = request.args.items()
    dict_transaction = dict(transaction_id)
    transaction_id_result = dict_transaction["transactionid"]
    print("transaction_id_result:", transaction_id_result)
    return transaction_id_result

 
global RESOURCEDICT


class OprtResource(views.MethodView):  

    def get(self):
        global RESOURCEDICT
        if request.method == 'GET':
            tid = get_tid()
            pc = process.Process_data(tid)
            RESOURCEDICT = pc.process_data_resource()
        return data("数据获取成功")

    
class ResourceResult(views.MethodView):  

    def get(self):
        return data(RESOURCEDICT)

