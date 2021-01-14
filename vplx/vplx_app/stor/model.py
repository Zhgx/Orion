# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, jsonify, render_template, request, make_response, views
import process
import log
                                                                                                                                                                                                         

def cors_data(datadict):
    response = make_response(jsonify(datadict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response

 
def get_request_data():
    if request.method == 'GET':
        str_data = request.args.items()
        dict_data = dict(str_data)
        tid = dict_data['tid']
        # 记录除了tid之后接收到的数据
        logger = log.Log()
        logger.tid = tid
        return dict_data



RESOURCEDICT = None

def get_all_resource():
    global RESOURCEDICT
    pc = process.Process_data()
    RESOURCEDICT = pc.process_data_resource()
    return True

class OprtResource(views.MethodView):  

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/resource/show/oprt', dict_data['ip'], '')
        if get_all_resource():
            logger.write_to_log('DATA', 'RETURN', 'OprtResource', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtResource', 'result', '1')
            return cors_data("1")

    
class ResourceResult(views.MethodView):  

    def get(self):
        # get_request_data()
        # logger = log.Log()
        # logger.write_to_log('DATA', 'ROUTE', '/resource/show/data', dict_data['ip'], '')
        if not RESOURCEDICT:
            get_all_resource()
        # logger.write_to_log('DATA', 'RETURN', 'ResourceResult', 'result', RESOURCEDICT)
        return cors_data(RESOURCEDICT)

