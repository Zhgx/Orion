from execute import crm


def test_execute_crm_cmd():
    assert crm.execute_crm_cmd('pwd') != None

class TestCRMData:

    def setup_class(self):
        self.crmdata = crm.CRMData()

    def test_get_crm_conf(self):
        pass