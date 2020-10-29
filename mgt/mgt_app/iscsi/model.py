
# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, render_template, views,request


class Index(views.MethodView):

    def get(self):
        return render_template("index.html")

class ISCSIWrite(views.MethodView):

    def get(self):
        if request.method == 'GET':
            str_host = request.args.items()
            dict_host = dict(str_host)
            print(dict_host["time"])
            print(dict_host["tid"])
            print(dict_host["data_host[hostiqn]"])
        return "成功" 

    
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
    
