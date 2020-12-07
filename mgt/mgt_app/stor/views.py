# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from mgt_app.stor import stor_blueprint
from mgt_app.stor import model

stor_blueprint.add_url_rule('/', view_func=model.Index.as_view('index'))
stor_blueprint.add_url_rule('/index/stor', view_func=model.IndexStor.as_view('indexstor'))
stor_blueprint.add_url_rule('/stor/resource/show', view_func=model.Resource.as_view('resource'))




