# -*- coding: utf-8 -*-
from mgt_app import create_app
import log
import consts
app = create_app()


consts.init()
consts.glo_log()
username = 'web_user'
tid = ''
logger = log.Log(username,tid,file_name=log.WEB_LOG_NAME)
consts.set_glo_log(logger)
app = create_app()

if __name__ == '__main__':
  app.run(host='0.0.0.0',  # 任何ip都可以访问
      port=7773,  # 端口
      debug=True
      )

