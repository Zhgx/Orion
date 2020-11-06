from execute import lvm

class TestLVM:

    def setup_class(self):
        self.l = lvm.LVM()

    def test_get_vg(self):
        assert 'VG' in self.l.get_vg()

    def test_get_thinlv(self):
        assert 'LV' in self.l.get_thinlv()

    def test_refine_thinlv(self):
        assert self.l.refine_thinlv() != None

    def test_refine_vg(self):
        assert self.l.refine_vg() != None

    def test_is_vg_exists(self):
        assert self.l.is_vg_exists('drbdpool') == True

    def test_is_thinlv_exists(self):
        assert self.l.is_thinlv_exists('drbdpool/thinlv_test') == True