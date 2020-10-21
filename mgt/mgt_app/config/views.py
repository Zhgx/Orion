# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from mgt_app.config import config_blueprint
from mgt_app.config import model

config_blueprint.add_url_rule('/', view_func=model.Index.as_view('index'))
config_blueprint.add_url_rule('/iscsi', view_func=model.Iscsi.as_view('iSCSI'))
config_blueprint.add_url_rule('/iscsi/map', view_func=model.Iscsi.as_view('iSCSIMap'))
config_blueprint.add_url_rule('/iscsi/map/create', view_func=model.IscsiCreate.as_view('iSCSICreate'))




