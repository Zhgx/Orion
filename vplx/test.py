from execute import CRMConfig,CRMData


# print(CRMConfig().get_crm_res_status('asdas','iSCSITarget'))




crmdata = CRMData()
vip_all = crmdata.get_vip()
target_all = crmdata.get_target()
iscsilogicaliunit_all = crmdata.get_iscsi_logical_unit()

print(crmdata.get_target_conf(vip_all,target_all,iscsilogicaliunit_all))