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


$("#host_group_create").click(function() {
	var host_group_name = $("#host_group_name").val()
	var host = $("#host").val().toString()
	var hg_name_hid = $("#hg_name_hid").val();
	var hg_name_verify_status = $("#hg_name_verify_status").val();
	var dict_data = JSON.stringify({
		"host_group_name" : host_group_name,
		"host" : host
	});
	if (hg_name_verify_status == "0") {
		hg_name_myfunction();
	};
	if (hg_name_hid == "1") {
		write_to_log(tid,'DATA','RADIO','host','',host);
		write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/hg/create",
			type : "GET",
			data : {
				tid : tid,
				ip : mgtIp,
				host_group_name : host_group_name,
				host : host
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/create' ,operation_feedback_prompt);
				alert(operation_feedback_prompt);
				 $("#hg_name_verify_status").val("0");
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
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/create', 'error');
				
			}
		})
	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create', 'refuse', dict_data);
		alert("请输入正确值!");
	}

});


$('#host').selectpicker({
	width : 200
});
function host_result_select() {
	$.ajax({
		url : vplxIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		success : function(status) {
			write_to_log(tid,'OPRT','ROUTE',vplxIp,'/host/show/oprt',status);
			$.ajax({
				url : vplxIp + "/host/show/data",
				type : "GET",
				dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
				success : function(host_result) {
					write_to_log(tid,'DATA','ROUTE',vplxIp,'/host/show/data',JSON.stringify(host_result));
					$('#host').html("");
					var html = "";
					for (i in host_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#host').append(html);
					$('#host').selectpicker('refresh');
					$('#host').selectpicker('render');
				},
				error : function(){
					write_to_log(tid,'DATA','ROUTE',vplxIp,'/host/show/data','error');
				}
				
			});
		},
		error : function() {
			write_to_log(tid,'DATA','ROUTE',vplxIp,'/host/show/oprt','error');
		}
	});
};
host_result_select();
$(window).on('load', function() {
	$('#host').selectpicker({
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

function hg_name_myfunction() {
	$("#hg_name_verify_status").val("1");
	document.getElementById("hg_name_examine").className = "hidden";
	document.getElementById("hg_name_format").className = "hidden";
	var input_result = $('#host_group_name').val();
	var hg_name_match_regular = /^[a-zA-Z]\w*$/;
	match_result = hg_name_match_regular.test(input_result)
	if (!input_result) {
		$("#hg_name_hid").val("0");
		document.getElementById("hg_name_examine").className = "hidden";
		document.getElementById("hg_name_format").className = "hidden";

	} else {
		if (!match_result) {
			$("#hg_name_hid").val("0");
			document.getElementById("hg_name_format").className = "";
		} else {
			document.getElementById("hg_name_format").className = "hidden";
			$
			.ajax({
				url : vplxIp + "/hg/show/oprt",
				type : "GET",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(HG_result) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
							'/hg/show/oprt', HG_result);
					$
					.ajax({
						url : vplxIp + "/hg/show/data",
						type : "GET",
						dataType : "json",
								data : {
									tid : tid,
									ip : mgtIp
								},
						success : function(HG_result_data) {
							write_to_log(tid,'DATA','ROUTE',vplxIp,'/hg/show/data', JSON.stringify(HG_result_data));
							if (input_result in HG_result_data) {
								$("#hg_name_hid").val("0");
								document.getElementById("hg_name_examine").className = "";
							} else {
								write_to_log(tid,'DATA','INPUT_TEXT','host_group_name','T',input_result);
								$("#hg_name_hid").val("1");
							}
						},
						error : function() {
							write_to_log(tid,'DATA','ROUTE',vplxIp,'/hg/show/data','error');
						}
					});
					
				},
				error : function() {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
							'/hg/show/oprt', 'error');
				}
			});
		}

	}

}



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
$("#host").on("change", function(a, b, c) {
 	$("#Hg_Show_Input").val($("#host option:selected").text());
})
