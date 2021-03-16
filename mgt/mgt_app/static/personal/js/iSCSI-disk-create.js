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
// 输入框验证


host_table();
function host_table() {
	$
			.ajax({
				url : vplxIp + "/disk/show/oprt",
				type : "GET",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(status) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
							'/disk/show/oprt', status);
					$
							.ajax({
								url : vplxIp + "/disk/show/data",
								type : "GET",
								dataType : "json",
								data : {
									tid : tid,
									ip : mgtIp
								},
								async : false,
								success : function(disk_result) {
									write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
											'/disk/show/data', JSON
													.stringify(disk_result));
									for (i in disk_result) {
										tr = '<td style="width: 100px;">'
												+ i
												+ '</td>'
												+ '<td>'
												+ disk_result[i]
												+ '</td>'
												;
										$("#Disk_Table_Show").append(
												'<tr>' + tr + '</tr>')
									}
								},
								error : function() {
									write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
											'/disk/show/data', 'error');
								}

							});
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/disk/show/oprt', 'error');
				}
			});
};
