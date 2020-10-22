# coding:utf-8
'''
Created on 2020/1/5
@author: Paul
@note: data post
'''
from flask import Flask,Blueprint

data_blueprint = Blueprint("data_blueprint", __name__)

# from . import views
from flask_vplx.data import views