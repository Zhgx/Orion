# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from flask_mgt.show import showblue
from flask_mgt.show import model

showblue.add_url_rule('/', view_func=model.Index.as_view('index'))
showblue.add_url_rule('/stor/resource', view_func=model.Resource.as_view('Resource'))




