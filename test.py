import os
import json
import time
import datetime
import undetected_chromedriver as uc
from loguru import logger


data_dir = '/a_py_codes/'

logger.info('chrome 正在启动...')
opt = uc.ChromeOptions()
opt.add_argument('--no-first-run')
opt.add_argument('--no-service-autorun')
opt.add_argument('--password-store=basic')
opt.add_argument('--disable-gpu')
user_data_dir = data_dir + 'logs/' + 'chrome_test'
opt.add_argument('--user-data-dir=' + user_data_dir)
chrome = uc.Chrome(options=opt, version_main=86, user_data_dir=user_data_dir, headless=True, driver_executable_path='/usr/bin/chromedriver')
logger.info('chrome 启动成功!')

for index in range(100):

    chrome.get('https://www.google.com/')
    logger.info('chrome get url...')

    chrome.save_screenshot(data_dir+'screenshot/'+f'test_{int(time.time())}.png')
    logger.info('chrome get screenshot ...')
    time.sleep(6)



