# coding:utf-8

from flask import views
from flask_vplx.execution import execution_blueprint
from flask_vplx.execution import model


# 创建
execution_blueprint.add_url_rule('/host/create', view_func=model.HostCreate.as_view('host_create'))
execution_blueprint.add_url_rule('/hg/create', view_func=model.HostGroupCreate.as_view('hostgroup_create'))
execution_blueprint.add_url_rule('/dg/create', view_func=model.DiskGroupCreate.as_view('diskgroup_create'))
execution_blueprint.add_url_rule('/map/create', view_func=model.MapCreate.as_view('map_create'))

# host操作/数据
execution_blueprint.add_url_rule('/host/show/oprt', view_func=model.OprtAllHost.as_view('oprt_all_host'))
execution_blueprint.add_url_rule('/host/show/data', view_func=model.AllHostResult.as_view('all_host_result'))

# disk 操作/数据
execution_blueprint.add_url_rule('/disk/show/oprt', view_func=model.OprtAllDisk.as_view('oprt_all_disk'))
execution_blueprint.add_url_rule('/disk/show/data', view_func=model.AllDiskResult.as_view('all_disk_result'))

# hg 操作/数据
execution_blueprint.add_url_rule('/hg/show/oprt', view_func=model.OprtAllHg.as_view('oprt_all_hg'))
execution_blueprint.add_url_rule('/hg/show/data', view_func=model.AllHgResult.as_view('all_hg_result'))

# dg 操作/数据
execution_blueprint.add_url_rule('/dg/show/oprt', view_func=model.OprtAllDg.as_view('oprt_all_dg'))
execution_blueprint.add_url_rule('/dg/show/data', view_func=model.AllDgResult.as_view('all_dg_result'))

# map 操作/数据
execution_blueprint.add_url_rule('/map/show/oprt', view_func=model.OprtAllMap.as_view('oprt_all_map'))
execution_blueprint.add_url_rule('/map/show/data', view_func=model.AllMapResult.as_view('all_map_result'))
