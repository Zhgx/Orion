# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from versatelG2.Show import showblue
from versatelG2.Show import model

showblue.add_url_rule('/', view_func=model.Index.as_view('indexview'))
showblue.add_url_rule('/iSCSI_create', view_func=model.iSCSICreate.as_view('iSCSIcreateview'))
showblue.add_url_rule('/Resource', view_func=model.Resource.as_view('Resourceview'))




