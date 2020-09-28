# coding:utf-8

from flask import views
from flask_vplx.Excution import excution_blue
from flask_vplx.Excution import model

excution_blue.add_url_rule('/iscsi_map', view_func=model.iscsiMapView.as_view('map_view'))
