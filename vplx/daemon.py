# -*- coding: utf-8 -*-
from flask_vplx import app
import consts
import sundry
import log

consts.init()
consts.glo_log()
username = sundry.get_username() 
tid = ''
logger = log.Log(username,tid,file_name=log.WEB_LOG_NAME)
consts.set_glo_log(logger)


if __name__ == '__main__':
  app.run(host='0.0.0.0',  # 任何ip都可以访问
      port=7777,  # 端口
      debug=True
      )

