import random
import sys
import time
import os
from crawlers import Crawlers
import configparser


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
crawlers_config = config['Crawlers']
keywords_english = crawlers_config['Keywords_english']
keywords_chinese = crawlers_config['Keywords_chinese']


def kill_orphan_chrome():
    num = 1
    while True:
        if sys.argv[1] == 'test':
            break
        else:
            try:
                if os.popen('ps -f --ppid 1 | grep chromedriver').read():
                    os.system("ps -f --ppid 1 | grep chromedriver | awk '{print $2}' | xargs kill -9")
            except:
                pass
            try:
                if os.popen('ps -f --ppid 1 | grep chrome').read():
                    os.system("ps -f --ppid 1 | grep chrome | awk '{print $2}' | xargs kill -9")
            except:
                pass
        time.sleep(random.uniform(0.1, 0.2))
        if num > 3:
            break


crawler = Crawlers()
for keyword in keywords_english.split(','):
    try:
        kill_orphan_chrome()
        print(f'keyword: {keyword}')
        if crawlers_config['Tiktok_crawler'] == 'True':
            print(f'开启tiktok爬虫...')
            try:
                crawler.tiktok_crawler(keyword)
            except:
                pass
        if keyword == 'funny' or keyword == 'hot':
            if crawlers_config['Youtube_crawler'] == 'True':
                print(f'开启youtube爬虫...')
                try:
                    crawler.youtube_crawler(keyword)
                except:
                    pass
        time.sleep(2)
    except:
        continue
for keyword in keywords_chinese.split(','):
    try:
        kill_orphan_chrome()
        print(f'keyword: {keyword}')
        if crawlers_config['Douyin_crawler'] == 'True':
            print(f'开启douyin爬虫...')
            crawler.douyin_crawler(keyword)
        time.sleep(3)
    except Exception as e:
        print(f'error: {e}')
        continue
