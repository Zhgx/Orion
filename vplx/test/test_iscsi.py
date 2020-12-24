from execute import iscsi
import subprocess


class TestDisk:

    def setup_class(self):
        subprocess.run('python3 vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi d s', shell=True)
        self.disk = iscsi.Disk()

    def teardown_class(self):
        subprocess.run('python3 vtel_client_main.py stor r d res_test -y', shell=True)

    # 有可能返回 {} ，不能直接使用assert
    def test_get_all_disk(self):
        assert not self.disk.get_all_disk()

    # 这个函数应该明确获得指定disk,如果没有获得指定disk则return None
    def test_get_spe_disk(self):
        assert self.disk.get_spe_disk('res_test')

    # 该函数没有返回值，调用了本模块get_all_disk()和sundry的show_iscsi_data()
    def test_show_all_disk(self):
        assert self.disk.show_all_disk() is None

    # 该函数没有返回值，调用了本模块get_spe_disk()和sundry的show_iscsi_data()
    def test_show_spe_disk(self):
        assert self.disk.show_spe_disk('res_test') is None


class TestHost:

    def setup_class(self):
        self.host = iscsi.Host()

    # 已存在返回 None ，新建成功返回 True
    def test_create_host(self):
        # 存在

        # 新建成功
        assert self.host.create_host('test_host1', 'iqn.2020-04.feixitek.com:pytest01')

    # 返回所有host，如果host为空，返回{},否则返回host字典
    def test_get_all_host(self):
        # host 为空
        assert self.host.get_all_host() == {}
        # host 不为空
        assert self.host.get_all_host()

    # 已存在返回该host ，不存在返回None
    def test_get_spe_host(self):
        assert self.host.get_spe_host('test_host1')
        # 新增测试用例
        assert not self.host.get_spe_host('test_host2')

    # 该函数没有返回值，调用了本模块get_all_host()和sundry的show_iscsi_data()
    def test_show_all_host(self):
        assert not self.host.show_all_host()

    # 该函数没有返回值，调用了本模块get_spe_host()和sundry的show_iscsi_data()
    def test_show_spe_host(self):
        assert not self.host.show_spe_host('test_host1')

    # 1.先检查host 是否存在，不存在返回 None 2.再判断该host 是否已经配置在HostGroup里，已配置返回None 3.不满足前两个返回条件，删除后返回True
    def test_delete_host(self):
        # 新增不存在用例
        assert self.host.delete_host('test_host2') is None
        # 已配置用例有待添加

        # 删除已存在而且没有配置在HostGroup中的host
        assert self.host.delete_host('test_host1')

    def test_modify_host(self):
        pass


class TestDiskGroup:

    def setup_class(self):
        subprocess.run('python3 vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi d s', shell=True)
        self.diskg = iscsi.DiskGroup()

    def teardown_class(self):
        subprocess.run('python vtel_client_main.py stor r d res_test -y', shell=True)

    # 1.判断 DiskGroup 是否存在，存在返回 None 2.遍历 disk 列表，若发现 disk 不存在返回 None 3.创建成功返回 True
    def test_create_diskgroup(self):
        # 已存在DiskGroup测试用例

        # 提供的disk列表中有不存在的disk测试用例

        # 创建成功的测试用例
        assert self.diskg.create_diskgroup('test_dg1', ['res_test'])

    # 返回所有 DiskGroup，如果为 DiskGroup 空，返回{},否则返回 DiskGroup 非空字典
    def test_get_all_diskgroup(self):
        # DiskGroup 为空
        assert self.diskg.get_all_diskgroup() == {}
        # DiskGroup 不为空
        assert not self.diskg.get_all_diskgroup()

    # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    def test_get_spe_diskgroup(self):
        # DiskGroup 不存在测试用例
        assert not self.diskg.get_spe_diskgroup('test_dg2')
        # DiskGroup 存在测试用例
        assert self.diskg.get_spe_diskgroup('test_dg1')

    # 该函数没有返回值，调用了本模块get_all_diskgroup()和sundry的show_iscsi_data()
    def test_show_all_diskgroup(self):
        assert self.diskg.show_all_diskgroup() is None

    # 该函数没有返回值，调用了本模块get_spe_diskgroup()和sundry的show_iscsi_data()
    def test_show_spe_diskgroup(self):
        assert self.diskg.show_spe_diskgroup('test_dg1') is None

    # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # 这个方法无返回值
    def test_delete_diskgroup(self):
        assert self.diskg.delete_diskgroup('test_dg1') is None


class TestHostGroup:

    def setup_class(self):
        self.host = iscsi.Host()
        self.host.create_host('test_host1', 'iqn.2020-04.feixitek.com:pytest01')
        self.hostg = iscsi.HostGroup()

    def teardown_class(self):
        self.host.delete_host('test_host1')

    # 1.判断 HostGroup 是否存在，存在返回 None 2.遍历 Host 列表，若发现 Host 不存在返回 None 3.创建成功返回 True
    def test_create_hostgroup(self):
        # 已存在 HostGroup 测试用例

        # 提供的 host 列表中有不存在的 host 测试用例

        # 创建成功的测试用例
        assert self.hostg.create_hostgroup('test_hg1', ['test_host1'])

    # 返回所有 HostGroup，如果为 HostGroup 空，返回{},否则返回 HostGroup 非空字典
    def test_get_all_hostgroup(self):
        # HostGroup 为空
        assert self.hostg.get_all_hostgroup() == {}
        # HostGroup 不为空
        assert not self.hostg.get_all_hostgroup()

    # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    def test_get_spe_hostgroup(self):
        # DiskGroup 不存在
        assert not self.hostg.get_spe_hostgroup('test_hg2')
        # DiskGroup 存在
        assert self.hostg.get_spe_hostgroup('test_hg1')

    # 该函数没有返回值，调用了本模块get_all_hostgroup()和sundry的show_iscsi_data()
    def test_show_all_hostgroup(self):
        assert self.hostg.show_all_hostgroup() is None

    # 该函数没有返回值，调用了本模块get_sep_hostgroup()和sundry的show_iscsi_data()
    def test_show_spe_hostgroup(self):
        assert self.hostg.show_spe_hostgroup('test_hg1') is None

    # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # 这个方法无返回值
    def test_delete_hostgroup(self):
        assert self.hostg.delete_hostgroup('test_hg1') is None


class TestMap:

    def setup_class(self):
        subprocess.run('python3 vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi d s', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest01', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi hg c test_hg test_host', shell=True)
        self.map = iscsi.Map()

    def teardown_class(self):
        subprocess.run('python3 vtel_client_main.py iscsi hg d test_hg', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi h d test_host', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi dg d test_dg', shell=True)
        subprocess.run('python3 vtel_client_main.py stor r d res_test -y', shell=True)

    # 1.map 是否存在/hostgroup是否存在/diskgroup是否存在
    def test_pre_check_create_map(self):
        # map 已存在

        # hostgroup 不存在
        assert self.map.pre_check_create_map('test_map', 'test_hg1', 'test_dg') is None
        # diskgroup 不存在
        assert self.map.pre_check_create_map('test_map', 'test_hg', 'test_dg1') is None
        # 同时满足三个条件
        assert self.map.pre_check_create_map('test_map', 'test_hg', 'test_dg')

    # 根据hg去获取hostiqn，返回由hostiqn组成的initiator
    def test_get_initiator(self):
        # hg 不存在
        # hg 存在
        assert self.map.get_initiator('test_hg') == 'iqn.2020-04.feixitek.com:pytest01'

    def test_get_target(self):
        # 检测该函数有返回值
        assert self.map.get_target() is not None

    # 使用 linstro 命令,有可能返回{}或非空字典
    def test_get_disk_data(self):
        assert self.map.get_disk_data('test_dg') is not None

    # 先调用pre_check_create_map()，这个函数已经在前面测试了
    # Q：已经被使用过的disk(ilu) 没有做处理？
    def test_create_map(self):
        assert self.map.create_map('test_map', 'test_hg', 'test_dg')

    # 获取 map 并返回，map 为空返回 {},不为空返回非空字典
    def test_get_all_map(self):
        # map 为空
        assert self.map.get_all_map() == {}
        # map 不为空
        assert self.map.get_all_map()

    # map 是否存在，存在返回非空列表[{map: map_data}, list_hg, list_dg],不存在返回 None
    def test_get_spe_map(self):
        # 不存在
        assert self.map.get_spe_map('test_map1') is None
        # 存在（需检测 map 结构内容？？？）
        assert self.map.get_spe_map('test_map')

    # 该函数没有返回值，调用了本模块get_all_map()和sundry的show_iscsi_data()
    def test_show_all_map(self):
        # ？？
        assert self.map.show_all_map() is None

    def test_show_spe_map(self):
        # 重新定义一个 map 实例对象？
        map = iscsi.Map()
        assert map.show_spe_map('test_map') is not None

    # 1.map 存在返回 True，不存在返回 None
    def test_pre_check_delete_map(self):
        # 不存在
        assert self.map.pre_check_delete_map('test_map1')
        # 存在
        assert self.map.pre_check_delete_map('test_map')

    # 1.使用pre_check_delete_map检查，map 不存在返回 None，删除成功返回 True
    def test_delete_map(self):
        map = iscsi.Map()
        # 不存在
        assert map.delete_map('test_map1')
        # 删除成功
        assert map.delete_map('test_map')
