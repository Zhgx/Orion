/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

// 操作提示
var masterIp = "http://10.203.1.76:7777"
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);
$("#host_create").click(
		function() {
			var hostName = $("#host_name").val()
			var hostiqn = $("#host_iqn").val()
			var host_name_hid = $("#host_name_hid").val();
			var host_iqn_hid = $("#host_iqn_hid").val();
			var host_name_verify_status =  $("#host_name_verify_status").val("1");
			var host_iqn_verify_status = $("#host_iqn_verify_status").val("1");
			var dict_data = JSON.stringify({
				"host_alias" : hostName,
				"host_iqn" : hostiqn
			});
			if (host_name_verify_status == "0") {
				host_name_myfunction();
			}else if (host_name_verify_status == "1")  {
				pass
			};
			if (host_iqn_verify_status == "0") {
				iqn_myfunction();
			}else if (host_iqn_verify_status == "1") {
				pass
			}
			if (host_name_hid == "1" && host_iqn_hid == "1") {
				$("#host_name_verify_status").val("0");
				$("#host_iqn_verify_status").val("0");
				write_to_log(tid, 'OPRT', 'CLICK', 'host_create', 'accept',
						dict_data);
				$.ajax({
					url : masterIp + "/host/create",
					type : "GET",
					data : {
						transaction_id : tid,
						host_name : hostName,
						host_iqn : hostiqn
					},
					success : function(operation_feedback_prompt) {
						write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
								'/host/create', operation_feedback_prompt);
						alert(operation_feedback_prompt);
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
						write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
								'/host/create', 'error');
					}
				})

			} else {
				write_to_log(tid, 'OPRT', 'CLICK', 'host_create', 'refuse',
						dict_data);
				alert("请输入正确值!")
			}
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

function host_name_myfunction() {
	$("#host_name_verify_status").val("1");
	document.getElementById("host_name_examine").className = "hidden";
	document.getElementById("host_name_format").className = "hidden";
	var input_result = $('#host_name').val();
	var host_name_match_regular = /^[a-zA-Z]\w*$/;
	match_result = host_name_match_regular.test(input_result)
	if (!input_result) {
		$("#host_name_hid").val("0");
		document.getElementById("host_name_examine").className = "hidden";
		document.getElementById("host_name_format").className = "hidden";
	} else {
		if (!match_result) {
			$("#host_name_hid").val("0");
			document.getElementById("host_name_format").className = "";
		} else {
			document.getElementById("host_name_format").className = "hidden";
			$
					.ajax({
						url : masterIp + "/host/show/oprt",
						type : "GET",
						dataType : "json",
						data : {
							transaction_id : tid
						},
						success : function(host_result) {
							write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
									'/host/show/oprt', host_result);

							$
									.ajax({
										url : masterIp + "/host/show/data",
										type : "GET",
										dataType : "json",
										success : function(host_result) {
											write_to_log(tid, 'DATA', 'ROUTE',
													masterIp,
													'/host/show/data',
													JSON.stringify(host_result));
											if (input_result in host_result) {
												write_to_log(tid, 'DATA',
														'INPUT_TEXT',
														'host_name', 'F',
														input_result);
												$("#host_name_hid").val("0");
												document
														.getElementById("host_name_examine").className = "";
											} else {
												write_to_log(tid, 'DATA',
														'INPUT_TEXT',
														'host_name', 'T',
														input_result);
												$("#host_name_hid").val("1");
											}
										},
										error : function() {
											write_to_log(tid, 'DATA', 'ROUTE',
													masterIp,
													'/host/show/data', 'error');
										}
									});

						},
						error : function() {
							write_to_log(tid, 'OPRT', 'ROUTE', masterIp,
									'/host/show/oprt', 'error');
						}
					});
		}
	}

}

function iqn_myfunction() {
	$("#host_iqn_verify_status").val("1");
	document.getElementById("iqn_format").className = "hidden";
	var input_result = $('#host_iqn').val();
	var iqn_match_regular = /^iqn.\d{4}-\d{2}.[a-zA-Z0-9.:-]+$/;
	match_result = iqn_match_regular.test(input_result)
	if (!input_result) {
		$("#host_iqn_hid").val("0");
		document.getElementById("iqn_format").className = "hidden";
	} else {
		if (!match_result) {
			$("#host_iqn_hid").val("0");
			write_to_log(tid, 'DATA', 'INPUT_TEXT', 'iqn', 'F', input_result)
			document.getElementById("iqn_format").className = "";
		} else {
			write_to_log(tid, 'DATA', 'INPUT_TEXT', 'iqn', 'T', input_result)
			$("#host_iqn_hid").val("1");
		}
	}
}



$('#host').selectpicker({
	width : 200
});
function host_result_select() {
	$.ajax({
		url : masterIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			transaction_id : tid
		},
		success : function(status) {
			write_to_log(tid,'OPRT','ROUTE',masterIp,'/host/show/oprt',status);
			$.ajax({
				url : masterIp + "/host/show/data",
				type : "GET",
				dataType : "json",
				success : function(host_result) {
					write_to_log(tid,'DATA','ROUTE',masterIp,'/host/show/data',JSON.stringify(host_result));
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
					write_to_log(tid,'DATA','ROUTE',masterIp,'/host/show/data','error');
				}
				
			});
		},
		error : function() {
			write_to_log(tid,'DATA','ROUTE',masterIp,'/host/show/oprt','error');
		}
	});
};
host_result_select();
$(window).on('load', function() {
	$('#host').selectpicker({
		'selectedText' : 'cat'
	});
});
