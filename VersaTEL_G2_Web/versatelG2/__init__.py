# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data post
'''

from flask import Flask, Blueprint

from versatelG2.Show import showblue

app = Flask(__name__)

# 将蓝图注册到app
app.register_blueprint(showblue)
