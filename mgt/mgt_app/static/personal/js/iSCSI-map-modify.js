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
	$.ajax({
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
					console.log(map_group_result);
					for ( var i in map_group_result) {
						tr = '<td  >' + i + '</td>'
								+ '<td onClick="change_hostgroup(this)">'
								+ map_group_result[i]["HostGroup"] + '</td>'
								+ '<td  onClick="change_diskgroup(this)">'
								+ map_group_result[i]["DiskGroup"] + '</td>';
						$("#M_T").append('<tr >' + tr + '</tr>')
					}
				},
			});
		},
	});

};

function change_hostgroup(obj) {
	//弹出框
	$('tr').each(function() {
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
		var td_map = td[0].innerHTML
		var hg = td[1].innerHTML
	}
	td_hg = hg.split(",");
	//		td_hg = JSON.stringify(hg);
	// 获取hostgroup的值
	$.ajax({
		url : vplxIp + "/hg/show/data",
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp
		},
		async : false,
		success : function(host_group_result) {
			$.ajax({
				url : vplxIp + "/hg/show/data",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async : false,
				success : function(hg_result) {
					$("#HG_Table tr:not(:first)").html("");
					for ( var i in hg_result) {
						for ( var j in td_hg) {
							if (td_hg[j] == i) {
								tr = '<td >' + td_map + '</td>' + '<td >'
										+ td_hg[j] + '</td>' + '<td >'
										+ hg_result[i] + '</td>' + '<td >'
										+ '<button  onClick="confirm_model_btn(this);">删除</button>' + '</td>';
								//									'<td >' + '删除' + '</td>';
								$("#HG_T").append(
										'<tr>'
												+ tr + '</tr>')
							}
						}
					}
				},
			});
		},

	});
}

function confirm_model_btn(obj) {
	$('tr').each(function() {
		$(this).on("click", function() {
			$("#confirm_model").modal("toggle");
		})
	});
	var e = e || window.event;
	var target = e.target || e.srcElement;
	if (target.parentNode.tagName.toLowerCase() == "td") {
	tr = target.parentNode.parentNode;
	td = tr.cells;
	 for(var i = 0; i<td.length; i++ ){
	 var td_map = td[0].innerHTML
	 var td_hg = td[1].innerHTML
	 }
	}
	$("#map_hid").val(td_map);
	$("#hg_hid").val(td_hg);
	$.ajax({
		url : vplxIp + "/map/modify/check",
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp,
			map : td_map,
			hg : td_hg
		},
		async : false,
		success : function(map_result) {
			$("#hg_hid_data").val( JSON.stringify(map_result['iscsi_data']));
			$("#map_result").text(map_result['info']);
		},
	});
}
//
//$(function() {
//    $('#confirm_model').on('hide.bs.modal',
//    function() {
//        alert('嘿，我听说您喜欢模态框...');
//    })
//});

function hg_remove(obj) {
	td_map = $("#map_hid").val();
	td_hg = $("#hg_hid").val();
	hg_hid_data = $("#hg_hid_data").val();
	console.log(typeof(hg_hid_data));
	console.log(typeof(td_hg));
	console.log(td_hg);
	$.ajax({
		url : vplxIp + "/map/modify",
		type : "get",
		dataType : "json",
		data : {
			tid : tid,
			ip : mgtIp,
			map : td_map,
			hg : td_hg,
			iscsi_data:hg_hid_data
		},
		async : false,
		success : function(map_result) {
			$("#map_hid").val("");
			$("#hg_hid").val("");
			alert(map_result);
		},
	});
}

function change_diskgroup(obj) {
	// 获取点击表格的td值
	var obj = [];
	if (event.srcElement.tagName == "TD") {
		curRow = event.srcElement.parentElement;
		tr = curRow.innerHTML;
		var td = curRow.cells
		//		 for (var i = 0; i < td.length; i++) {
		var td_disk = td[2].innerHTML
		//		 }
		console.log(td_disk);
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