# coding:utf-8
from flask import views,request

class iscsiMapView(views.MethodView):
        if request.method == 'GET':
            data_all = request.args.items()
            for i in data_all:
                data_one_dict = {i[0]:i[1]}
                data.update(data_one_dict)
                print(data)
