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
	$
			.ajax({
				url : vplxIp + "/host/show/oprt",
				type : "GET",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				success : function(status) {
					write_to_log(tid, 'OPRT', 'ROUTE', vplxIp,
							'/host/show/oprt', status);
					$
							.ajax({
								url : vplxIp + "/host/show/data",
								type : "GET",
								dataType : "json",
								data : {
									tid : tid,
									ip : mgtIp
								},
								success : function(host_result) {
									write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
											'/host/show/data', JSON
													.stringify(host_result));
									for (i in host_result) {
										tr = '<td >'
												+ '<input type="checkbox" name="checkbox" οnclick="test(this);"/>'
												+ '</td>' + '<td name="id">' + i
												+ '</td>' + '<td name="name">'
												+ host_result[i] + '</td>'
										$("#H_T").append(
												'<tr>'
														+ tr + '</tr>')
									}
								},
								error : function() {
									write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
											'/host/show/data', 'error');
								}

							});
				},
				error : function() {
					write_to_log(tid, 'DATA', 'ROUTE', vplxIp,
							'/host/show/oprt', 'error');
				}
			});
};



$(function() {
	$("#btn").on('click', function() {
		function check() {
            var check = $("input[type='checkbox']:checked");//在table中找input下类型为checkbox属性为选中状态的数据
            var i = 0;
            check.each(function(){
                i++;
            });
            console.log(i);
              check.each(function () {//遍历
                  var row = $(this).parent("td").parent("tr");
                var id = row.find("[name='id']").html(); //注意html()和val()
                var name = row.find("[name='name']").html(); 
                console.log(id+","+name)
            })
        }
		
		
	});
});


