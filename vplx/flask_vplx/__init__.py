# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data post
'''

from flask import Flask, Blueprint

from flask_vplx.data import datablue
from flask_vplx.execution import execution_blue

app = Flask(__name__)

# 将蓝图注册到app
app.register_blueprint(datablue,)
app.register_blueprint(execution_blue)
