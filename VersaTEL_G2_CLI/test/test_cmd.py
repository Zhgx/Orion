import pytest
import consts
import sundry as s
import iscsi_json
import subprocess

path = '/home/samba/VersaTEL_G3_Code/VersaTEL_G2_CLI/'
log_data = consts.glo_rpldata()


# 断言
# 1. 取环境数据，执行系统命令/配置文件/JSON 的数据 还原环境，使用预处理
# 2. 如何取到这些数据？
# 3.


@pytest.mark.iscsi_d_s
def test_get_linstor_data():
	cmd = 'linstor --no-color --no-utf8 r lv'
	cmd_result = s.execute_cmd(cmd, '123213')
	# cmd_result = subprocess.getoutput(cmd)
	assert str(log_data['get_linstor_data']) == str(cmd_result)
	# 基于log记录系统命令的结果，在此环境下执行的函数/方法的结果 =》 随着代码的修改，会发生改变
	# log数据 =》 不会发生改变


@pytest.mark.iscsi_d_s
def test_update_data():
	js = iscsi_json.JSON_OPERATION()
	assert log_data['update_data'] == js.get_data('Disk')

@pytest.mark.iscsi_d_s
def test_iscsi_d_s():
	cmd_output = subprocess.getoutput(f'python {path}vtel_client_main.py iscsi d s')
	assert str(log_data['cmd_output']) == str(cmd_output)