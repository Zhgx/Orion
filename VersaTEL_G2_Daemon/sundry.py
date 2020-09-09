import time
from random import shuffle


def create_transaction_id():
    return int(time.time())

def create_oprt_id():
    time_stamp = str(create_transaction_id())
    str_list = list(time_stamp)
    shuffle(str_list)
    return ''.join(str_list)