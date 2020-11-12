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
												+ '<input type="checkbox" id="checkbox" name="checkbox"  checked＝"false";"/>'
												+ '</td>' + '<td name="id">' + i
												+ '</td>'
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
		
		var products = [];  
		var ordernums = [];  
		var ordernums1 = []; 
		var $span = $("input[name=checkbox]:checked");
		var $tds = $("td").has($span);     //定义选中复选框的单元格 
		var $trs = $("tr").has($tds);  
		for(var i=0; i<$trs.length;i++){  
		var product = $("td:eq(1)",$($trs[i])).html();   //获取选中的C3单元格的值
		products.push(product);     //将选中的值放到数组中
		$("#H_T_Show").html("");
		for (i in products) {
			tr = '<td >'
				+ '<input type="checkbox" id="checkbox1" name="checkbox1"  checked＝"false";"/>'
				+ '</td>' + '<td>' + products[i]
			+ '</td>' 
			$("#H_T_Show").append(
					'<tr>'
					+ tr + '</tr>')
		}
		}
	});
});

$(function() {
			  var obt=document.getElementById("btn1");
			  var otb=document.getElementById("HTable_Show");
			  var tbody=otb.getElementsByTagName("tbody")[0];  
			  obt.onclick=function(){
			    var cks=document.getElementsByName("checkbox1");
			    for(var index=0;index<cks.length;index++){
			      if(cks[index].checked==true){
			        tbody.removeChild(cks[index].parentNode.parentNode);
			      }
			    }
			  }
});

