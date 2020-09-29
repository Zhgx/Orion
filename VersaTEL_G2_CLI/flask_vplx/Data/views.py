# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import views
from flask_vplx.Data import datablue
from flask_vplx.Data import model

datablue.add_url_rule('/node', view_func=model.nodeView.as_view('node_view'))
datablue.add_url_rule('/resource_operate', view_func=model.R_OP_View.as_view('resource_op_view'))
datablue.add_url_rule('/resource_data', view_func=model.R_D_View.as_view('resource_data_view'))
 
