import consts
import sys
import log
import sundry
from replay import Replay

sys.path.append('../')
consts.init()


<<<<<<< HEAD
# transaction_id = sundry.create_transaction_id()
logger = log.Log()
logger.user = 'test'
# logger.tid = transaction_id
consts.set_glo_rpl('no')
=======
transaction_id = log.create_transaction_id()
logger = log.Log()
logger.user = 'test'
logger.tid = transaction_id
>>>>>>> b78e6cb5f618d5ddec071cdb27972707d55b5a74
