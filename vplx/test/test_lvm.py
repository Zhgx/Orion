from execute import lvm

class TestLVM:

    def setup_class(self):
        self.l = lvm.LVM()

    # vg /throw exception
    def test_get_vg(self):
        assert 'VG' in self.l.get_vg()

    # None/thinlv
    def test_get_thinlv(self):
        assert 'LV' in self.l.get_thinlv()

    # []/list_thinlv
    def test_refine_thinlv(self):
        assert self.l.refine_thinlv() is not None

    # list_vg/[]
    def test_refine_vg(self):
        assert self.l.refine_vg()  is not None

    # True / None
    def test_is_vg_exists(self):
        # 不存在
        assert self.l.is_vg_exists('drbdpool2') is None
        # 存在
        assert self.l.is_vg_exists('drbdpool')

    # True / None
    def test_is_thinlv_exists(self):
        # 不存在
        assert self.l.is_thinlv_exists('drbdpool2/thinlv_test') is None
        # 存在
        assert self.l.is_thinlv_exists('drbdpool/thinlv_test')