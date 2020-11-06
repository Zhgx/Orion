
var vplxIp = get_vlpx_ip();
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);



function get_vlpx_ip(){
	var obj = new Object();
	$.ajax({
		url : "http://127.0.0.1:7773/vplxip",
		type : "GET",
		dataType : "json",
		async:false,
		success : function(data) {
			obj =  "http://"+data["ip"];
		}
	});

	return obj;
}
function resource_show_data() {
	 var obj = new Object();
	$.ajax({
		type : "get",
		data:vplxIp,
		success : function(data) {
			var obj = data;
			alert(obj);
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

function resource_oprt() {
	$
			.ajax({
				url : vplxIp + "/resource/show/oprt",
				type : "get",
				dataType : "json",
				data : {
					transaction_id : tid
				},
				success : function(status) {
					write_to_log(tid,'OPRT','ROUTE',vplxIp,'/resource/show/oprt',status);
					layui
							.use(
									[ 'laydate', 'laypage', 'layer', 'table',
											'carousel', 'upload', 'element',
											'slider' ],
									function() {
										var table = layui.table // 表格
										// 执行一个 table 实例
										table
												.render({
													elem : '#demo',
													url : resource_show_data()
															+ "/resource/show/data" // 数据接口
													,
													title : '用户表',
													cols : [ [ // 表头
															{
																type : 'checkbox',
																fixed : 'left'
															},
															{
																field : 'resource',
																title : 'resource',
																sort : true
															},
															{
																field : 'mirror_way',
																title : 'mirror_way',
																event : 'collapse',
																templet : function(
																		d) {
																	return '<div style="position: relative;\n'
																			+ '    padding: 0 10px 0 20px;">'
																			+ d.mirror_way
																			+ '<i style="left: 0px;" lay-tips="展开" class="layui-icon layui-colla-icon layui-icon-right"></i></div>'
																}
															},
															{
																field : 'device_name',
																title : 'device_name',
																sort : true
															},
															{
																field : 'size',
																title : 'size',
																sort : true
															},
															{
																field : 'used',
																title : 'used',
																sort : true
															},
															{
																fixed : 'right',
																align : 'center',
																toolbar : '#barDemo'
															} ] ]
												});

										// 监听工具条
										table
												.on(
														'tool(test)',
														function(obj) {
															var data = obj.data.mirror_way_son
															// 做好数据处理，下面直接放进子表中

															if (obj.event === 'collapse') {
																var trObj = layui
																		.$(this)
																		.parent(
																				'tr'); // 当前行
																var accordion = true // 开启手风琴，那么在进行折叠操作时，始终只会展现当前展开的表格。
																var content = '<table></table>' // 内容
																// 表格行折叠方法
																collapseTable({
																	elem : trObj,
																	accordion : accordion,
																	content : content,
																	success : function(
																			trObjChildren,
																			index) { // 成功回调函数
																		// trObjChildren
																		// 展开tr层DOM
																		// index
																		// 当前层索引
																		trObjChildren
																				.find(
																						'table')
																				.attr(
																						"id",
																						index);
																		table
																				.render({
																					elem : "#"
																							+ index,

																					// url:""
																					// 两种
																					data : data,

																					limit : 10000,
																					cellMinWidth : 80,

																					cols : [ [
																							{
																								type : 'checkbox',
																								fixed : 'left'
																							},
																							{
																								field : 'node_name',
																								title : 'node_name'
																							},
																							{
																								field : 'stp_name',
																								title : 'stp_name'
																							},
																							{
																								field : 'drbd_role',
																								title : 'drbd_role',
																								sort : true
																							},

																							{
																								field : 'status',
																								title : 'status',
																								sort : true
																							},
																							{
																								fixed : 'right',
																								align : 'center',
																								toolbar : '#barDemo1'
																							} ] ]
																				});

																	}
																});

															}
														});

										function collapseTable(options) {
											var trObj = options.elem;
											if (!trObj)
												return;
											var accordion = options.accordion, success = options.success, content = options.content
													|| '';
											var tableView = trObj
													.parents('.layui-table-view'); // 当前表格视图
											var id = tableView.attr('lay-id'); // 当前表格标识
											var index = trObj.data('index'); // 当前行索引
											var leftTr = tableView
													.find('.layui-table-fixed.layui-table-fixed-l tr[data-index="'
															+ index + '"]'); // 左侧当前固定行
											var rightTr = tableView
													.find('.layui-table-fixed.layui-table-fixed-r tr[data-index="'
															+ index + '"]'); // 右侧当前固定行
											var colspan = trObj.find('td').length; // 获取合并长度
											var trObjChildren = trObj.next(); // 展开行Dom
											var indexChildren = id + '-'
													+ index + '-children'; // 展开行索引
											var leftTrChildren = tableView
													.find('.layui-table-fixed.layui-table-fixed-l tr[data-index="'
															+ indexChildren
															+ '"]'); // 左侧展开固定行
											var rightTrChildren = tableView
													.find('.layui-table-fixed.layui-table-fixed-r tr[data-index="'
															+ indexChildren
															+ '"]'); // 右侧展开固定行
											var lw = leftTr.width() + 15; // 左宽
											var rw = rightTr.width() + 15; // 右宽
											// 不存在就创建展开行
											if (trObjChildren.data('index') != indexChildren) {
												// 装载HTML元素
												var tr = '<tr data-index="'
														+ indexChildren
														+ '"><td colspan="'
														+ colspan
														+ '"><div style="height: auto;padding-left:'
														+ lw
														+ 'px;padding-right:'
														+ rw
														+ 'px" class="layui-table-cell">'
														+ content
														+ '</div></td></tr>';
												trObjChildren = trObj.after(tr)
														.next().hide(); // 隐藏展开行
												var fixTr = '<tr data-index="'
														+ indexChildren
														+ '"></tr>';// 固定行
												leftTrChildren = leftTr.after(
														fixTr).next().hide(); // 左固定
												rightTrChildren = rightTr
														.after(fixTr).next()
														.hide(); // 右固定
											}
											// 展开|折叠箭头图标
											trObj
													.find(
															'td[lay-event="collapse"] i.layui-colla-icon')
													.toggleClass(
															"layui-icon-right layui-icon-down");
											// 显示|隐藏展开行
											trObjChildren.toggle();
											// 开启手风琴折叠和折叠箭头
											if (accordion) {
												trObj
														.siblings()
														.find(
																'td[lay-event="collapse"] i.layui-colla-icon')
														.removeClass(
																"layui-icon-down")
														.addClass(
																"layui-icon-right");
												trObjChildren
														.siblings(
																'[data-index$="-children"]')
														.hide(); // 展开
												rightTrChildren
														.siblings(
																'[data-index$="-children"]')
														.hide(); // 左固定
												leftTrChildren
														.siblings(
																'[data-index$="-children"]')
														.hide(); // 右固定
											}
											success(trObjChildren,
													indexChildren); // 回调函数
											heightChildren = trObjChildren
													.height(); // 展开高度固定
											rightTrChildren.height(
													heightChildren + 115)
													.toggle(); // 左固定
											leftTrChildren.height(
													heightChildren + 115)
													.toggle(); // 右固定
										}

									});

				},
				error:function () {
					write_to_log(tid,'OPRT','ROUTE',vplxIp,'/resource/show/oprt','error');

				}

			});
};
resource_oprt();
