
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
    
class IndexStor(views.MethodView):
    def get(self):
        return render_template("index_linstor_preview.html")
    
    
class LINSTORCreate(views.MethodView):
    def get(self):
        return render_template("LINSTOR_create.html")
    
class Resource(views.MethodView):
    def get(self):
        return render_template("Resource.html")
    
class Node(views.MethodView):
    def get(self):
        return render_template("Node.html")
    
class Storagepool(views.MethodView):
    def get(self):
        return render_template("Storagepool.html")
