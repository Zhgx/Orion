# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from versatelG2.Show import showblue
from versatelG2.Show import model

showblue.add_url_rule('/', view_func=model.Index.as_view('index'))
showblue.add_url_rule('/iscsi/create', view_func=model.IscsiCreate.as_view('iSCSIcreate'))
showblue.add_url_rule('/resource/show', view_func=model.Resource.as_view('Resource'))




