# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import views
from flask_vplx.data import datablue
from flask_vplx.data import model

datablue.add_url_rule('/resource/show/oprt', view_func=model.OprtResource.as_view('resource_oprt'))
datablue.add_url_rule('/resource/show/data', view_func=model.ResourceResult.as_view('resource_data'))
 
