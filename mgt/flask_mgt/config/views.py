# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from flask_mgt.config import configblue
from flask_mgt.config import model

configblue.add_url_rule('/', view_func=model.Index.as_view('index'))
configblue.add_url_rule('/iscsi/map', view_func=model.IscsiCreate.as_view('iSCSIcreate'))




