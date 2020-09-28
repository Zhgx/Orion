# coding:utf-8

from flask import Flask,Blueprint

excution_blue = Blueprint("excution_blue", __name__)

from flask_vplx.Excution import views
# from . import views