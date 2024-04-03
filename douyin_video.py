# -*- coding: utf-8 -*-
# @Author  : dongdonglongbbb@gmail.com
# @Time    : 2024/3/19 12:01
# @Desc    :
import random
import traceback
import requests
import time
import datetime
from loguru import logger
import execjs
import urllib.parse
from fake_useragent import UserAgent

test_ttwid_url = 'https://v.douyin.com/iFQ87sqD/'


def generate_request_params(url, user_agent):
    query = urllib.parse.urlparse(url).query
    print(f'query: {query}')
    xbogus = execjs.compile(open('douyin_x-bogus.js').read()).call('sign', query, user_agent)
    new_url = url + "&X-Bogus=" + xbogus
    response_data = {
        "param": new_url,
        "X-Bogus": xbogus
    }
    logger.info(f'param: {response_data}')
    return response_data


def generate_random_str(randomlength=107):
    """
    抖音 msToken 参数
    根据传入长度产生随机字符串
    """
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789='
    length = len(base_str) - 1
    for _ in range(randomlength):
        random_str += base_str[random.randint(0, length)]
    return random_str


def get_douyin_origin_video(aweme_id):
    try:
        agent = UserAgent().chrome
        msToken = generate_random_str()
        url_with_bogus = generate_request_params(
            url=f'https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id={aweme_id}&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333',
            user_agent=agent)["param"]
        ttwid_ = get_ttwid()
        if ttwid_:
            ttwid = ttwid_
        else:
            ttwid = '1%7CWBuxH_bhbuTENNtACXoesI5QHV2Dt9-vkMGVHSRRbgY%7C1677118712%7C1d87ba1ea2cdf05d80204aea2e1036451dae638e7765b8a4d59d87fa05dd39ff'
    except:
        logger.error(f'douyin aweme_id: {aweme_id} 获取 参数失败!!')
        return False
    logger.info(f'douyin aweme_id: {aweme_id} 获取 参数成功!')
    for index in range(2):
        try:
            headers = {
                'User-Agent': agent,
                'Referer': 'https://www.douyin.com/',
                'Host': 'www.douyin.com',
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Cookie': f'msToken={msToken};odin_tt=324fb4ea4a89c0c05827e18a1ed9cf9bf8a17f7705fcc793fec935b637867e2a5a9b8168c885554d029919117a18ba69; ttwid={ttwid}; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWNsaWVudC1jc3IiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFIFJFUVVFU1QtLS0tLVxyXG5NSUlCRFRDQnRRSUJBREFuTVFzd0NRWURWUVFHRXdKRFRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxXHJcbllYSmtNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVKUDZzbjNLRlFBNUROSEcyK2F4bXAwNG5cclxud1hBSTZDU1IyZW1sVUE5QTZ4aGQzbVlPUlI4NVRLZ2tXd1FJSmp3Nyszdnc0Z2NNRG5iOTRoS3MvSjFJc3FBc1xyXG5NQ29HQ1NxR1NJYjNEUUVKRGpFZE1Cc3dHUVlEVlIwUkJCSXdFSUlPZDNkM0xtUnZkWGxwYmk1amIyMHdDZ1lJXHJcbktvWkl6ajBFQXdJRFJ3QXdSQUlnVmJkWTI0c0RYS0c0S2h3WlBmOHpxVDRBU0ROamNUb2FFRi9MQnd2QS8xSUNcclxuSURiVmZCUk1PQVB5cWJkcytld1QwSDZqdDg1czZZTVNVZEo5Z2dmOWlmeTBcclxuLS0tLS1FTkQgQ0VSVElGSUNBVEUgUkVRVUVTVC0tLS0tXHJcbiJ9'
            }
            res = requests.get(url=url_with_bogus, headers=headers, timeout=10).json()['aweme_detail']
            temp = {
                "itemId": aweme_id,
                "platform": "douyin",
                "itemUrl": f'https://www.douyin.com/video/{aweme_id}?modeFrom=',
                "title": res['caption'],
                "descDetail": res['desc'],
                "originVideo": None,
                "normalVideo": None,
                "audio": None,
                'imageUrl': res['video']['cover']['url_list'][0],
                'likes': res['statistics']['digg_count'],
                'collectNum': res['statistics']['collect_count'],
                'commentNum': res['statistics']['comment_count'],
                'lastUpdateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(res['create_time'])),
                'publishTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(res['create_time'])),

                'crawlTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'createTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if 'play_addr' in res['video'].keys() and len(res['video']['play_addr']['url_list']) > 0:
                logger.info(f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['play_addr']['url_list'][0]}")
                temp["originVideo"] = res['video']['play_addr']['url_list'][0]
                temp["normalVideo"] = res['video']['play_addr']['url_list'][0]
                return temp

            elif 'play_addr_265' in res['video'].keys() and len(res['video']['play_addr_265']['url_list']) > 0:
                logger.info(f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['play_addr_265']['url_list'][0]}")
                temp["originVideo"] = res['video']['play_addr_265']['url_list'][0]
                temp["normalVideo"] = res['video']['play_addr_265']['url_list'][0]
                return temp

            elif 'play_addr_h264' in res['video'].keys() and len(res['video']['play_addr_h264']['url_list']) > 0:
                logger.info(
                    f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['play_addr_h264']['url_list'][0]}")
                temp["originVideo"] = res['video']['play_addr_h264']['url_list'][0]
                temp["normalVideo"] = res['video']['play_addr_h264']['url_list'][0]
                return temp

            elif 'video' in res.keys() and res['video']['bit_rate'][0]['play_addr']['url_list']:
                logger.info(
                    f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['bit_rate'][0]['play_addr']['url_list'][0]}")
                temp["originVideo"] = res['video']['bit_rate'][0]['play_addr']['url_list']
                temp["normalVideo"] = res['video']['bit_rate'][0]['play_addr']['url_list']
                return temp
            else:
                logger.info(f'url: {url_with_bogus} 未能找到 原始视频 开始重试...')
                continue
        except:
            logger.error(f'url: {url_with_bogus} 请求异常开始重试... error: {traceback.format_exc()}')
            continue
    return False


def get_ttwid():
    session = requests.session()
    agent = UserAgent().chrome
    headers = {
        'User-Agent': agent,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'authority': 'v.douyin.com'
    }
    ttwid = None
    url = test_ttwid_url
    for index in range(3):
        try:
            logger.info(f'开始请求: {url}')
            res = session.get(url=url, headers=headers, allow_redirects=False)
            if res.status_code in [302, 301]:
                url = res.headers.get('Location')
                cookies_dict = session.cookies.get_dict()
                if cookies_dict and 'ttwid' in cookies_dict.keys():
                    ttwid = cookies_dict['ttwid']
                    logger.info(f'获取到 ttwid: {ttwid}')
                    return ttwid
            continue
        except:
            continue
    return ttwid


if __name__ == '__main__':
    # print(generate_random_str())
    # print(generate_request_params(url='https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=7344748942900333824&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333',
    #                               user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'))
    print(get_douyin_origin_video(aweme_id='7156904930987478307'))
    # get_ttwid()