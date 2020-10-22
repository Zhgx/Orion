/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

var masterIp = "http://10.203.1.76:7777"

//操作提示
$("#host_create").click(function() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	var hostName = $("#host_name").val()
	var hostiqn = $("#host_iqn").val()

	$.ajax({
		url : masterIp + "/host/create",
		type : "GET",
		data : {
			transaction_id:time,
			host_name : hostName,
			host_iqn : hostiqn
		},
		success : function(Successful_feedback) {
			alert(Successful_feedback);
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
	$("#host_name").val("");
	$("#host_iqn").val("");

});
$("#host_group_create").click(function() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	var host_group_name = $("#host_group_name").val()
	var host = $("#host").val().toString()
	$.ajax({
		url : masterIp + "/hg/create",
		type : "GET",
		data : {
			transaction_id:time,
			host_group_name : host_group_name,
			host : host
		},
		success : function(operation_feedback_prompt) {
			alert(operation_feedback_prompt);
			$('#host_group').selectpicker({
				width : 200
			});
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
	$("#host_group_name").val("");
});

$("#disk_group_create").click(function() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	var disk_group_name = $("#disk_group_name").val()
	var disk = $("#disk").val().toString()
	$.ajax({
		url : masterIp + "/dg/create",
		type : "GET",
		data : {
			transaction_id:time,
			disk_group_name : disk_group_name,
			disk : disk
		},
		success : function(operation_feedback_prompt) {

			alert(operation_feedback_prompt);
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
	$("#disk_group_name").val("");
});
$("#map_create").click(function() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	var map_name = $("#map_name").val()
	var disk_group = $("#disk_group").val()
	var host_group = $("#host_group").val()
	$.ajax({
		url : masterIp + "/map/create",
		type : "GET",
		data : {
			transaction_id:time,
			map_name : map_name,
			disk_group : disk_group,
			host_group : host_group
		},
		success : function(operation_feedback_prompt) {
			alert(operation_feedback_prompt);
		},
		error : function() {
		}
	})
	$("#map_name").val("");
});

$('#host').selectpicker({
	width : 200
});
function host_result_select() {
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id:time
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
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/disk/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id:time
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
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/hg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			transaction_id:time
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
	var time = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
	time = time.substr(0, 10);
	$.ajax({
		url : masterIp + "/dg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			transaction_id:time
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
