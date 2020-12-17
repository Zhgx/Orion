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
		url : "/mgtip",
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
		url : "/vplxip",
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
		async : false,
		success : function(write_log_result) {
		}
	});
}

// disk_table();
// function disk_table() {
// $.ajax({
// url : vplxIp + "/disk/show/oprt",
// type : "GET",
// dataType : "json",
// data : {
// tid : tid,
// ip : mgtIp
// },
// success : function(status) {
// write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/disk/show/oprt',
// status);
// $.ajax({
// url : vplxIp + "/disk/show/data",
// type : "GET",
// dataType : "json",
// data : {
// tid : tid,
// ip : mgtIp
// },
// success : function(disk_result) {
// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
// '/disk/show/data', JSON.stringify(disk_result));
// // var _data = data.data; //由于后台传过来的json有个data，在此重命名
// for (i in disk_result) {
// tr = '<td >' + i + '</td>' + '<td >' + i + '</td>'
// $("#D_T").append(
// '<tr onClick="change_disk(this)" >' + tr
// + '</tr>')
// }
// },
// error : function() {
// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
// '/disk/show/data', 'error');
// }
// });
// },
// error : function() {
// write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/disk/show/oprt',
// 'error');
// }
// });
// };

// function change_disk(obj) {
// if (event.srcElement.tagName == "TD") {
// curRow = event.srcElement.parentElement;
// tr = curRow.innerHTML;
//		
// $("#D_T_Show").append(
// '<tr onClick="change_disk_second(this)">' + tr + '</tr>');
// curRow.remove();// 删除
// }
// }
disk_table();
function disk_table() {
	$.ajax({
		url : vplxIp + "/resource/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		async : false,
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/resource/show/oprt',
					status);
			$.ajax({
				url : vplxIp + "/resource/show/data",
				type : "GET",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(resource_result) {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/resource/show/data', JSON.stringify(resource_result));
					 var _data = resource_result.data; // 由于后台传过来的json有个data，在此重命名
					for (i in _data) {
						tr = '<td >' + _data[i].resource + '</td>' + '<td >' + _data[i].size + '</td>'
						$("#D_T").append(
								'<tr onClick="change_disk(this)" >' + tr
										+ '</tr>')
					}
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/disk/show/data', 'error');
				}
			});
		},
		error : function() {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/disk/show/oprt',
					'error');
		}
	});
};

function change_disk(obj) {
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		$("#D_T_Show").append(
				'<tr onClick="change_disk_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
		var td = curRow.cells
		var td_host = td[0].innerHTML
			console.log(td_host);
			$.ajax({
				url : vplxIp + "/resource/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(resource_result) {
					console.log(resource_result);
					 var _data = resource_result.data; // 由于后台传过来的json有个data，在此重命名
							for (i in _data) {
								if (td_host == _data[i].resource) {
									tr = '<td >' + _data[i].device_name + '</td>'
									$("#D_Dev_T_Show").append(
											'<tr>' + tr
											+ '</tr>')
								}
							} 
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data',
							'error');
				}

			});
	}
}

function change_disk_second() {
	var obj_list = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML
		$("#D_T").append('<tr onClick="change_disk(this)" >' + tr + '</tr>')
		curRow.remove();
		// var count=0;
		for (i=1; i < window.DTable_Show.rows.length; i++) {
			obj_list.push(window.DTable_Show.rows[i].cells[0].innerHTML) 
		}
		$("#D_Dev_Table_Show tr:not(:first)").html("");
			$.ajax({
				url : vplxIp + "/resource/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(resource_result) {
					 var _data = resource_result.data; // 由于后台传过来的json有个data，在此重命名
					 for(i in obj_list){
							for (j in _data) {
								if (obj_list[i] == _data[j].resource) {
									tr = '<td >' + _data[j].device_name + '</td>'
									$("#D_Dev_T_Show").append(
											'<tr>' + tr
											+ '</tr>')
								}
							} 
						 
					 }
					 write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
					 '/hg/show/data', JSON
					 .stringify(host_group_result));
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
							'error');
				}

			});
		
		
		
	}
}
// 输入框验证
function dg_name_myfunction() {
	document.getElementById("dg_name_examine").className = "hidden";
	document.getElementById("dg_name_format").className = "hidden";
	var input_result = $('#disk_group_name').val();
	var dg_name_match_regular = /^[a-zA-Z]\w*$/;
	match_result = dg_name_match_regular.test(input_result)
	if (!input_result) {
		$("#dg_name_hid").val("0");
		document.getElementById("dg_name_examine").className = "hidden";
		document.getElementById("dg_name_format").className = "hidden";
	} else {
		if (!match_result) {
			$("#dg_name_hid").val("0");
			document.getElementById("dg_name_format").className = "";
		} else {
			document.getElementById("dg_name_format").className = "hidden";
			$
					.ajax({
						url : vplxIp + "/dg/show/oprt",
						type : "GET",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						async : false,
						success : function(DG_result) {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/dg/show/oprt', DG_result);
							$
									.ajax({
										url : vplxIp + "/dg/show/data",
										type : "GET",
										dataType : "json",
										data : {
											tid : tid,
											ip : mgtIp
										},
										async : false,
										success : function(DG_result) {
											write_to_log(tid, 'DATA', 'ROUTE',
													vplxIp, '/dg/show/data',
													JSON.stringify(DG_result));
											
											if (JSON.stringify(DG_result) === '{}') {
												$("#dg_name_hid").val("1");
											} else {
												for ( var i in DG_result) {
													if (input_result == i) {
														$("#dg_name_hid").val("0");
														document
														.getElementById("dg_name_examine").className = "";
														break;
													} else {
														$("#dg_name_hid").val("1");
													}
												}
											}
										},
										error : function() {
											write_to_log(tid, 'DATA', 'ROUTE',
													vplxIp, '/dg/show/data',
													'error');
										}
									});
						},
						error : function() {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/dg/show/oprt', 'error');
						}
					});
		}
	}
}

function div_success() {
	document.getElementById('light_success').style.display='block';
	setTimeout("light_success.style.display='none'",2000);
}

function div_failed() {
	document.getElementById('light_failed').style.display='block';
	document.getElementById('fade').style.display='block';
	setTimeout("light_failed.style.display='none'",4000);
	setTimeout("fade.style.display='none'",4000);
}


$("#disk_group_create").mousedown(function(){
			dg_name_myfunction();
			var obj_disk = [];
			var tableId = document.getElementById("DTable_Show");
			var str = "";
			for (var i = 1; i < DTable_Show.rows.length; i++) {
				obj_disk.push(DTable_Show.rows[i].cells[0].innerHTML)
			}
			obj_disk_str = obj_disk.toString();
			var disk_group_name = $("#disk_group_name").val()
			var dict_data = JSON.stringify({
				"disk_group_name" : disk_group_name,
				"disk" : obj_disk_str
			});
			var dg_name_hid_value = $("#dg_name_hid").val();
			if (dg_name_hid_value == "1") {
				write_to_log(tid, 'DATA', 'RADIO', 'disk', '', obj_disk_str);
				write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create',
						'accept', dict_data);
				$.ajax({
					url : vplxIp + "/dg/create",
					type : "GET",
					data : {
						tid : tid,
						ip : mgtIp,
						disk_group_name : disk_group_name,
						disk : obj_disk_str
					},
					async : false,
					success : function(operation_feedback_prompt) {
						if (operation_feedback_prompt == '0') {
							var text = "创建成功!";
							$('#P_text_success').text(text);
							div_success();
						}else {
							var text = "创建失败!";
							$('#P_text_failed').text(text);
							 div_failed();
						}
						
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/dg/create', operation_feedback_prompt);
						$("#disk_group_name").val("");
						$("#dg_name_hid").val("0");
					},
					error : function() {
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/dg/create', 'error');
					}
				})
			} else {
				write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create',
						'refuse', dict_data);
			}
		});


$(function () { $("[data-toggle='popover']").popover(); });

$("[rel=drevil]").popover({
    trigger:'manual',
    html: 'true', 
    animation: false
}).on("mouseenter", function () {
    var _this = this;
    $(this).popover("show");
    $(this).siblings(".popover").on("mouseleave", function () {
        $(_this).popover('hide');
    });
}).on("mouseleave", function () {
    var _this = this;
    setTimeout(function () {
        if (!$(".popover:hover").length) {
            $(_this).popover("hide")
        }
    }, );
});　

