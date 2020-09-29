from execute import iscsi


class TestDisk:

    def setup_class(self):
        self.disk = iscsi.Disk()

    def test_get_all_disk(self):
        assert self.disk.get_all_disk() == None

    def test_get_spe_disk(self):
        assert self.disk.get_spe_disk('res_a') == None

    def test_show_all_disk(self):
        assert self.disk.show_all_disk() == None

    def test_show_spe_disk(self):
        assert self.disk.show_spe_disk('res_a') == None


class TestHost:

    def setup_class(self):
        self.host = iscsi.Host()

    def test_create_host(self):
        assert self.host.create_host() == None

    def test_get_all_host(self):
        assert self.host.get_all_host() == None

    def test_get_spe_host(self):
        assert self.host.get_spe_host() == None

    def test_show_all_host(self):
        assert self.host.show_all_host() == None

    def test_show_spe_host(self):
        assert self.host.show_spe_host() == None

    def test_delete_host(self):
        assert self.host.delete_host() == None
