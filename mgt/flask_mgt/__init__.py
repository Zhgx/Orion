# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data post
'''

from flask import Flask, Blueprint

from flask_mgt.show import showblue
from flask_mgt.config import configblue

app = Flask(__name__)

# 将蓝图注册到app
app.register_blueprint(showblue,url_prefix="/show")
app.register_blueprint(configblue,url_prefix="/create")
