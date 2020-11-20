/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

// 操作提示
var vplxIp = get_vlpx_ip();
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);
var mgtIp = get_mgt_ip();

function get_mgt_ip() {
	var obj = new Object();
	$.ajax({
		url : "http://127.0.0.1:7773/mgtip",
		type : "GET",
		dataType : "json",
		async : false,
		success : function(data) {
			obj = "http://" + data["ip"];
		}
	});

	return obj;
}

function get_vlpx_ip() {
	var obj = new Object();
	$.ajax({
		url : "http://127.0.0.1:7773/vplxip",
		type : "GET",
		dataType : "json",
		async : false,
		success : function(data) {
			obj = "http://" + data["ip"];
		}
	});

	return obj;
}

function write_to_log(tid, t1, t2, d1, d2, data) {
	$.ajax({
		url : '/iscsi/write_log',
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			t1 : t1,
			t2 : t2,
			d1 : d1,
			d2 : d2,
			data : data
		},
		success : function(write_log_result) {
		}
	});
}

hg_table();
function hg_table() {
	$
			.ajax({
				url : vplxIp + "/hg/show/oprt",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(status) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/show/oprt',
							status);
					$.ajax({
						url : vplxIp + "/hg/show/data",
						type : "get",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						success : function(host_group_result) {
							write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
									'/hg/show/data', JSON
											.stringify(host_group_result));
							for (i in host_group_result) {
								tr = '<td >' + i + '</td>';
								$("#HG_T").append(
										'<tr onClick="change_hostgroup(this)">'
												+ tr + '</tr>')
							}
						},
						error : function() {
							write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
									'/hg/show/data', 'error');
						}

					});

				},
				error : function() {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/show/oprt',
							'error');
				}
			});

};

function change_hostgroup(obj) {
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells
		for (var i = 0; i < td.length; i++) {
			var td_host = td[i].innerHTML
			$.ajax({
				url : vplxIp + "/hg/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(host_group_result) {
					// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
					// '/hg/show/data', JSON
					// .stringify(host_group_result));
					for (j in host_group_result) {
						if (td_host == j) {
							var list_host = host_group_result[j]
							$("#HostTable  tr:not(:first)").html("");
							for (jj in list_host) {
								tr = '<td >' + list_host[jj] + '</td>';
								$("#Host_T").append('<tr >' + tr + '</tr>')
							}
						}
					}
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data',
							'error');
				}

			});

		}
		$("#HG_T_Show").append(
				'<tr onClick="change_hostgroup_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
	}
}

function change_hostgroup_second() {
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML
		$("#HG_T").append(
				'<tr onClick="change_hostgroup(this)" >' + tr + '</tr>')
		curRow.remove();
	}
}

Dg_Table();
function Dg_Table() {
	$
			.ajax({
				url : vplxIp + "/dg/show/oprt",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(status) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/show/oprt',
							status);
					$.ajax({
						url : vplxIp + "/dg/show/data",
						type : "get",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						success : function(all_dg_result) {
							write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
									'/dg/show/data', JSON
											.stringify(all_dg_result));
							for (i in all_dg_result) {
								tr = '<td >' + i + '</td>';
								$("#DG_T").append(
										'<tr onClick="change_diskgroup(this)">'
												+ tr + '</tr>')
							}
						},
						error : function() {
							write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
									'/dg/show/data', 'error');
						}
					});
				},
				error : function() {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/show/oprt',
							'error');
				}

			});
};

function change_diskgroup(obj) {
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells;
		for (var i = 0; i < td.length; i++) {
			var td_disk = td[i].innerHTML;
			$.ajax({
				url : vplxIp + "/dg/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(disk_group_result) {
					// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
					// '/hg/show/data', JSON
					// .stringify(host_group_result));
					for (j in disk_group_result) {
						if (td_disk == j) {
							var list_disk = disk_group_result[j]
							$("#DiskTable  tr:not(:first)").html("");
							for (jj in list_disk) {
								tr = '<td >' + list_disk[jj] + '</td>';
								$("#Disk_T").append('<tr >' + tr + '</tr>')
							}
						}
					}
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
							'error');
				}

			});

		}

		$("#DG_T_Show").append(
				'<tr onClick="change_diskgroup_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
	}
}

function change_diskgroup_second() {
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML
		$("#DG_T").append(
				'<tr onClick="change_diskgroup(this)" >' + tr + '</tr>')
		curRow.remove();
	}
}

// 输入框验证
function map_name_myfunction() {
	document.getElementById("map_name_examine").className = "hidden";
	document.getElementById("map_name_format").className = "hidden";
	var input_result = $('#map_name').val();
	var map_name_match_regular = /^[a-zA-Z]\w*$/;
	match_result = map_name_match_regular.test(input_result)
	if (!input_result) {
		$("#map_name_hid").val("0");
		document.getElementById("map_name_examine").className = "hidden";
		document.getElementById("map_name_format").className = "hidden";
	} else {
		if (!match_result) {
			$("#map_name_hid").val("0");
			document.getElementById("map_name_format").className = "";
		} else {

			document.getElementById("map_name_format").className = "hidden";
			$
					.ajax({
						url : vplxIp + "/map/show/oprt",
						type : "GET",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						success : function(map_result) {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/map/show/oprt', map_result);
							$
									.ajax({
										url : vplxIp + "/map/show/data",
										type : "GET",
										dataType : "json",
										data : {
											tid : tid,
											ip : mgtIp
										},
										success : function(Map_result) {
											write_to_log(tid, 'DATA', 'ROUTE',
													vplxIp, '/map/show/data',
													JSON.stringify(Map_result));
											if (input_result in Map_result) {
												$("#map_name_hid").val("0");
												document
														.getElementById("map_name_examine").className = "";
											} else {
												$("#map_name_hid").val("1");
											}
										},
										error : function() {
											write_to_log(tid, 'DATA', 'ROUTE',
													vplxIp, '/map/show/data',
													'error');
										}

									});
						},
						error : function() {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/map/show/oprt', 'error');
						}
					});

		}
	}
}

$("#map_create").click(
		function() {
			var obj_diskgroup = [];
			var tableId = document.getElementById("HGTable_Show");
			var str = "";
			for (var i = 1; i < tableId.rows.length; i++) {
				obj_diskgroup.push(tableId.rows[i].cells[0].innerHTML)
			}
			obj_diskgroup_str = obj_diskgroup.toString();
			var obj_hostgroup = [];
			var tableId = document.getElementById("DGTable_Show");
			var str = "";
			for (var i = 1; i < tableId.rows.length; i++) {
				obj_hostgroup.push(tableId.rows[i].cells[0].innerHTML)
			}
			obj_hostgroup_str = obj_hostgroup.toString();
			
			var map_name = $("#map_name").val()
			var dict_data = JSON.stringify({
				"map_name" : map_name,
				"disk_group" : obj_diskgroup_str,
				"host_group" : obj_hostgroup_str
			});
			map_name_myfunction();
			var map_name_hid = $("#map_name_hid").val();
			if (map_name_hid == "1") {
				write_to_log(tid, 'DATA', 'CHECKBOX', 'host group', '',
						obj_hostgroup_str);
				write_to_log(tid, 'DATA', 'CHECKBOX', 'disk group', '',
						obj_diskgroup_str);
				write_to_log(tid, 'OPRT', 'CLICK', 'map_create', 'accept',
						dict_data);
				$.ajax({
					url : vplxIp + "/map/create",
					type : "GET",
					data : {
						tid : tid,
						ip : mgtIp,
						map_name : map_name,
						disk_group : obj_diskgroup_str,
						host_group : obj_hostgroup_str
					},
					success : function(operation_feedback_prompt) {
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/map/create', JSON
										.stringify(operation_feedback_prompt));
						$("#map_name").val("");
						$("#map_name_hid").val("0");
					},
					error : function() {
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/map/create', 'error');
					}
				})
			} else {
				write_to_log(tid, 'OPRT', 'CLICK', 'map_create', 'refuse',
						dict_data);
				alert("请输入正确值!")
			}
		});
