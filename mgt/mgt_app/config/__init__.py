# coding:utf-8

'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,Blueprint

config_blueprint = Blueprint("config_blueprint", __name__,template_folder='templates')

from mgt_app.config import views