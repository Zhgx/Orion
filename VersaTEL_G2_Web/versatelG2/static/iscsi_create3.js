/*
 * 2020.9.29 Paul
 * note : 英文简写说明
 * 
 * */

//操作提示
$("#Host_create").click(function() {
	var Host_Name = $("#Host_Name").val()
	var Host_iqn = $("#Host_iqn").val()
	$.ajax({
		url : "http://10.203.1.76:7777/Host_create",
		type : "GET",
		data : {
			Host_Name : Host_Name,
			Host_iqn : Host_iqn
		},
		success : function(data) {

			alert(data);
		},
		error : function() {
		}
	})
	$("#Host_Name").val("");
	$("#Host_iqn").val("");
});
// /////////////////////////////////////////////
$("#HostGroup_create").click(function() {
	var HostGroup_Name = $("#HostGroup_Name").val()
	var Host = $("#Host").val().toString()
	$.ajax({
		url : "http://10.203.1.76:7777/HostGroup_create",
		type : "GET",
		data : {
			HostGroup_Name : HostGroup_Name,
			Host : Host
		},
		success : function(data) {
			alert(data);

			// $("#double").val(data);
			// 赋值
		},
		error : function() {
		}
	})
	$("#HostGroup_Name").val("");
});
// /////////////////////////////////////////////
$("#DiskGroup_create").click(function() {
	var DiskGroup_Name = $("#DiskGroup_Name").val()
	var Disk = $("#Disk").val().toString()
	$.ajax({
		url : "http://10.203.1.76:7777/DiskGroup_create",
		type : "GET",
		data : {
			DiskGroup_Name : DiskGroup_Name,
			Disk : Disk
		},
		success : function(data) {
			alert(data);
		},
		error : function() {
		}
	})
	$("#DiskGroup_Name").val("");
});
// ///////////////////////////
$("#Map_create").click(function() {
	var Map_Name = $("#Map_Name").val()
	var Disk_Group = $("#Disk_Group").val()
	var Host_Group = $("#Host_Group").val()
	$.ajax({
		url : "http://10.203.1.76:7777/Map_create",
		type : "GET",
		data : {
			Map_Name : Map_Name,
			Disk_Group : Disk_Group,
			Host_Group : Host_Group
		},
		success : function(data) {
			alert(data);
		},
		error : function() {
		}
	})
	$("#Map_Name").val("");
});