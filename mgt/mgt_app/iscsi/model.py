
# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask, render_template, views


class Index(views.MethodView):

    def get(self):
        return render_template("index.html")


    
class IscsiCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_create.html")
    
    
class IscsiMapCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_map_create.html")
    
    
class IscsiHostCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_host_create.html")
    
    
class IscsiHostGroupCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_hostgroup_create.html")
    
    
class IscsiDiskGroupCreate(views.MethodView):

    def get(self):
        return render_template("iscsi_diskgroup_create.html")
    
