try:
    import configparser as cp
except Exception:
    import ConfigParser as cp


name_of_config_file = 'config.ini'


def read_config_file():
    obj_cfg = cp.ConfigParser(allow_no_value=True)
    obj_cfg.read(name_of_config_file)
    return obj_cfg



class Config():

    def __init__(self):
        self.cfg = read_config_file()

    def get_ip(self):
        return self.cfg.get('VPLX','IP')

    def get_port(self):
        return self.cfg.get('VPLX', 'PORT')


if __name__ == '__main__':
    pass