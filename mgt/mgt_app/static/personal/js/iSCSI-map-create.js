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

function get_mgt_ip(){
	var obj = new Object();
	$.ajax({
		url : "http://127.0.0.1:7773/mgtip",
		type : "GET",
		dataType : "json",
		async:false,
		success : function(data) {
			obj =  "http://"+data["ip"];
		}
	});

	return obj;
}

function get_vlpx_ip(){
	var obj = new Object();
	$.ajax({
		url : "http://127.0.0.1:7773/vplxip",
		type : "GET",
		dataType : "json",
		async:false,
		success : function(data) {
			console.log("okokok");
			console.log(data["ip"]);
			obj =  "http://"+data["ip"];
		}
	});

	return obj;
}

$("#map_create").click(function() {
	var map_name = $("#map_name").val()
	var disk_group = $("#disk_group").val()
	var host_group = $("#host_group").val()
	var map_name_hid = $("#map_name_hid").val();
	var map_name_verify_status = $("#map_name_verify_status").val();
	var dict_data = JSON.stringify({
		"map_name" : map_name,
		"disk_group" : disk_group,
		"host_group" : host_group
	});
	if (map_name_verify_status == "0") {
		map_name_myfunction();
	} else if (map_name_verify_status == "1") {
		pass
	}
	if (map_name_hid == "1") {
		write_to_log(tid,'DATA','CHECKBOX','host group','',host_group);
		write_to_log(tid,'DATA','CHECKBOX','disk group','',disk_group);
		write_to_log(tid, 'OPRT', 'CLICK', 'map_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/map/create",
			type : "GET",
			data : {
				tid : tid,
				ip : mgtIp,
				map_name : map_name,
				disk_group : disk_group,
				host_group : host_group
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/map/create' ,JSON.stringify(operation_feedback_prompt));
				$("#map_name_verify_status").val("0");
				alert(operation_feedback_prompt);
				$("#map_name").val("");
				$("#map_name_hid").val("0");
			},
			error : function() {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/map/create', 'error');
			}
		})
	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'map_create', 'refuse', dict_data);
		alert("请输入正确值!")
	}
});

$('#host_group').selectpicker({
	width : 200
});

function all_hg_result_select() {
	$.ajax({
		url : vplxIp + "/hg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/show/oprt', status);
			$.ajax({
				url : vplxIp + "/hg/show/data",
				type : "get",
				dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
				success : function(host_group_result) {
					// var _data = data.data; //由于后台传过来的json有个data，在此重命名
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data',JSON.stringify( host_group_result));
					$('#host_group').html("");
					var html = "";
					for (i in host_group_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#host_group').append(html);
					// 缺一不可
					$('#host_group').selectpicker('refresh');
					$('#host_group').selectpicker('render');
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/hg/show/data', 'error');
				}
				
			});

		},
		error : function() {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/show/oprt', 'error');
		}
	});

};
all_hg_result_select();
$(window).on('load', function() {
	$('#host_group').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#disk_group').selectpicker({
	width : 200
});

function all_dg_result_select() {
	$.ajax({
		url : vplxIp + "/dg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/show/oprt',status);
			$.ajax({
				url : vplxIp + "/dg/show/data",
				type : "get",
				dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
				success : function(all_dg_result) {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',JSON.stringify(all_dg_result));
					$('#disk_group').html("");
					var html = "";
					for (i in all_dg_result) {
						$('#disk_group').append(
								'<option value=' + i + '>' + i + '</option>')
					}
					// 缺一不可
					$('#disk_group').selectpicker('refresh');
					$('#disk_group').selectpicker('render');
				},
				error : function(){
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data', 'error');
				}
			});
		},
		error : function() {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/show/oprt', 'error');
		}
		
	});
};
all_dg_result_select();
$(window).on('load', function() {
	$('#disk_group').selectpicker({
		'selectedText' : 'cat'
	});
});

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
// 输入框验证
function map_name_myfunction() {
	$("#map_name_verify_status").val("1");
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
							write_to_log(tid,'OPRT','ROUTE',vplxIp,'/map/show/oprt',map_result);
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
											write_to_log(tid,'DATA','ROUTE',vplxIp,'/map/show/data',JSON.stringify(Map_result));
											if (input_result in Map_result) {
												$("#map_name_hid").val("0");
												document
														.getElementById("map_name_examine").className = "";
											} else {
												$("#map_name_hid").val("1");
											}
										},
										error : function(){
											write_to_log(tid,'DATA','ROUTE',vplxIp,'/map/show/data','error');
										}
										
									});
						},
						error : function(){
							write_to_log(tid,'OPRT','ROUTE',vplxIp,'/map/show/oprt','error');
						}
					});

		}
	}
}

