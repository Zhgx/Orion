/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * R-S Resource select  /下拉框
 * R-D Resource Data /Resource数据
 * _R_D Resource数据变量
 * A_V 标签a的value值
 * R_N Resource Name /具体的名字
 * R_Hint /Resource 提示
 * R_operate.js v0.01
 * */

//操作提示
var masterIp = "http://10.203.1.76:7777"
function update_resource_operate() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	log_url = masterIp + "/resource/show/oprt"
	write_to_log(tid, 'UPDATA_SELECT', 'update_select_data', log_url,
	'start')
	$.ajax({
		url : masterIp + "/resource/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(R_Hint) {
			write_to_log(tid, 'UPDATA_SELECT', 'update_select_data', log_url,
			'request success')
			var area = document.getElementById("R-S");
			area.innerHTML = "";
			R_Select(tid);
		},
		error : function(xhr, state, errorThrown) {
			var log_data = 'request:' + state
			write_to_log(tid, 'UPDATA_SELECT', 'update_select_data', log_url, log_data)
		}
	});
}

First_refresh();
function First_refresh() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	log_url = masterIp + "/resource/show/oprt"
	$.ajax({
		url : masterIp + "/resource/show/oprt",
		type : "GET",
		data : {
			transaction_id : tid
		},
		success : function(R_Hint) {
			write_to_log(tid, 'FRESH', 'resource_show_oprt', log_url,
					'request success')
			R_Select(tid);
			all_resource_show(tid);
		},
		error : function(xhr, state, errorThrown) {
			var log_data = 'request:' + state
			write_to_log(tid, 'FRESH', 'resource_show_oprt', log_url, log_data)
		}
	});
}

// 下拉框
$('#R-S').selectpicker({
	width : 200
});
function R_Select(tid) {
	log_url = masterIp + "/resource/show/data"
	write_to_log(tid, 'GET_DATA', 'get_resource_select_data', log_url, 'start')
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(R_D) {
			write_to_log(tid, 'GET_DATA', 'get_resource_select_data', log_url,
					'success')
			var _R_D = R_D.data; // 由于后台传过来的json有个data，在此重命名
			$('#R-S').html(" ");
			var html_Fir = "";
			var html_Sec = "";
			html_Fir += '<optgroup label="Resource">'
			for (i in _R_D) {
				html_Fir += '<option  value=' + _R_D[i].resource + '>'
						+ _R_D[i].resource + '</option>'
			}
			html_Fir += '</optgroup>'
			html_Sec += '<optgroup >'
			html_Sec += '<option  value="All_Resource">' + "All Resource"
					+ '</option>'
			html_Sec += '</optgroup>'
			$('#R_S').append(html_Fir);
			$('#R_S').append(html_Sec);
			document.getElementById("A_V").innerHTML = "<a>All_Resource</a>";
			// 缺一不可
			$('#R_S').selectpicker('refresh');
			$('#R_S').selectpicker('render');
		},
		error : function(xhr, state, errorThrown) {
			var log_data = 'request:' + state
			write_to_log(tid, 'GET_DATA', 'get_resource_select_data', log_url,
					log_data)
		}
	});
}

// 下拉框点击事件
function selectOnchang(obj) {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	var value = obj.options[obj.selectedIndex].value;
	document.getElementById("A_V").innerHTML = "<a>" + value + "</a>";
	if (value == "All_Resource") {
		all_resource_show(tid);
		write_to_log(tid, 'CLICK_SELECT', 'resource_show_all_data', 'func selectOnchang',
				value)
	} else {
		write_to_log(tid, 'CLICK_SELECT', 'resource_show_one_data', 'func selectOnchang',
				value)
		one_resource_show(value,tid);
	}
}

// 所有
function all_resource_show(tid) {
	log_url = masterIp + "/resource/show/data",
	write_to_log(tid, 'GET_DATA', 'get_resource_all_data', log_url, 'start')
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(R_D) {
			write_to_log(tid, 'GET_DATA', 'get_resource_all_data', log_url, 'request success')
			var _R_D = R_D.data;
			var html = "";
			var html_sec = "";
			html_sec += "<tr>";
			html_sec += "<td>" + "device_name" + "</td>"
			html_sec += "<td>" + "mirror_way" + "</td>"
			html_sec += "<td>" + "resource" + "</td>"
			html_sec += "<td>" + "resource" + "</td>"
			html_sec += "<td>" + "used" + "</td>"
			html_sec += "</tr>";
			for (var i = 0; i < _R_D.length; i++) {
				html += "<tr>";
				html += "<td>" + _R_D[i].device_name + "</td>"
				html += "<td>" + _R_D[i].mirror_way + "</td>"
				html += "<td>" + _R_D[i].resource + "</td>"
				html += "<td>" + _R_D[i].size + "</td>"
				html += "<td>" + _R_D[i].used + "</td>"
				html += "</tr>";
			}
			$("#J_THData").html(html_sec);
			$("#J_TbData").html(html);
		},
		error : function(xhr, state, errorThrown) {
			var log_data = 'request:' + state
			write_to_log(tid, 'GET_DATA', 'get_resource_all_data', log_url,
					log_data)
		}
	});
}

// 单个
function one_resource_show(R_N,tid) {
	log_url = masterIp + "/resource/show/data",
	write_to_log(tid, 'GET_DATA', 'get_resource_one_data', log_url,
			'start')
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(R_D) {
			write_to_log(tid, 'GET_DATA', 'get_resource_one_data', log_url,
			'request success')
			var _R_D = R_D.data;
			for (i in _R_D) {
				if (_R_D[i].resource == R_N) {
					
					var mirror_way_son = _R_D[i].mirror_way_son;
					var html = "";
					var html_sec = "";
					html_sec += "<tr>";
					html_sec += "<td>" + "drbd_role" + "</td>"
					html_sec += "<td>" + "node_name" + "</td>"
					html_sec += "<td>" + "status" + "</td>"
					html_sec += "<td>" + "stp_name" + "</td>"
					html_sec += "</tr>";
					for (var i = 0; i < mirror_way_son.length; i++) {
						html += "<tr>";
						html += "<td>" + mirror_way_son[i].drbd_role + "</td>"
						html += "<td>" + mirror_way_son[i].node_name + "</td>"
						html += "<td>" + mirror_way_son[i].status + "</td>"
						html += "<td>" + mirror_way_son[i].stp_name + "</td>"
						html += "</tr>";
					}
					$("#J_THData").html(html_sec);
					$("#J_TbData").html(html);

				}
			}
		},
		error : function(xhr, state, errorThrown) {
			var log_data = 'request:' + state
			write_to_log(tid, 'GET_DATA', 'get_resource_one_data', log_url,
					log_data)
		}
	});
}

function write_to_log(tid, type, d1, d2, data) {
	$.ajax({
		url : '/iscsi/write_log',
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			type : type,
			d1 : d1,
			d2 : d2,
			data : data
		},
		success : function(write_log_result) {
		}
	});
}
