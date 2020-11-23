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
	// 获取点击表格的td值
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		$("#HG_T_Show").append(
				'<tr onClick="change_hostgroup_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
		var td = curRow.cells
		// for (var i = 0; i < td.length; i++) {
		var td_host = td[0].innerHTML
		// 获取hostgroup的值
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
				
				// 获取host的数据
				$.ajax({
					url : vplxIp + "/host/show/data",
					type : "get",
					dataType : "json",
					data : {
						tid : tid,
						ip : mgtIp
					},
					success : function(host_result) {
						var obj_list = [];
						var obj_host_list = [];
						for (i=1; i < window.HGTable_Show.rows.length; i++) {
							obj_list.push(window.HGTable_Show.rows[i].cells[0].innerHTML);
						};
						for( i in obj_list){
							var aa = host_group_result[obj_list[i]];
							for (var j = 0; j <aa.length; j++) {
								obj_host_list.push(aa[j]);
							}
						}
						 var obj_host_list_new = obj_host_list.filter((e,i)=>obj_host_list.indexOf(e)==i)
						 $("#HostTable tr:not(:first)").html("");
						 for (var i = 0; i < obj_host_list_new.length; i++) {
						tr = '<td >' + obj_host_list_new[i] + '</td>' + '<td >'
						+ host_result[obj_host_list_new[i]]
						+ '</td>';
						$("#Host_T").append('<tr >' + tr + '</tr>')
						}
					},
				});
			},
			error : function() {
				write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data',
						'error');
			}

		});
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
				
				// 获取host的数据
				$.ajax({
					url : vplxIp + "/host/show/data",
					type : "get",
					dataType : "json",
					data : {
						tid : tid,
						ip : mgtIp
					},
					success : function(host_result) {
						var obj_list = [];
						var obj_host_list = [];
						for (i=1; i < window.HGTable_Show.rows.length; i++) {
							obj_list.push(window.HGTable_Show.rows[i].cells[0].innerHTML);
						};
						for( i in obj_list){
							var aa = host_group_result[obj_list[i]];
							for (var j = 0; j <aa.length; j++) {
								obj_host_list.push(aa[j]);
							}
						}
						 var obj_host_list_new = obj_host_list.filter((e,i)=>obj_host_list.indexOf(e)==i)
						 $("#HostTable tr:not(:first)").html("");
						 for (var i = 0; i < obj_host_list_new.length; i++) {
						tr = '<td >' + obj_host_list_new[i] + '</td>' + '<td >'
						+ host_result[obj_host_list_new[i]]
						+ '</td>';
						$("#Host_T").append('<tr >' + tr + '</tr>')
						}
					},
				});
			},
			error : function() {
				write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data',
						'error');
			}

		});
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
		$("#DG_T_Show").append(
				'<tr onClick="change_diskgroup_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
			$.ajax({
				url : vplxIp + "/dg/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(disk_group_result) {
					$.ajax({
						url : vplxIp + "/resource/show/data",
						type : "get",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						success : function(resource_result) {
							var resource_data = resource_result.data
							var obj_list = [];
							var obj_disk_list = [];
							for (i=1; i < window.DGTable_Show.rows.length; i++) {
								obj_list.push(window.DGTable_Show.rows[i].cells[0].innerHTML);
							};
							for( i in obj_list){
								var aa = disk_group_result[obj_list[i]];
								for (var j = 0; j <aa.length; j++) {
									obj_disk_list.push(aa[j]);
								}
							}
							 var obj_disk_list_new = obj_disk_list.filter((e,i)=>obj_disk_list.indexOf(e)==i)
							 $("#DiskTable tr:not(:first)").html("");
							 for (var i = 0; i < obj_disk_list_new.length; i++) {
								 for (var  j= 0;  j< resource_data.length; j++) {
									 if (obj_disk_list_new[i] == resource_data[j].resource) {
										 tr = '<td >' + resource_data[j].resource + '</td>' +'<td >'
										 + resource_data[j].device_name
										 + '</td>';
										 $("#Disk_T").append('<tr >' + tr + '</tr>')
									}
								}
							}
						}
					});
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
							'error');
				}

			});
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
		$.ajax({
			url : vplxIp + "/dg/show/data",
			type : "get",
			dataType : "json",
			data : {
				tid : tid,
				ip : mgtIp
			},
			success : function(disk_group_result) {
				$.ajax({
					url : vplxIp + "/resource/show/data",
					type : "get",
					dataType : "json",
					data : {
						tid : tid,
						ip : mgtIp
					},
					success : function(resource_result) {
						var resource_data = resource_result.data
						var obj_list = [];
						var obj_disk_list = [];
						for (i=1; i < window.DGTable_Show.rows.length; i++) {
							obj_list.push(window.DGTable_Show.rows[i].cells[0].innerHTML);
						};
						for( i in obj_list){
							var aa = disk_group_result[obj_list[i]];
							for (var j = 0; j <aa.length; j++) {
								obj_disk_list.push(aa[j]);
							}
						}
						 var obj_disk_list_new = obj_disk_list.filter((e,i)=>obj_disk_list.indexOf(e)==i)
						 $("#DiskTable tr:not(:first)").html("");
						 for (var i = 0; i < obj_disk_list_new.length; i++) {
							 for (var  j= 0;  j< resource_data.length; j++) {
								 if (obj_disk_list_new[i] == resource_data[j].resource) {
									 tr = '<td >' + resource_data[j].resource + '</td>' +'<td >'
									 + resource_data[j].device_name
									 + '</td>';
									 $("#Disk_T").append('<tr >' + tr + '</tr>')
								}
							}
						}
					}
				});
			},
			error : function() {
				write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
						'error');
			}

		});
		
		
		
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
