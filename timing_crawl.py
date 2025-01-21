import time
from crawlers import Crawlers
import configparser


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
crawlers_config = config['Crawlers']
keywords_english = crawlers_config['Keywords_english']
keywords_chinese = crawlers_config['Keywords_chinese']


crawler = Crawlers()
for keyword in keywords_english.split(','):
    try:
        print(f'keyword: {keyword}')
        if crawlers_config['Tiktok_crawler'] == 'True' or crawlers_config['Tiktok_crawler'] is True:
            print(f'开启tiktok爬虫...')
            try:
                crawler.tiktok_crawler(keyword)
            except:
                pass
        if crawlers_config['Youtube_crawler'] == 'True' or crawlers_config['Youtube_crawler'] is True:
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
        print(f'keyword: {keyword}')
        if crawlers_config['Douyin_crawler'] == 'True' or crawlers_config['Douyin_crawler'] is True:
            print(f'开启douyin爬虫...')
            crawler.douyin_crawler(keyword)
        time.sleep(10)
    except Exception as e:
        print(f'error: {e}')
        continue
