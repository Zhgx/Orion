
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
    
    
class Resource(views.MethodView):
    def get(self):
        return render_template("Resource.html")
