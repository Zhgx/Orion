/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

//操作提示
//host
var masterIp = "http://10.203.1.76:7777"

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
						url : masterIp + "/host/show/data",
						type : "GET",
						dataType : "json",
						success : function(host_result) {
							if (input_result in host_result) {
								$("#host_name_hid").val("0");
								document.getElementById("host_name_examine").className = "";
							} else {
								$("#host_name_hid").val("1");
							}
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
			document.getElementById("hg_name_format").className = "";
		} else {
			document.getElementById("hg_name_format").className = "hidden";
			$
					.ajax({
						url : masterIp + "/hg/show/data",
						type : "GET",
						dataType : "json",
						success : function(HG_result) {
							if (input_result = HG_result) {
								$("#hg_name_hid").val("0");
								document.getElementById("hg_name_examine").className = "";
							} else {
								$("#hg_name_hid").val("1");
							}
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
			document.getElementById("dg_name_format").className = "";
		} else {
			document.getElementById("dg_name_format").className = "hidden";
			$
					.ajax({
						url : masterIp + "/dg/show/data",
						type : "GET",
						dataType : "json",
						success : function(DG_result) {
							if (input_result in DG_result) {
								$("#dg_name_hid").val("0");
								document.getElementById("dg_name_examine").className = "";
							} else {
								$("#dg_name_hid").val("1");
							}
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
			document.getElementById("map_name_format").className = "";
		} else {

			document.getElementById("map_name_format").className = "hidden";
			$
					.ajax({
						url : masterIp + "/map/show/data",
						type : "GET",
						dataType : "json",
						success : function(Map_result) {
							if (input_result in Map_result) {
								$("#map_name_hid").val("0");
								document.getElementById("map_name_examine").className = "";
							} else {
								$("#map_name_hid").val("1");
							}
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
			document.getElementById("iqn_format").className = "";
		} else {
			$("#host_iqn_hid").val("1");
		}
	}
}
