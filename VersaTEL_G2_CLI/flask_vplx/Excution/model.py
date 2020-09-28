# coding:utf-8
from flask import views,request

class iscsiMapView(views.MethodView):
    def get(self):
        return ("nihao")
