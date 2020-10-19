# coding:utf-8

from flask import Flask,Blueprint

execution_blue = Blueprint("execution_blue", __name__)

from flask_vplx.execution import views
# from . import views