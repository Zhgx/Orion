# coding:utf-8
'''
Created on 2020/3/2
@author: Paul
@note: data
'''

from flask import Flask,views
from mgt_app.iscsi import iscsi_blueprint
from mgt_app.iscsi import model

iscsi_blueprint.add_url_rule('/', view_func=model.Index.as_view('index'))

iscsi_blueprint.add_url_rule('/iscsi/create', view_func=model.IscsiCreate.as_view('iscsi_create'))

iscsi_blueprint.add_url_rule('/iscsi/map/create', view_func=model.IscsiMapCreate.as_view('iscsi_map_create'))
# iscsi_blueprint.add_url_rule('/iscsi/map/show', view_func=model.IscsiMapShow.as_view('iscsi_map_show'))
# iscsi_blueprint.add_url_rule('/iscsi/map/delete', view_func=model.IscsiMapDelete.as_view('iscsi_map_delete'))

iscsi_blueprint.add_url_rule('/iscsi/host/create', view_func=model.IscsiHostCreate.as_view('iscsi_host_create'))
# iscsi_blueprint.add_url_rule('/iscsi/host/show', view_func=model.IscsiHostShow.as_view('iscsi_host_show'))
# iscsi_blueprint.add_url_rule('/iscsi/host/delete', view_func=model.IscsiHostDelete.as_view('iscsi_host_delete'))

iscsi_blueprint.add_url_rule('/iscsi/hostgroup/create', view_func=model.IscsiHostGroupCreate.as_view('iscsi_hostgroup_create'))
# iscsi_blueprint.add_url_rule('/iscsi/hostgroup/show', view_func=model.IscsiHostGroupShow.as_view('iscsi_hostgroup_show'))
# iscsi_blueprint.add_url_rule('/iscsi/hostgroup/delete', view_func=model.IscsiHostGroupDelete.as_view('iscsi_hostgroup_delete'))

iscsi_blueprint.add_url_rule('/iscsi/diskgroup/create', view_func=model.IscsiDiskGroupCreate.as_view('iscsi_diskgroup_create'))
# iscsi_blueprint.add_url_rule('/iscsi/diskgroup/show', view_func=model.IscsiDiskGroupShow.as_view('iscsi_hostgroup_show'))
# iscsi_blueprint.add_url_rule('/iscsi/diskgroup/delete', view_func=model.IscsiDiskGroupDelete.as_view('iscsi_hostgroup_delete'))




