/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

//操作提示
//host

var master_ip = "http://10.203.1.76:7777"

function host_name_myfunction(){
	document.getElementById("host_name_examine").className = "hidden";
	var input_result = $('#host_name').val();
	$
			.ajax({
				url : master_ip + "/all_host_result",
				type : "GET",
				dataType : "json",
				success : function(host_result) {
					for (i in host_result) {
						if (i == input_result) {
							document.getElementById("host_name_examine").className = "";
						}
					}
				}
			});
}

function hg_name_myfunction() {
	document.getElementById("hg_name_examine").className = "hidden";
	var input_result = $('#host_group_name').val();
	$.ajax({
		url : master_ip + "/all_hg_result",
		type : "GET",
		dataType : "json",
		success : function(HG_result) {
			for (i in HG_result) {
				if (i == input_result) {
					document.getElementById("hg_name_examine").className = "";
				}
			}
		}
	});
}

function dg_name_myfunction() {
	document.getElementById("dg_name_examine").className = "hidden";
	var input_result = $('#disk_group_name').val();
	$.ajax({
		url : master_ip + "/all_dg_result",
		type : "GET",
		dataType : "json",
		success : function(DG_result) {
			for (i in DG_result) {
				if (i == input_result) {
					document.getElementById("dg_name_examine").className = "";
				}
			}
		}
	});
}

function map_name_myfunction() {
	document.getElementById("map_name_examine").className = "hidden";
	var input_result = $('#map_name').val();
	$.ajax({
		url : master_ip + "/all_map_result",
		type : "GET",
		dataType : "json",
		success : function(Map_result) {
			for (i in Map_result) {
				if (i == input_result) {
					document.getElementById("map_name_examine").className = "";
				}
			}
		}
	});
}
