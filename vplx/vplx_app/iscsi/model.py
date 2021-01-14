# coding:utf-8
from flask import Flask, jsonify, render_template, request, make_response, views
from flask_cors import *
from execute import iscsi
import iscsi_json
import consts
import log


def cors_data(data_dict):
    response = make_response(jsonify(data_dict))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


def get_request_data():
    if request.method == 'GET':
        str_data = request.args.items()
        dict_data = dict(str_data)
        tid = dict_data['tid']
        # 记录除了tid之后接收到的数据
        logger = log.Log()
        logger.tid = tid
        return dict_data

    
class HostCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        host = dict_data["host_name"]
        iqn = dict_data["host_iqn"]
        logger.write_to_log('OPRT', 'ROUTE', '/host/create', dict_data['ip'], dict_data)
        host_obj = iscsi.Host()
        host_create_results = host_obj.create(host, iqn)
        logger.write_to_log('DATA', 'RESULT', 'HostCreate', 'result', host_create_results)
        if host_create_results == True:
            result = "0"
        else:
            result = "1"
        logger.write_to_log('DATA', 'RETURN', 'HostCreate', 'result', result)
        return cors_data(result)

    
class HostGroupCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        print(dict_data)
        logger = log.Log()
        host = dict_data['host'].split(',')
        host_group_name = dict_data["host_group_name"]
        logger.write_to_log('OPRT', 'ROUTE', '/hg/create', dict_data['ip'], dict_data)
        host_group_obj = iscsi.HostGroup()
        host_group_create_results = host_group_obj.create(host_group_name, host)
        logger.write_to_log('DATA', 'RESULT', 'HostGroupCreate', 'result', host_group_create_results)
        if host_group_create_results == True:
            result = "0"
        else:
            result = "1"
        logger.write_to_log('DATA', 'RETURN', 'HostGroupCreate', 'result', result)
        return cors_data(result)

    
class DiskGroupCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        disk = dict_data['disk'].split(',')
        logger.write_to_log('OPRT', 'ROUTE', '/dg/create', dict_data['ip'], dict_data)
        disk_group_name = dict_data["disk_group_name"]
        disk_group_obj = iscsi.DiskGroup()

        disk_group_create_results = disk_group_obj.create(disk_group_name, disk)
        logger.write_to_log('DATA', 'RESULT', 'DiskGroupCreate', 'result', disk_group_create_results)
        if disk_group_create_results == True:
            result = "0"
        else:
            result = "1"
        logger.write_to_log('DATA', 'RETURN', 'DiskGroupCreate', 'result', result)
        return cors_data(result)

    
class MapCreate(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        map_name = dict_data["map_name"]
        host_group_name = dict_data["host_group"].split(',')
        disk_group_name = dict_data["disk_group"].split(',')
        print(disk_group_name)
        logger.write_to_log('OPRT', 'ROUTE', '/map/create', dict_data['ip'], dict_data)
        map_obj = iscsi.Map()
        map_create_results = map_obj.create(map_name, host_group_name, disk_group_name)
        logger.write_to_log('DATA', 'RESULT', 'MapCreate', 'result', map_create_results)
        if map_create_results == True:
            result = "0"
        else:
            result = "1"
        logger.write_to_log('DATA', 'RETURN', 'MapCreate', 'result', result)
        return cors_data(result)


def get_tid():
    if request.method == 'GET':
        str_transaction_id = request.args.items()
        dict_transaction = dict(str_transaction_id)
        return dict_transaction["transaction_id"]


# host
HOST_RESULT = None


def update_host():
    global HOST_RESULT
   
    js = iscsi_json.JsonOperation()
    HOST_RESULT = js.json_data['Host']
    
    return True


class OprtAllHost(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/host/show/oprt', dict_data['ip'], '')
        if update_host():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHost', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHost', 'result', '1')
            return cors_data("1")

    
class AllHostResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('DATA', 'ROUTE', '/host/show/data', dict_data['ip'], '')
        if not HOST_RESULT:
            update_host()
        logger.write_to_log('DATA', 'RETURN', 'AllHostResult', 'result', HOST_RESULT)
        return cors_data(HOST_RESULT)


# disk   
DISK_RESULT = None


def update_disk():
    global DISK_RESULT
    
    disk = iscsi.Disk()
    DISK_RESULT = disk.update_disk()
    return True


class OprtAllDisk(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/disk/show/oprt', dict_data["ip"], '')
        if update_disk():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDisk', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDisk', 'result', '1')
            return cors_data("1")

    
class AllDiskResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('DATA', 'ROUTE', '/disk/show/data', dict_data["ip"], '')
        if not DISK_RESULT:
            update_disk()
        logger.write_to_log('DATA', 'RETURN', 'AllDiskResult', 'result', DISK_RESULT)
        return cors_data(DISK_RESULT)


# hostgroup
HOSTGROUP_RESULT = None


def update_hg():
    global HOSTGROUP_RESULT

    js = iscsi_json.JsonOperation()
    host_group = iscsi.HostGroup()
    HOSTGROUP_RESULT = js.json_data['HostGroup']
    return True


class OprtAllHg(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/hg/show/oprt', dict_data['ip'], '')
        if update_hg():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHg', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllHg', 'result', '1')
            return cors_data("1")


class AllHgResult(views.MethodView):
    
    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('DATA', 'ROUTE', '/hg/show/data', dict_data['ip'], '')
        if not HOSTGROUP_RESULT:
            update_hg()
        logger.write_to_log('DATA', 'RETURN', 'AllHgResult', 'result', HOSTGROUP_RESULT)
        return cors_data(HOSTGROUP_RESULT)

    
# diskgroup
DISKGROUP_RESULT = None


def update_dg():
    global DISKGROUP_RESULT

    js = iscsi_json.JsonOperation()
    DISKGROUP_RESULT = js.json_data['DiskGroup']
    return True


class OprtAllDg(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/dg/show/oprt', dict_data['ip'], '')
        if update_dg():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDg', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllDg', 'result', '1')
            return cors_data("1")

    
class AllDgResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('DATA', 'ROUTE', '/dg/show/data', dict_data['ip'], '')
        if not DISKGROUP_RESULT:
            update_dg()
        logger.write_to_log('DATA', 'RETURN', 'AllDgResult', 'result', DISKGROUP_RESULT)
        return cors_data(DISKGROUP_RESULT)
    
    
# map
MAP_RESULT = None


def update_map():
    global MAP_RESULT

    js = iscsi_json.JsonOperation()
    MAP_RESULT = js.json_data['Map']
    return True


class OprtAllMap(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('OPRT', 'ROUTE', '/map/show/oprt', dict_data['ip'], '')
        if update_map():
            logger.write_to_log('DATA', 'RETURN', 'OprtAllMap', 'result', '0')
            return cors_data("0")
        else:
            logger.write_to_log('DATA', 'RETURN', 'OprtAllMap', 'result', '1')
            return cors_data("1")

    
class AllMapResult(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        logger = log.Log()
        logger.write_to_log('DATA', 'ROUTE', '/map/show/data', dict_data['ip'], '')
        if not MAP_RESULT:
           update_map()
        logger.write_to_log('DATA', 'RETURN', 'AllMapResult', 'result', MAP_RESULT)
        return cors_data(MAP_RESULT)


class CheckMapModify(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        map = dict_data['map']
        hg = dict_data['hg']
        js = iscsi_json.JsonOperation()
        js_modify = iscsi_json.JsonMofidy()
        js_modify.remove_member('HostGroup', map, [hg], type='Map')
        dict_before = js.get_disk_with_iqn()
        dict_now = js_modify.get_disk_with_iqn()
        obj_ilu = iscsi.IscsiConfig(dict_before, dict_now)

        info = f"删除：{','.join(obj_ilu.delete)}\n新增：{','.join(obj_ilu.create)}\n修改：{','.join(obj_ilu.modify)}"
        dict = {'iscsi_data': js.iscsi_data, 'info': info}
        return cors_data(dict)


class MapModify(views.MethodView):

    def get(self):
        dict_data = get_request_data()
        print(dict_data)
        map = dict_data['map']
        hg = dict_data['hg']
        print(type(dict_data['iscsi_data']))
        iscsi_data = eval(dict_data['iscsi_data'])
        js_now = iscsi_json.JsonOperation()
        print("1:", type(iscsi_data))
        print("2:", type(js_now.iscsi_data))
        if iscsi_data == js_now.iscsi_data:
            js_modify = iscsi_json.JsonMofidy()
            js_modify.remove_member('HostGroup', map, [hg], type='Map')
            dict_before = js_now.get_disk_with_iqn()
            dict_now = js_modify.get_disk_with_iqn()
            obj_ilu = iscsi.IscsiConfig(dict_before, dict_now)
            try:
                obj_ilu.create_iscsilogicalunit()
                obj_ilu.delete_iscsilogicalunit()
                obj_ilu.modify_iscsilogicalunit()
            except Exception:
                print('异常,暂无回退')
                info = '执行失败，已回退'
            if not js_modify.json_data['Map'][map]['HostGroup']:
                js_now.delete_data('Map', map)
            else:
                js_now.remove_member('HostGroup', map, [hg], type='Map')
            info = '删除成功'
        else:
            print('json配置文件已改变')
            info = 'json配置文件已改变,请重新操作'
        return cors_data(info)

