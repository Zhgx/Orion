
var vplxIp = get_vlpx_ip();
var tid = Date.parse(new Date()).toString();// 获取到毫秒的时间戳，精确到毫秒
var tid = tid.substr(0, 10);
var mgtIp = get_mgt_ip();

function get_mgt_ip(){
	var obj = new Object();
	$.ajax({
		url : "/mgtip",
		type : "GET",
		dataType : "json",
		async:false,
		success : function(data) {
			obj =  "http://"+data["ip"];
		}
	});

	return obj;
}


function get_vlpx_ip(){
	var obj = new Object();
	$.ajax({
		url : "/vplxip",
		type : "GET",
		dataType : "json",
		async:false,
		success : function(data) {
			obj =  "http://"+data["ip"];
		}
	});

	return obj;
}

function node_show_data_log() {
	$.ajax({
		type : "get",
		url:vplxIp+ "/node/show/data",
		data : {
			tid : tid,
			ip : mgtIp
		},
		async:false,
		success : function(resource_data) {
			write_to_log(tid,'DATA','ROUTE',vplxIp,'/node/show/data',JSON.stringify(resource_data.data));
			}
		});
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
		async:false,
		success : function(write_log_result) {
		}
	});
}

function node_oprt() {
	$
			.ajax({
				url : vplxIp + "/node/show/oprt",
				type : "get",
				dataType : "json",
				data : {
					tid : tid,
					ip : mgtIp
				},
				async:false,
				success : function(status) {
					write_to_log(tid,'OPRT','ROUTE',vplxIp,'/node/show/oprt',status);
					node_show_data_log();
					 layui.use(['laydate', 'laypage', 'layer', 'table', 'carousel', 'upload', 'element', 'slider'],
							 function() {
							     var table = layui.table //表格
							     //执行一个 table 实例
							     table.render({
							         elem: '#node_test',
							         url: vplxIp+ "/node/show/data", //数据接口
							         title: '用户表'
							         ,toolbar: '#toolbarDemo',
							         cols: [[ //表头
							         {
							             type: 'checkbox',
							             fixed: 'left'
							         },
							         {
							             field: 'node',
							             title: 'node',
							             width: 100
							         },
							         {
							             field: 'node_type',
							             title: 'node_type',
							             sort: true
							         },
							         {
							             field: 'res_num',
							             title: 'res_num',
							             event: 'collapse',
							             templet: function(d) {
							                 return '<div style="position: relative;\n' + '    padding: 0 10px 0 20px;">' + d.res_num + '<i style="left: 0px;" lay-tips="展开" class="layui-icon layui-colla-icon layui-icon-right"></i></div>'
							             }
							         },
							         {
							             field: 'stp_num',
							             title: 'stp_num',
							             sort: true
							         },
							         {
							             field: 'addr',
							             title: 'addr',
							             sort: true
							         },
							         {
							             field: 'status',
							             title: 'status',
							             sort: true
							         },
							        ]]
							     });

									
								 table.on('toolbar(test)', function(obj){
									    var checkStatus = table.checkStatus(obj.config.id);
									    switch(obj.event){
									      case 'getCheckData':
//var data = checkStatus.data;
//layer.alert(JSON.stringify(data));
									    	  var that = this; 
									          // 多窗口模式，层叠置顶
									          layer.open({
									            type: 2 // 此处以iframe举例
									            ,title: 'Resource创建'
									            ,area: ['390px', '260px']
									            ,shade: 0
									            ,maxmin: true
									            ,offset: [ // 为了演示，随机坐标
									              Math.random()*($(window).height()-300)
									              ,Math.random()*($(window).width()-390)
									            ] 
									            ,content: {
									            p:222,
									            	
									            	
									            }
									            ,btn: ['关闭', '继续创建'] // 只是为了演示
									            ,yes: function(){
									            	layer.closeAll();
									            }
									            ,btn2: function(){
									            	$(that).click(); 
									            }
									            ,zIndex: layer.zIndex // 重点1
									            ,success: function(layero){
									              layer.setTop(layero); // 重点2
									            }
									          });
									      break;
//case 'getCheckLength':
//var data = checkStatus.data;
//layer.msg('选中了：'+ data.length + ' 个');
//break;
//case 'isAll':
//layer.msg(checkStatus.isAll ? '全选': '未全选');
//break;
									      
									      // 自定义头工具栏右侧图标 - 提示
									      case 'LAYTABLE_TIPS':
									        layer.alert('这是工具栏右侧自定义的一个图标按钮');
									      break;
									    };
									  });
								
							     
							     
							     
							     
							     
							     
							     
							     
							     
							     //监听工具条
							     table.on('tool(test)',
							     function(obj) {

							         var data = obj.data.res_num_son
							         //做好数据处理，下面直接放进子表中
							         
							         if (obj.event === 'collapse') {
							             var trObj = layui.$(this).parent('tr'); //当前行
							             var accordion = true //开启手风琴，那么在进行折叠操作时，始终只会展现当前展开的表格。
							             var content = '<table></table>' //内容
							             //表格行折叠方法
							             collapseTable({
							                 elem: trObj,
							                 accordion: accordion,
							                 content: content,
							                 success: function(trObjChildren, index) { //成功回调函数
							                     //trObjChildren 展开tr层DOM
							                     //index 当前层索引
							                     trObjChildren.find('table').attr("id", index);
							                     table.render({
							                         elem: "#" + index,
							                         
							                        //url:""    两种
							 						data: data,
							 						
							                         limit:10000000,
							                         cellMinWidth: 80,
							                         
							                         cols: [[{
							                             type: 'checkbox',
							                             fixed: 'left'
							                         },
							                         {
							                             field: 'res_name',
							                             title: 'res_name',
							                             sort: true
							                         },
							                         {
							                             field: 'stp_name',
							                             title: 'stp_name'
							                         },
							                         {
							                             field: 'size',
							                             title: 'size',
							                             sort: true
							                         },
							                         {
							                             field: 'device_name',
							                             title: 'device_name'
							                         },
							                         {
							                             field: 'used',
							                             title: 'used'
							                         },
							                         {
							                             field: 'status',
							                             title: 'status'
							                         },
							                        ]]
							                     });

							                 }
							             });

							         }if(obj.event === 'detail'){
									      layer.msg('查看操作');
									    } else if(obj.event === 'del'){
									    	  data_dict = obj.data
									    	  console.log(data_dict);
										      node_data =  data_dict.node
									      layer.confirm('真的删除'+ node_data+'的数据么' , function(index){
									        obj.del(); // 删除对应行（tr）的DOM结构
									        layer.close(index);
									        // 这里一般是发送修改的Ajax请求
								            // 同步更新表格和缓存对应的值
									        // 向服务端发送删除指令
									    	$.ajax({
									    		url :  vplxIp +'/node/show/delete',
									    		type : "get",
									    		dataType : "json",
									    		data : {
									    			tid : tid,
									    			node_data : node_data
									    		},
									    		async : false,
									    		success : function(delete_result) {
									    			alert(delete_result);
									    		}
									    	});
									      });
									    } else if(obj.event === 'edit'){
									      layer.msg('编辑操作');
									    } else if(obj.event === 'setSign'){
									    	var data_F = obj.data
									        layer.prompt({
									            formType: 3
									            ,title: '把[resource] 为 '+ data_F.resource +'改成如下值'
									            ,value: data_F.resource
									          }, function(value, index){
									            layer.close(index);
									            // 这里一般是发送修改的Ajax请求
									            // 同步更新表格和缓存对应的值
									        	$.ajax({
										    		url :  vplxIp +'/LINSTOR/modify',
										    		type : "get",
										    		dataType : "json",
										    		data : {
										    			tid : tid,
										    			resource_data : value
										    		},
										    		async : false,
										    		success : function(modify_result) {
										    			alert(modify_result);
										    		}
										    	});
									            obj.update({
									            resource:value
									            });
									          });
									        }
							     });

							     function collapseTable(options) {
							         var trObj = options.elem;
							         if (!trObj) return;
							         var accordion = options.accordion,
							         success = options.success,
							         content = options.content || '';
							         var tableView = trObj.parents('.layui-table-view'); //当前表格视图
							         var id = tableView.attr('lay-id'); //当前表格标识
							         var index = trObj.data('index'); //当前行索引
							         var leftTr = tableView.find('.layui-table-fixed.layui-table-fixed-l tr[data-index="' + index + '"]'); //左侧当前固定行
							         var rightTr = tableView.find('.layui-table-fixed.layui-table-fixed-r tr[data-index="' + index + '"]'); //右侧当前固定行
							         var colspan = trObj.find('td').length; //获取合并长度
							         var trObjChildren = trObj.next(); //展开行Dom
							         var indexChildren = id + '-' + index + '-children'; //展开行索引
							         var leftTrChildren = tableView.find('.layui-table-fixed.layui-table-fixed-l tr[data-index="' + indexChildren + '"]'); //左侧展开固定行
							         var rightTrChildren = tableView.find('.layui-table-fixed.layui-table-fixed-r tr[data-index="' + indexChildren + '"]'); //右侧展开固定行
							         var lw = leftTr.width() + 15; //左宽
							         var rw = rightTr.width() + 15; //右宽
							         //不存在就创建展开行
							         if (trObjChildren.data('index') != indexChildren) {
							             //装载HTML元素
							             var tr = '<tr data-index="' + indexChildren + '"><td colspan="' + colspan + '"><div style="height: auto;padding-left:' + lw + 'px;padding-right:' + rw + 'px" class="layui-table-cell">' + content + '</div></td></tr>';
							             trObjChildren = trObj.after(tr).next().hide(); //隐藏展开行
							             var fixTr = '<tr data-index="' + indexChildren + '"></tr>';//固定行
							             leftTrChildren = leftTr.after(fixTr).next().hide(); //左固定
							             rightTrChildren = rightTr.after(fixTr).next().hide(); //右固定
							         }
							         //展开|折叠箭头图标
							         trObj.find('td[lay-event="collapse"] i.layui-colla-icon').toggleClass("layui-icon-right layui-icon-down");
							         //显示|隐藏展开行
							         trObjChildren.toggle();
							         //开启手风琴折叠和折叠箭头
							         if (accordion) {
							             trObj.siblings().find('td[lay-event="collapse"] i.layui-colla-icon').removeClass("layui-icon-down").addClass("layui-icon-right");
							             trObjChildren.siblings('[data-index$="-children"]').hide(); //展开
							             rightTrChildren.siblings('[data-index$="-children"]').hide(); //左固定
							             leftTrChildren.siblings('[data-index$="-children"]').hide(); //右固定
							         }
							         success(trObjChildren, indexChildren); //回调函数
							         heightChildren = trObjChildren.height(); //展开高度固定
							         rightTrChildren.height(heightChildren + 115).toggle(); //左固定
							         leftTrChildren.height(heightChildren + 115).toggle(); //右固定
							     }

							 });

				},
				error:function () {
					write_to_log(tid,'OPRT','ROUTE',vplxIp,'/resource/show/oprt','error');

				}

			});
};
node_oprt();



layui.use(['form', 'layedit', 'laydate','element'], function(){
	  var form = layui.form
	  ,layer = layui.layer
	  ,layedit = layui.layedit
	  ,laydate = layui.laydate;
	  var $ = layui.jquery
	  ,element = layui.element;

		 
		 // 监听提交
		  form.on('submit(demo1)', function(data){
			  resource_data = JSON.stringify(data.field);
				$.ajax({
		    		url :  vplxIp +'/LINSTOR/Create',
		    		type : "get",
		    		dataType : "json",
		    		data : {
		    			tid : tid,
		    			resource_data : resource_data
		    		},
		    		async : false,
		    		success : function(delete_result) {
		    		}
		    	});
			  
		  });
});

layui.use(['form', 'layedit', 'laydate','element'], function(){
	  var form = layui.form
	  ,layer = layui.layer
	  ,layedit = layui.layedit
	  ,laydate = layui.laydate;
	  var $ = layui.jquery
	  ,element = layui.element;

		 
		 // 监听提交
		  form.on('submit(demo1)', function(data){
			  Node_data = JSON.stringify(data.field);
				$.ajax({
		    		url :  vplxIp +'/LINSTOR/Node/Create',
		    		type : "get",
		    		dataType : "json",
		    		data : {
		    			tid : tid,
		    			node : Node_data
		    		},
		    		async : false,
		    		success : function(craete_result) {
		    			console.log(craete_result);
		    			alert(craete_result["result"]);
		    		}
		    	});
			  
		  });
});


