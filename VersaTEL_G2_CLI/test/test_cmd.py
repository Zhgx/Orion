import pytest
import consts
import sundry as s
import iscsi_json
import subprocess
import linstor
from execute import iscsi

path = '/home/samba/VersaTEL_G3_Code/VersaTEL_G2_CLI/'
log_data = consts.glo_rpldata()


# 断言
# 1. 取环境数据，执行系统命令/配置文件/JSON 的数据 还原环境，使用预处理
# 2. 如何取到这些数据？
# 3.


@pytest.mark.iscsi_d_s
def test_get_linstor_data():
	cmd = 'linstor --no-color --no-utf8 r lv'
	cmd_result = linstor.get_linstor_data(cmd)
	assert str(cmd_result)
	# 基于log记录系统命令的结果，在此环境下执行的函数/方法的结果 =》 随着代码的修改，会发生改变
	# log数据 =》 不会发生改变


@pytest.mark.iscsi_d_s
def test_get_all_disk():
	disk = iscsi.Disk()
	result = disk.get_all_disk()
	# js = iscsi_json.JSON_OPERATION()
	# js.update_data()
	# assert js.get_data('Disk')
    assert result ==


@pytest.mark.iscsi_d_s
def test_show_iscsi_data():
	list_header = ["ResourceName", "Path"]
	table = s.show_iscsi_data(list_header, dict_data)
	assert table


@pytest.mark.iscsi_d_s_
def test_show_spe_disk():
