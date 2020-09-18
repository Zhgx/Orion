import pytest
import consts
import sundry as s
import iscsi_json
import subprocess
from execute import iscsi,linstor
import logdb

path = '/home/samba/VersaTEL_G3_Code/VersaTEL_G2_CLI/'
log_data = consts.glo_rpldata()
db = consts.glo_db()
transaction_id = consts.glo_tsc_id()

# 断言
# 1. 取环境数据，执行系统命令/配置文件/JSON 的数据 还原环境，使用预处理
# 2. 如何取到这些数据？
# 3.	# 基于log记录系统命令的结果，在此环境下执行的函数/方法的结果 =》 随着代码的修改，会发生改变
# 	# log数据 =》 不会发生改变


@pytest.mark.iscsi_d_s
def test_get_linstor_data():
	cmd = 'linstor --no-color --no-utf8 r lv'
	linstor_obj = linstor.Linstor()
	cmd_result = linstor_obj.get_linstor_data(cmd)
	result = db.get_refine_linstor_data(transaction_id)
	assert cmd_result == result



@pytest.mark.iscsi_d_s
def test_get_all_disk(): # 存疑,是否真正插入到json文件中没有测试出来，可能需要另外编写一个用例测试是否插入了
	disk = iscsi.Disk()
	result1 = disk.get_all_disk()
	id_dict = db.get_id(transaction_id, 'update_data')
	result2 = db.get_oprt_result(id_dict['oprt_id'])['result']
	assert result1 == eval(result2)


@pytest.mark.iscsi_d_s
def test_show_iscsi_data():
	list_header = ["ResourceName", "Path"]
	disk = iscsi.Disk()
	dict_data = disk.get_all_disk()
	table = s.show_iscsi_data(list_header, dict_data)
	assert '| ResourceName |      Path     |'in str(table)
