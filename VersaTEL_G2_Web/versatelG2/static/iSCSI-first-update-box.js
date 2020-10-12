/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

//操作提示
$('#Host').selectpicker({
	width : 200
});
function host_result_select()  {
	$.ajax({
		url : "http://10.203.1.76:7777/oprt_all_host",
		type : "GET",
		dataType : "json",
		success : function() {
			$.ajax({
				url : "http://10.203.1.76:7777/all_host_result",
				type : "GET",
				dataType : "json",
				success : function(host_result) {
					$('#Host').html("");
					var html = "";
					for (i in host_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#Host').append(html);
					$('#Host').selectpicker('refresh');
					$('#Host').selectpicker('render');
				}
			});
		}
	});
});
host_result_select()
$(window).on('load', function() {
	$('#Host').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#Disk').selectpicker({
	width : 200
});

function disk_result_select()  {
	$.ajax({
		url : "http://10.203.1.76:7777/oprt_all_disk",
		type : "GET",
		dataType : "json",
		success : function() {
			$.ajax({
				url : "http://10.203.1.76:7777/all_disk_result",
				type : "GET",
				dataType : "json",
				success : function(Disk_result) {
					// var _data = data.data; //由于后台传过来的json有个data，在此重命名
					$('#Disk').html("");
					var html = "";
					for (i in Disk_result) {
						// alert(i);
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#Disk').append(html);
					// 缺一不可
					$('#Disk').selectpicker('refresh');
					$('#Disk').selectpicker('render');
				}
			});
		}
	});

});
disk_result_select()
$(window).on('load', function() {
	$('#Disk').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#Host_Group').selectpicker({
	width : 200
});

function all_hg_result_select()  {
	$.ajax({
		url : "http://10.203.1.76:7777/oprt_all_hg",
		type : "get",
		dataType : "json",
		success : function() {
			$.ajax({
				url : "http://10.203.1.76:7777/all_hg_result",
				type : "get",
				dataType : "json",
				success : function(Host_Group_result) {
					// var _data = data.data; //由于后台传过来的json有个data，在此重命名
					$('#Host_Group').html("");
					var html = "";
					for (i in Host_Group_result) {
						html += '<option value=' + i + '>' + i + '</option>'
					}
					$('#Host_Group').append(html);
					// 缺一不可
					$('#Host_Group').selectpicker('refresh');
					$('#Host_Group').selectpicker('render');
				}
			});

		}
	});

});
all_hg_result_select()
$(window).on('load', function() {
	$('#Host_Group').selectpicker({
		'selectedText' : 'cat'
	});
});

$('#Disk_Group').selectpicker({
	width : 200
});

function all_dg_result_select() {
	$.ajax({
		url : "http://10.203.1.76:7777/oprt_all_dg",
		type : "get",
		dataType : "json",
		success : function(data) {

			$.ajax({
				url : "http://10.203.1.76:7777/all_dg_result",
				type : "get",
				dataType : "json",
				success : function(all_dg_result) {
					$('#Disk_Group').html("");
					var html = "";
					for (i in all_dg_result) {
						$('#Disk_Group').append(
								'<option value=' + i + '>' + i + '</option>')
					}
					// 缺一不可
					$('#Disk_Group').selectpicker('refresh');
					$('#Disk_Group').selectpicker('render');
				}
			});
		}
	});
});
all_dg_result_select()
$(window).on('load', function() {
	$('#Disk_Group').selectpicker({
		'selectedText' : 'cat'
	});
});
