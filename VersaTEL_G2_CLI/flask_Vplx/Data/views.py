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
 