/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

var masterIp = "http://10.203.1.76:7777"

// 操作提示
$("#host_create").click(function() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	var hostName = $("#host_name").val()
	var hostiqn = $("#host_iqn").val()
	var host_name_hid = $("#host_name_hid").val();
	var host_iqn_hid = $("#host_iqn_hid").val();
	if (host_name_hid == "1") {
		var host_name_hid_result = "True"
	}else {
		var host_name_hid_result = "False"
		
	};
	if (host_iqn_hid == "1") {
		var host_iqn_hid_result = "True"
	}else {
		var host_iqn_hid_result = "False"
	};
	var dict_data = JSON.stringify({"host_name":hostName,"host_iqn": hostiqn,"host_name_status":host_name_hid_result,"host_iqn_status":host_iqn_hid_result});
	var d1 = "host_create";
	var d2  = masterIp + "/host/create";
	write_to_log(tid,'INPUT',d1,d2,dict_data)
	if (host_name_hid == "1" && host_iqn_hid == "1") {
		$.ajax({
			url : masterIp + "/host/create",
			type : "GET",
			data : {
				transaction_id : tid,
				host_name : hostName,
				host_iqn : hostiqn
			},
			success : function(Successful_feedback) {
				
				write_to_log(tid,'INPUT',d1,d2,Successful_feedback)
				alert(Successful_feedback);
				$("#host_name").val("");
				$("#host_iqn").val("");
				$("#host_iqn_hid").val("0");
				$('#host').selectpicker({
					width : 200
				});
				host_result_select();
				$(window).on('load', function() {
					$('#host').selectpicker({
						'selectedText' : 'cat'
					});
				});

			},
			error : function() {
			}
		})

	} else {
		alert("请输入正确值!")
	}
});
$("#host_group_create").click(function() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	var host_group_name = $("#host_group_name").val()
	var host = $("#host").val().toString()
	var hg_name_hid = $("#hg_name_hid").val();
	if (hg_name_hid == "1") {
		var hg_name_hid_result = "True"
	}else {
		var hg_name_hid_result = "False"
		
	};
	var dict_data = JSON.stringify({"host_group_name":host_group_name,"host":host,"hg_name_status":hg_name_hid_result});
	var d1 = "host_group_create";
	var d2  = masterIp + "/hg/create";
	write_to_log(tid,'INPUT',d1,d2,dict_data)
	if (hg_name_hid == "1") {
		$.ajax({
			url : masterIp + "/hg/create",
			type : "GET",
			data : {
				transaction_id : tid,
				host_group_name : host_group_name,
				host : host
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid,'INPUT',d1,d2,operation_feedback_prompt)
				alert(operation_feedback_prompt);
				$("#host_group_name").val("");
				$('#host_group').selectpicker({
					width : 200
				});
				$("#hg_name_hid").val("0");
				all_hg_result_select();
				$(window).on('load', function() {
					$('#host_group').selectpicker({
						'selectedText' : 'cat'
					});
				});

				// $("#double").val(data);
				// 赋值
			},
			error : function() {
			}
		})
	}else {
		alert("请输入正确值!");
	}

});

$("#disk_group_create").click(function() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	var disk_group_name = $("#disk_group_name").val()
	var disk = $("#disk").val().toString()
	var dg_name_hid = $("#dg_name_hid").val();
	if (dg_name_hid == "1") {
		var dg_name_hid_result = "True"
	}else {
		var dg_name_hid_result = "False"
	};
	var dict_data = JSON.stringify({"disk_group_name":disk_group_name,"disk":disk,"dg_name_status":dg_name_hid_result});
	var d1 = "disk_group_create";
	var d2  = masterIp + "/dg/create";
	write_to_log(tid,'INPUT',d1,d2,dict_data)
	if (dg_name_hid == "1") {
		
		$.ajax({
			url : masterIp + "/dg/create",
			type : "GET",
			data : {
				transaction_id : tid,
				disk_group_name : disk_group_name,
				disk : disk
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid,'INPUT',d1,d2,operation_feedback_prompt)
				alert(operation_feedback_prompt);
				$("#disk_group_name").val("");
				$("#dg_name_hid").val("0");
				$('#disk_group').selectpicker({
					width : 200
				});
				all_dg_result_select();
				$(window).on('load', function() {
					$('#disk_group').selectpicker({
						'selectedText' : 'cat'
					});
				});

			},
			error : function() {
			}
		})
	}else {
		alert("请输入正确值!")
	}
});
$("#map_create").click(function() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	var map_name = $("#map_name").val()
	var disk_group = $("#disk_group").val()
	var host_group = $("#host_group").val()
	var map_name_hid = $("#map_name_hid").val();
	if (map_name_hid == "1") {
		var map_name_hid_result = "True"
	}else {
		var map_name_hid_result = "False"
	};
	var dict_data = JSON.stringify({"map_name":map_name,"disk_group":disk_group,"host_group":host_group,"map_name_status":map_name_hid_result});
	var d1 = "map_create";
	var d2  = masterIp + "/map/create";
	write_to_log(tid,'INPUT',d1,d2,dict_data)
	if (map_name_hid == "1") {
		$.ajax({
			url : masterIp + "/map/create",
			type : "GET",
			data : {
				transaction_id : tid,
				map_name : map_name,
				disk_group : disk_group,
				host_group : host_group
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid,'INPUT',d1,d2,operation_feedback_prompt)
				alert(operation_feedback_prompt);
				$("#map_name").val("");
				$("#map_name_hid").val("0");
			},
			error : function() {
			}
		})
	}else {
		alert("请输入正确值!")
	}
});

$('#host').selectpicker({
	width : 200
});
function host_result_select() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	$.ajax({
		url : masterIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function() {
			$.ajax({
				url : masterIp + "/host/show/data",
				type : "GET",
				dataType : "json",
				success : function(host_result) {
					$('#host').html("");
					var html = "";
					for (i in host_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#host').append(html);
					$('#host').selectpicker('refresh');
					$('#host').selectpicker('render');
				}
			});
		}
	});
};
host_result_select();
$(window).on('load', function() {
	$('#host').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#disk').selectpicker({
	width : 200
});

function disk_result_select() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	$.ajax({
		url : masterIp + "/disk/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function() {
			$.ajax({
				url : masterIp + "/disk/show/data",
				type : "GET",
				dataType : "json",
				success : function(disk_result) {
					// var _data = data.data; //由于后台传过来的json有个data，在此重命名
					$('#disk').html("");
					var html = "";
					for (i in disk_result) {
						// alert(i);
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#disk').append(html);
					// 缺一不可
					$('#disk').selectpicker('refresh');
					$('#disk').selectpicker('render');
				}
			});
		}
	});

};
disk_result_select();
$(window).on('load', function() {
	$('#disk').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#host_group').selectpicker({
	width : 200
});

function all_hg_result_select() {
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	$.ajax({
		url : masterIp + "/hg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function() {
			$.ajax({
				url : masterIp + "/hg/show/data",
				type : "get",
				dataType : "json",
				success : function(host_group_result) {
					// var _data = data.data; //由于后台传过来的json有个data，在此重命名
					$('#host_group').html("");
					var html = "";
					for (i in host_group_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#host_group').append(html);
					// 缺一不可
					$('#host_group').selectpicker('refresh');
					$('#host_group').selectpicker('render');
				}
			});

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
	var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	tid = tid.substr(0, 10);
	$.ajax({
		url : masterIp + "/dg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function() {
			$.ajax({
				url : masterIp + "/dg/show/data",
				type : "get",
				dataType : "json",
				success : function(all_dg_result) {
					$('#disk_group').html("");
					var html = "";
					for (i in all_dg_result) {
						$('#disk_group').append(
								'<option value=' + i + '>' + i + '</option>')
					}
					// 缺一不可
					$('#disk_group').selectpicker('refresh');
					$('#disk_group').selectpicker('render');
				}
			});
		}
	});
};
all_dg_result_select();
$(window).on('load', function() {
	$('#disk_group').selectpicker({
		'selectedText' : 'cat'
	});
});


function write_to_log(tid,type,d1,d2,data) {
	$.ajax({
		url : '/iscsi/write_log',
		type : "get",
		dataType : "json",
		data:{
			tid:tid,
			type:type,
			d1:d1,
			d2:d2,
			data:data
		},
		success : function(write_log_result) {
		}
	});
}



