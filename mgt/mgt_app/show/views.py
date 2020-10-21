# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from mgt_app.show import show_blueprint
from mgt_app.show import model

show_blueprint.add_url_rule('/', view_func=model.Index.as_view('index'))
show_blueprint.add_url_rule('/stor', view_func=model.Stor.as_view('Stor'))
show_blueprint.add_url_rule('/stor/resource', view_func=model.Stor.as_view('StorResource'))
show_blueprint.add_url_rule('/stor/resource/show', view_func=model.Resource.as_view('Resource'))




