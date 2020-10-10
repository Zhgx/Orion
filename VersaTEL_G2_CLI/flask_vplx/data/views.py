# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import views
from flask_vplx.data import datablue
from flask_vplx.data import model

datablue.add_url_rule('/resource_operate', view_func=model.OprtResource.as_view('resource_op_view'))
datablue.add_url_rule('/resource_data', view_func=model.ResourceResult.as_view('resource_data_view'))
 
