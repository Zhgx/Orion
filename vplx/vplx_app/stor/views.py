# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import views
from vplx_app.stor import stor_blueprint
from vplx_app.stor import model

stor_blueprint.add_url_rule('/resource/show/oprt', view_func=model.OprtResource.as_view('resource_oprt'))
stor_blueprint.add_url_rule('/resource/show/data', view_func=model.ResourceResult.as_view('resource_data'))
 
