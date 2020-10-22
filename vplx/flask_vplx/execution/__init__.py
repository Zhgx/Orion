# coding:utf-8

from flask import Flask,Blueprint

execution_blueprint = Blueprint("execution_blueprint", __name__)

from flask_vplx.execution import views
# from . import views