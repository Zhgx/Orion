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
    from mgt_app.show import showblue
    from mgt_app.config import configblue
    app.register_blueprint(showblue,url_prefix="/show")
    app.register_blueprint(configblue,url_prefix="/create")
    return app
