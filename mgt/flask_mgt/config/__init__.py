# coding:utf-8

'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,Blueprint

configblue = Blueprint("configblue", __name__)

from flask_mgt.config import views