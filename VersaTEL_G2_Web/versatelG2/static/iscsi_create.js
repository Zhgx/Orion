/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

//操作提示
//host
function Host_Name_myFunction() {
	document.getElementById("Host_Name_Examine").className = "hidden";
	var input_result = $('#Host_Name').val();
	$
			.ajax({
				url : "http://10.203.1.76:7777/all_host_result",
				type : "GET",
				dataType : "json",
				success : function(host_result) {
					for (i in host_result) {
						if (i == input_result) {
							document.getElementById("Host_Name_Examine").className = "";
						}
					}
				}
			});
}

// hostgroup
function HG_Name_myFunction() {
	document.getElementById("HG_Name_Examine").className = "hidden";
	var input_result = $('#HostGroup_Name').val();
	$.ajax({
		url : "http://10.203.1.76:7777/all_hg_result",
		type : "GET",
		dataType : "json",
		success : function(HG_result) {
			for (i in HG_result) {
				if (i == input_result) {
					document.getElementById("HG_Name_Examine").className = "";
				}
			}
		}
	});
}

function DG_Name_myFunction() {
	document.getElementById("DG_Name_Examine").className = "hidden";
	var input_result = $('#DiskGroup_Name').val();
	$.ajax({
		url : "http://10.203.1.76:7777/all_hg_result",
		type : "GET",
		dataType : "json",
		success : function(DG_result) {
			for (i in DG_result) {
				if (i == input_result) {
					document.getElementById("DG_Name_Examine").className = "";
				}
			}
		}
	});
}

function Map_Name_myFunction() {
	document.getElementById("Map_Name_Examine").className = "hidden";
	var input_result = $('#Map_Name').val();
	$.ajax({
		url : "http://10.203.1.76:7777/all_hg_result",
		type : "GET",
		dataType : "json",
		success : function(Map_result) {
			for (i in Map_result) {
				if (i == input_result) {
					document.getElementById("Map_Name_Examine").className = "";
				}
			}
		}
	});
}



