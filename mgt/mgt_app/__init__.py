# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data post
'''

from flask import Flask, Blueprint


def create_app():
    
    app = Flask(__name__)

    # 将蓝图注册到app
    from mgt_app.stor import stor_blueprint
    from mgt_app.iscsi import iscsi_blueprint
    app.register_blueprint(stor_blueprint)
    app.register_blueprint(iscsi_blueprint)
    return app
