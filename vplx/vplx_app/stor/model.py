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
import consts
                                                                                                                                                                                                         

def cors_data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response

 
def get_tid():
    if request.method == 'GET':
        str_transaction_id = request.args.items()
        dict_transaction = dict(str_transaction_id)
        return dict_transaction["transaction_id"]


RESOURCEDICT = None

def get_all_resource():
    global RESOURCEDICT
    pc = process.Process_data()
    RESOURCEDICT = pc.process_data_resource()
    return True

class OprtResource(views.MethodView):  

    def get(self):
        tid = get_tid()
        logger = consts.glo_log()
        logger.transaction_id = tid
        if get_all_resource():
            return cors_data("0")
        else:
            return cors_data("1")

    
class ResourceResult(views.MethodView):  

    def get(self):
        if not RESOURCEDICT:
            get_all_resource()
        return cors_data(RESOURCEDICT)

