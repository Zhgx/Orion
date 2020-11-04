/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

// 操作提示
var masterIp = "http://10.203.1.76:7777"
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);

$("#disk_group_create").click(function() {
	var disk_group_name = $("#disk_group_name").val()
	var disk = $("#disk").val().toString()
	var dg_name_hid = $("#dg_name_hid").val();
	var dict_data = JSON.stringify({
		"disk_group_name" : disk_group_name,
		"disk" : disk
	});
	dg_name_myfunction();
	if (dg_name_hid == "1") {
		write_to_log(tid,'DATA','COMBO_BOX','disk','',disk);
		write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create', 'accept', dict_data);
		$.ajax({
			url : masterIp + "/dg/create",
			type : "GET",
			data : {
				transaction_id : tid,
				disk_group_name : disk_group_name,
				disk : disk
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', masterIp, '/dg/create' ,operation_feedback_prompt);
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
				write_to_log(tid, 'OPRT', 'ROUTE', masterIp, '/dg/create', 'error');
			}
		})
	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create', 'refuse', dict_data);
		alert("请输入正确值!")
	}
});

$('#disk').selectpicker({
	width : 200
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
				url : masterIp + "/dg/show/oprt",
				type : "GET",
				dataType : "json",
				data : {
					transaction_id : tid
				},
				success : function(DG_result) {
					write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
							'/dg/show/oprt', DG_result);
					$
					.ajax({
						url : masterIp + "/dg/show/data",
						type : "GET",
						dataType : "json",
						success : function(DG_result) {
							write_to_log(tid,'DATA','ROUTE',masterIp,'/dg/show/data',JSON.stringify(DG_result));
							if (input_result in DG_result) {
								$("#dg_name_hid").val("0");
								document.getElementById("dg_name_examine").className = "";
							} else {
								$("#dg_name_hid").val("1");
							}
						},
						error : function() {
							write_to_log(tid,'DATA','ROUTE',masterIp,'/dg/show/data','error');
						}
					});
				},
				error : function() {
					write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
							'/dg/show/oprt', 'error');
				}
			});
			
			
		}
	}
}

$('#disk').selectpicker({
	width : 200
});

function disk_result_select() {
	$.ajax({
		url : masterIp + "/disk/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(status) {
			write_to_log(tid,'OPRT','ROUTE',masterIp,'/disk/show/oprt',status);
			$.ajax({
				url : masterIp + "/disk/show/data",
				type : "GET",
				dataType : "json",
				success : function(disk_result) {
					write_to_log(tid,'DATA','ROUTE',masterIp,'/disk/show/data',JSON.stringify(disk_result));
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
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', masterIp, '/disk/show/data', 'error');
				}
			});
		},
		error : function() {
			write_to_log(tid, 'OPRT', 'ROUTE', masterIp, '/disk/show/oprt', 'error');
		}
	});

};
disk_result_select();
$(window).on('load', function() {
	$('#disk').selectpicker({
		'selectedText' : 'cat'
	});
});


$('#disk_group').selectpicker({
	width : 200
});

function all_dg_result_select() {
	$.ajax({
		url : masterIp + "/dg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', masterIp, '/dg/show/oprt',status);
			$.ajax({
				url : masterIp + "/dg/show/data",
				type : "get",
				dataType : "json",
				success : function(all_dg_result) {
					write_to_log(tid, 'DATA', 'ROUTE', masterIp, '/dg/show/data',JSON.stringify(all_dg_result));
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
					write_to_log(tid, 'DATA', 'ROUTE', masterIp, '/dg/show/data', 'error');
				}
			});
		},
		error : function() {
			write_to_log(tid, 'OPRT', 'ROUTE', masterIp, '/dg/show/oprt', 'error');
		}
		
	});
};
$(window).on('load', function() {
	$('#disk_group').selectpicker({
		'selectedText' : 'cat'
	});
});

