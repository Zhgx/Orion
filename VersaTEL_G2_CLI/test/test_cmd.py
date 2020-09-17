import pytest
import consts
import sundry as s
import iscsi_json
import subprocess

path = '/home/samba/VersaTEL_G3_Code/VersaTEL_G2_CLI/'
log_data = consts.glo_rpldata()


@pytest.mark.iscsi_d_s
def test_get_linstor_data():
	cmd = 'linstor --no-color --no-utf8 r lv'
	cmd_result = s.execute_cmd(cmd, '123213')
	# cmd_result = subprocess.getoutput(cmd)
	assert str(log_data['get_linstor_data']) == str(cmd_result)

@pytest.mark.iscsi_d_s
def test_update_data():
	js = iscsi_json.JSON_OPERATION()
	assert log_data['update_data'] == js.get_data('Disk')

@pytest.mark.iscsi_d_s
def test_iscsi_d_s():
	cmd_output = subprocess.getoutput(f'python {path}vtel_client_main.py iscsi d s')
	assert str(log_data['cmd_output']) == str(cmd_output)