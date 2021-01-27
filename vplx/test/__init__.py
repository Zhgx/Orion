import consts
import sys
import log
import sundry
from replay import Replay

sys.path.append('../')
consts.init()


transaction_id = log.create_transaction_id()
logger = log.Log()
logger.user = 'test'
logger.tid = transaction_id
