# coding:utf-8

from flask import views
from flask_vplx.execution import execution_blue
from flask_vplx.execution import model


# 创建
execution_blue.add_url_rule('/host_create', view_func=model.HostCreate.as_view('host_create'))
execution_blue.add_url_rule('/hostgroup_create', view_func=model.HostGroupCreate.as_view('hostgroup_create'))
execution_blue.add_url_rule('/diskgroup_create', view_func=model.DiskGroupCreate.as_view('diskgroup_create'))
execution_blue.add_url_rule('/map_create', view_func=model.MapCreate.as_view('map_create'))

# host操作/数据
execution_blue.add_url_rule('/oprt_all_host', view_func=model.OprtAllHost.as_view('oprt_all_host'))
execution_blue.add_url_rule('/all_host_result', view_func=model.AllHostResult.as_view('all_host_result'))

# disk 操作/数据
execution_blue.add_url_rule('/oprt_all_disk', view_func=model.OprtAllDisk.as_view('oprt_all_disk'))
execution_blue.add_url_rule('/all_disk_result', view_func=model.AllDiskResult.as_view('all_disk_result'))

# hg 操作/数据
execution_blue.add_url_rule('/oprt_all_hg', view_func=model.OprtAllHg.as_view('oprt_all_hg'))
execution_blue.add_url_rule('/all_hg_result', view_func=model.AllHgResult.as_view('all_hg_result'))

# dg 操作/数据
execution_blue.add_url_rule('/oprt_all_dg', view_func=model.OprtAllDg.as_view('oprt_all_dg'))
execution_blue.add_url_rule('/all_dg_result', view_func=model.AllDgResult.as_view('all_dg_result'))

# map 操作/数据
execution_blue.add_url_rule('/oprt_all_map', view_func=model.OprtAllMap.as_view('oprt_all_map'))
execution_blue.add_url_rule('/all_map_result', view_func=model.AllMapResult.as_view('all_map_result'))
