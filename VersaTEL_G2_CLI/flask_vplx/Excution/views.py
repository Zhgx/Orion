# coding:utf-8

from flask import views
from flask_vplx.Excution import excution_blue
from flask_vplx.Excution import model
#创建
excution_blue.add_url_rule('/Host_create', view_func=model.Host_create.as_view('Host_create'))
excution_blue.add_url_rule('/HostGroup_create', view_func=model.HostGroup_create.as_view('HostGroup_create'))
excution_blue.add_url_rule('/DiskGroup_create', view_func=model.DiskGroup_create.as_view('DiskGroup_create'))
excution_blue.add_url_rule('/Map_create', view_func=model.Map_create.as_view('Map_create'))

#host操作/数据
excution_blue.add_url_rule('/oprt_all_host', view_func=model.oprt_all_host.as_view('oprt_all_host'))
excution_blue.add_url_rule('/all_host_result', view_func=model.all_host_result.as_view('all_host_result'))

#disk 操作/数据
excution_blue.add_url_rule('/oprt_all_disk', view_func=model.oprt_all_disk.as_view('oprt_all_disk'))
excution_blue.add_url_rule('/all_disk_result', view_func=model.all_disk_result.as_view('all_disk_result'))

#hg 操作/数据
excution_blue.add_url_rule('/oprt_all_hg', view_func=model.oprt_all_hg.as_view('oprt_all_hg'))
excution_blue.add_url_rule('/all_hg_result', view_func=model.all_hg_result.as_view('all_hg_result'))

#dg 操作/数据
excution_blue.add_url_rule('/oprt_all_dg', view_func=model.oprt_all_dg.as_view('oprt_all_dg'))
excution_blue.add_url_rule('/all_dg_result', view_func=model.all_dg_result.as_view('all_dg_result'))

#map 操作/数据
excution_blue.add_url_rule('/oprt_all_map', view_func=model.oprt_all_map.as_view('oprt_all_map'))
excution_blue.add_url_rule('/all_map_result', view_func=model.all_map_result.as_view('all_map_result'))
