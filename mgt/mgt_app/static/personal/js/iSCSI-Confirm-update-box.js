/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

// 操作提示
var vplxIp = get_vlpx_ip();
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);

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


$("#host_create").click(function() {
	var hostName = $("#host_name").val()
	var hostiqn = $("#host_iqn").val()
	var host_name_hid = $("#host_name_hid").val();
	var host_iqn_hid = $("#host_iqn_hid").val();
	var dict_data = JSON.stringify({
		"host_alias" : hostName,
		"host_iqn" : hostiqn
	});
	if (host_name_hid == "1" && host_iqn_hid == "1") {
		write_to_log(tid, 'OPRT', 'CLICK', 'host_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/host/create",
			type : "GET",
			data : {
				tid : tid,
				host_name : hostName,
				host_iqn : hostiqn
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/host/create' ,operation_feedback_prompt);
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
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/host/create', 'error');
			}
		})

	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'host_create', 'refuse', dict_data);
		alert("请输入正确值!")
	}
});
$("#host_group_create").click(function() {
	var host_group_name = $("#host_group_name").val()
	var host = $("#host").val().toString()
	var hg_name_hid = $("#hg_name_hid").val();
	var dict_data = JSON.stringify({
		"host_group_name" : host_group_name,
		"host" : host
	});
	if (hg_name_hid == "1") {
		write_to_log(tid,'DATA','RADIO','host','',host);
		write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/hg/create",
			type : "GET",
			data : {
				tid : tid,
				host_group_name : host_group_name,
				host : host
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/create' ,operation_feedback_prompt);
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
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/create', 'error');
				
			}
		})
	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create', 'refuse', dict_data);
		alert("请输入正确值!");
	}

});

$("#disk_group_create").click(function() {
	var disk_group_name = $("#disk_group_name").val()
	var disk = $("#disk").val().toString()
	var dg_name_hid = $("#dg_name_hid").val();
	var dict_data = JSON.stringify({
		"disk_group_name" : disk_group_name,
		"disk" : disk
	});
	if (dg_name_hid == "1") {
		write_to_log(tid,'DATA','RADIO','disk','',disk);
		write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/dg/create",
			type : "GET",
			data : {
				tid : tid,
				disk_group_name : disk_group_name,
				disk : disk
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/create' ,operation_feedback_prompt);
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
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/create', 'error');
			}
		})
	} else {
		write_to_log(tid, 'OPRT', 'CLICK', 'disk_group_create', 'refuse', dict_data);
		alert("请输入正确值!")
	}
});
$("#map_create").click(function() {
	var map_name = $("#map_name").val()
	var disk_group = $("#disk_group").val()
	var host_group = $("#host_group").val()
	var map_name_hid = $("#map_name_hid").val();
	var dict_data = JSON.stringify({
		"map_name" : map_name,
		"disk_group" : disk_group,
		"host_group" : host_group
	});
	if (map_name_hid == "1") {
		write_to_log(tid,'DATA','CHECKBOX','host group','',host_group);
		write_to_log(tid,'DATA','CHECKBOX','disk group','',disk_group);
		write_to_log(tid, 'OPRT', 'CLICK', 'map_create', 'accept', dict_data);
		$.ajax({
			url : vplxIp + "/map/create",
			type : "GET",
			data : {
				tid : tid,
				map_name : map_name,
				disk_group : disk_group,
				host_group : host_group
			},
			success : function(operation_feedback_prompt) {
				write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/map/create' ,operation_feedback_prompt);
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

$('#host').selectpicker({
	width : 200
});
function host_result_select() {
	$.ajax({
		url : vplxIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			tid : tid
		},
		success : function(status) {
			write_to_log(tid,'OPRT','ROUTE',vplxIp,'/host/show/oprt',status);
			$.ajax({
				url : vplxIp + "/host/show/data",
				type : "GET",
				dataType : "json",
						data : {
			tid : tid
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

$('#host_group').selectpicker({
	width : 200
});

function all_hg_result_select() {
	$.ajax({
		url : vplxIp + "/hg/show/oprt",
		type : "get",
		dataType : "json",
		data : {
			tid : tid
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/hg/show/oprt', status);
			$.ajax({
				url : vplxIp + "/hg/show/data",
				type : "get",
				dataType : "json",
						data : {
			tid : tid
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
			tid : tid
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/dg/show/oprt',status);
			$.ajax({
				url : vplxIp + "/dg/show/data",
				type : "get",
				dataType : "json",
						data : {
			tid : tid
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

function host_name_myfunction() {
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
						url : vplxIp + "/host/show/oprt",
						type : "GET",
						dataType : "json",
						data : {
							tid : tid
						},
						success : function(host_result) {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/host/show/oprt', host_result);

							$
									.ajax({
										url : vplxIp + "/host/show/data",
										type : "GET",
										dataType : "json",
												data : {
			tid : tid
		},
										success : function(host_result) {
											write_to_log(tid,'DATA','ROUTE',vplxIp,'/host/show/data', JSON.stringify(host_result));
											if (input_result in host_result) {
												write_to_log(tid,'DATA','TEXT','host_name','F',input_result);
												$("#host_name_hid").val("0");
												document
														.getElementById("host_name_examine").className = "";
											} else {
												write_to_log(tid,'DATA','TEXT','host_name','T',input_result);
												$("#host_name_hid").val("1");
											}
										},
										error : function() {
											write_to_log(tid,'DATA','ROUTE',vplxIp,'/host/show/data','error');
										}
									});

						},
						error : function() {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,'/host/show/oprt', 'error');
						}
					});
		}
	}

}

function hg_name_myfunction() {
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
					tid : tid
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
			tid : tid
		},
						success : function(HG_result_data) {
							write_to_log(tid,'DATA','ROUTE',vplxIp,'/hg/show/data', JSON.stringify(HG_result_data));
							if (input_result in HG_result_data) {
								$("#hg_name_hid").val("0");
								document.getElementById("hg_name_examine").className = "";
							} else {
								write_to_log(tid,'DATA','TEXT','host_group_name','T',input_result);
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
			tid : tid
		},
				success : function(DG_result) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
							'/dg/show/oprt', DG_result);
					$
					.ajax({
						url : vplxIp + "/dg/show/data",
						type : "GET",
						dataType : "json",
								data : {
			tid : tid
		},
						success : function(DG_result) {
							write_to_log(tid,'DATA','ROUTE',vplxIp,'/dg/show/data',JSON.stringify(DG_result));
							if (input_result in DG_result) {
								$("#dg_name_hid").val("0");
								document.getElementById("dg_name_examine").className = "";
							} else {
								$("#dg_name_hid").val("1");
							}
						},
						error : function() {
							write_to_log(tid,'DATA','ROUTE',vplxIp,'/dg/show/data','error');
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
			tid : tid
		},
						success : function(map_result) {
							write_to_log(tid,'OPRT','ROUTE',vplxIp,'/map/show/oprt',map_result);
							$
									.ajax({
										url : vplxIp + "/map/show/data",
										type : "GET",
										dataType : "json",
												data : {
			tid : tid
		},
										success : function(Map_result) {
											write_to_log(tid,'DATA','ROUTE',vplxIp,'/map/show/data',Map_result);
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
function iqn_myfunction() {
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
			write_to_log(tid,'DATA','TEXT','iqn','F',input_result)
			document.getElementById("iqn_format").className = "";
		} else {
			write_to_log(tid,'DATA','TEXT','iqn','T',input_result)
			$("#host_iqn_hid").val("1");
		}
	}
}
