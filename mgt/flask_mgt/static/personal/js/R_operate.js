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
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/resource/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : time
		},
		success : function(R_Hint) {
			var area = document.getElementById("R-S");
			area.innerHTML = "";
			R_Select();
		}
	});
}

First_refresh();
function First_refresh() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/resource/show/oprt",
		type : "GET",
		data : {
			transaction_id : time
			 },
		success : function(R_Hint) {
			R_Select();
			all_resource_show();
		}
	});
}

// 下拉框
$('#R-S').selectpicker({
	width : 200
});
function R_Select() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : time
		},
		success : function(R_D) {
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
		}
	});
}

// 下拉框点击事件
function selectOnchang(obj) {
	var value = obj.options[obj.selectedIndex].value;
	document.getElementById("A_V").innerHTML = "<a>" + value + "</a>";
	if (value == "All_Resource") {
		all_resource_show();
	} else {
		one_resource_show(value);
	}
}

// 所有
function all_resource_show() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : time
		},
		success : function(R_D) {
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
		}
	});
}

// 单个
function one_resource_show(R_N) {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/resource/show/data",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : time
		},
		success : function(R_D) {
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
		}
	});
}
