
# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''
from flask import Flask, jsonify, render_template, request, make_response, views
import log

def cors_data(data_dict):
    response = make_response(jsonify(data_dict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


class Index(views.MethodView):

    def get(self):
        return render_template("index.html")

class ISCSIWrite(views.MethodView):

    def get(self):
        if request.method == 'GET':
            str_host = request.args.to_dict()
            logger = log.Log('username',str_host["tid"],file_name=log.WEB_LOG_NAME)
            logger.write_to_log('t1', 't2', 'd1', 'd2', str_host["data_host"])
        return cors_data("success") 

    
class IndexPreview(views.MethodView):

    def get(self):
        return render_template("index_preview.html")

    
class IscsiCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_create.html")


class IscsiAll(views.MethodView):

    def get(self):
        return render_template("iscsi_all.html")
    
    
class IscsiMap(views.MethodView):

    def get(self):
        return render_template("iscsi_map.html")
    
    
class IscsiHost(views.MethodView):

    def get(self):
        return render_template("iscsi_host.html")
    
    
class IscsiHostGroup(views.MethodView):

    def get(self):
        return render_template("iscsi_hostgroup.html")
    
    
class IscsiDiskGroup(views.MethodView):

    def get(self):
        return render_template("iscsi_diskgroup.html")
    
