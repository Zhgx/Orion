import consts
import sys
import log
import sundry

sys.path.append('../')
consts.init()

# transaction_id = s.create_transaction_id()
# logger = log.Log('test',transaction_id)
# consts.set_glo_log(logger)
# consts.set_glo_tsc_id(transaction_id)
# # consts.set_glo_id(99)
# # consts.set_glo_str('test')
# consts.set_glo_rpl('no')

transaction_id = sundry.create_transaction_id()
logger = log.Log()
logger.user = 'test'
logger.tid = transaction_id
consts.set_glo_rpl('no')
