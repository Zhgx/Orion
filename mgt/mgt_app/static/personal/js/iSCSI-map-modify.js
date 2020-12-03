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
		success : function(write_log_result) {
		}
	});
}

map_table();
function map_table() {
	$
			.ajax({
				url : vplxIp + "/map/show/oprt",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(status) {
					$.ajax({
						url : vplxIp + "/map/show/data",
						type : "get",
						dataType : "json",
						data : {
							tid : tid,
							ip : mgtIp
						},
						async : false,
						success : function(map_group_result) {
							for (i in map_group_result) {
								tr = '<td  >' + i + '</td>'+
									'<td   onClick="change_hostgroup(this)">' + map_group_result[i][0] + '</td>'+
									'<td  onClick="change_diskgroup(this)">' + map_group_result[i][1] + '</td>';
								$("#M_T").append(
										'<tr >'
												+ tr + '</tr>')
							}
							},
					});
				},
			});

};

function change_hostgroup(obj) {
	//弹出框
	   $('tr').each(function () {
	        $(this).on("click", function() {
	            $("#host_model").modal("toggle");
	        })
	    });
	// 获取点击表格的td值
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells
//		 for (var i = 0; i < td.length; i++) {
		var td_host = td[1].innerHTML
//		 }
		console.log(td_host);
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
				$.ajax({
					url : vplxIp + "/hg/show/data",
					type : "get",
					dataType : "json",
					data : {
						tid : tid,
						ip : mgtIp
					},
					success : function(host_result) {
						for ( var i in host_result) {
							if (td_host == i ) {
								console.log(td_host);
								tr = '<td >' + i + '</td>'+
									'<td >' + host_result[i] + '</td>'+
									'<td >' + '<button onClick="confirm_model_btn()">删除</button>' + '</td>';
								$("#HG_T").append('<tr >' + tr + '</tr>')
							}
						}
					},
				});
			},

		});
	}
}


function confirm_model_btn() {
	  $('tr').each(function () {
	        $(this).on("click", function() {
	            $("#confirm_model").modal("toggle");
	        })
	    });
}
	

function hg_remove(obj) {
	var theRow = obj.parentNode.parentNode.rowIndex;
	document.getElementById("HG_Table").deleteRow(theRow); 
}







function change_diskgroup(obj) {
	// 获取点击表格的td值
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells
//		 for (var i = 0; i < td.length; i++) {
		var td_host = td[2].innerHTML
//		 }
		console.log(td_host);
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
				$.ajax({
					url : vplxIp + "/host/show/data",
					type : "get",
					dataType : "json",
					data : {
						tid : tid,
						ip : mgtIp
					},
					success : function(host_result) {
						
					},
				});
			},

		});
	}
}