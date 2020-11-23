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
			console.log("okokok");
			console.log(data["ip"]);
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

host_table();
function host_table() {
	$.ajax({
		url : vplxIp + "/host/show/oprt",
		type : "GET",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		success : function(status) {
			write_to_log(tid, 'OPRT', 'ROUTE', vplxIp, '/host/show/oprt',
					status);
			$.ajax({
				url : vplxIp + "/host/show/data",
				type : "GET",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(host_result) {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/host/show/data', JSON.stringify(host_result));
					for (i in host_result) {
						tr = '<td >' + i + '</td>'
						$("#H_T").append(
								'<tr onClick="change_host(this)" >' + tr + '</tr>')
					}
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/host/show/data', 'error');
				}

			});
		},
		error : function() {
			write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/host/show/oprt',
					'error');
		}
	});
};

function change_host(obj) {
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells;
		var td_host = td[0].innerHTML;
			$.ajax({
				url : vplxIp + "/host/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(host_result) {
					// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
					// '/hg/show/data', JSON
					// .stringify(host_group_result));
					for (j in host_result) {
						if (td_host == j) {
							var iqn = host_result[j]
			// $("#H_IQN_Table_Show tr:not(:first)").html("");
								tr = '<td >' + iqn + '</td>';
								$("#H_IQN_T_Show").append('<tr >' + tr + '</tr>')
						}
					}
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
							'error');
				}

			});
		$("#H_T_Show").append(
				'<tr onClick="change_host_second(this)">' + tr + '</tr>');
		curRow.remove();// 删除
	}
}
// var td = curRow.cells
// for(var i = 0; i<td.length; i++ ){
// var bb = td[i].innerHTML
// obj.push(bb);
// $("#H_T_Show").append(obj);
// alert(obj);
// }
// if (curRow.style.background) {//变颜色
// curRow.style.background="";
// }else {
// curRow.style.background="blue";
// }
//
function change_host_second() {
	var obj_list = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML
		$("#H_T").append('<tr onClick="change_host(this)" >' + tr + '</tr>')
		curRow.remove();
		// var count=0;
		for (i=1; i < window.HTable_Show.rows.length; i++) {
		for (j=0; j < window.HTable_Show.rows[i].cells.length; j++) { 
			obj_list.push(window.HTable_Show.rows[i].cells[j].innerHTML) 
			}
		}
		$("#H_IQN_Table_Show tr:not(:first)").html("");
		
			$.ajax({
				url : vplxIp + "/host/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(host_result) {
					for ( i in obj_list) {
						var iqn = host_result[obj_list[i]];
							tr = '<td >' + iqn + '</td>';
							$("#H_IQN_T_Show").append('<tr >' + tr + '</tr>')
					}
					// write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
					// '/hg/show/data', JSON
					// .stringify(host_group_result));
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp, '/dg/show/data',
							'error');
				}

			});

		
	}
}


// 获取表格td值
// function numberCells() {
// var obj_list = [];
// var count=0;
// for (i=1; i < window.HTable_Show.rows.length; i++) {
// for (j=0; j < window.HTable_Show.rows[i].cells.length; j++) {
// obj_list.push(window.HTable_Show.rows[i].cells[j].innerHTML)
// }
// }
// alert(obj_list);
// }






// 输入框验证
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
											var objj =[];
											for (i in HG_result_data) {
												objj.push(i);
											}
											write_to_log(
													tid,
													'DATA',
													'ROUTE',
													vplxIp,
													'/hg/show/data',
													JSON
															.stringify(HG_result_data));
											if (input_result in objj) {
												$("#hg_name_hid").val("0");
												document
														.getElementById("hg_name_examine").className = "";
											} else {
												write_to_log(tid, 'DATA',
														'INPUT_TEXT',
														'host_group_name', 'T',
														input_result);
												$("#hg_name_hid").val("1");
											}
										},
										error : function() {
											write_to_log(tid, 'DATA', 'ROUTE',
													vplxIp, '/hg/show/data',
													'error');
										}
									});

						},
						error : function() {
							write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
									'/hg/show/oprt', 'error');
						}
					});
		}
	};
}

$("#host_group_create").click(
		function() {
			var obj_host = [];
			var tableId = document.getElementById("HTable_Show");
			var str = "";
			for (var i = 1; i < tableId.rows.length; i++) {
				obj_host.push(tableId.rows[i].cells[0].innerHTML)
			}
			obj_host_str = obj_host.toString();
			var host_group_name = $("#host_group_name").val()
			// var host = $("#host").val().toString()
			var dict_data = JSON.stringify({
				"host_group_name" : host_group_name,
				"host" : obj_host_str
			});
			hg_name_myfunction();
			var host_group_name = $("#hg_name_hid").val()
			console.log(hg_name_hid);
			if (hg_name_hid == "1") {
				write_to_log(tid, 'DATA', 'RADIO', 'host', '', obj_host_str);
				write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create',
						'accept', dict_data);
				$.ajax({
					url : vplxIp + "/hg/create",
					type : "GET",
					data : {
						tid : tid,
						ip : mgtIp,
						host_group_name : host_group_name,
						host : obj_host_str
					},
					success : function(operation_feedback_prompt) {
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/hg/create', operation_feedback_prompt);
						$("#host_group_name").val("");
						$("#hg_name_hid").val("0");
					},
					error : function() {
						write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
								'/hg/create', 'error');

					}
				})
			} else {
				write_to_log(tid, 'OPRT', 'CLICK', 'host_group_create',
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


