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
import urllib.parse
from fake_useragent import UserAgent
import douyin_a_bogus
import a_lxml_create_html
import re
from credentials import load_douyin_cookie


def generate_request_params(url, user_agent, cookie_str):
    query = urllib.parse.urlparse(url).query
    logger.info(f'query: {query}')

    # xbogus = execjs.compile(open('douyin_x-bogus.js').read()).call('sign', query, user_agent)
    # new_url = url + "&X-Bogus=" + xbogus

    abogus = douyin_a_bogus.get_ab(target_url=query, user_agent=user_agent, cookie_str=cookie_str)
    logger.info(f'abogus: {abogus}')
    if abogus is False:
        logger.info(f'获取 abogus 失败!!')
        raise Exception(f'获取 abogus 失败!!')
    new_url = url + "&a_bogus=" + abogus
    response_data = {
        "param": new_url,
        "a-bogus": abogus
    }
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
        agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        msToken = generate_random_str()
        # Cookie values are loaded from the local file or environment.
        cookie = load_douyin_cookie()
        url_with_bogus = generate_request_params(url=f'https://www.douyin.com/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={aweme_id}&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=124.0.0.0&browser_online=true&engine_name=Blink&engine_version=124.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7319780293514495522&verifyFp=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC&fp=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC&msToken={msToken}', user_agent=agent, cookie_str=cookie)["param"]
    except:
        logger.error(f'douyin aweme_id: {aweme_id} 获取 参数失败!!')
        return False
    logger.info(f'douyin aweme_id: {aweme_id} 获取 参数成功!')
    for index in range(2):
        try:
            headers = {
                'User-Agent': agent,
                'Referer': f'https://www.douyin.com/video/{aweme_id}?modeFrom=',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': cookie,
                'priority': 'u=1, i'
            }
            res = requests.get(url=url_with_bogus, headers=headers, timeout=10)
            print(f'状态码: {res.status_code}')
            res = res.json()['aweme_detail']
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
                logger.info(f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['play_addr_h264']['url_list'][0]}")
                temp["originVideo"] = res['video']['play_addr_h264']['url_list'][0]
                temp["normalVideo"] = res['video']['play_addr_h264']['url_list'][0]
                return temp

            elif 'video' in res.keys() and res['video']['bit_rate'][0]['play_addr']['url_list']:
                logger.info(f"douyin aweme_id: {aweme_id} 找到原始视频: {res['video']['bit_rate'][0]['play_addr']['url_list'][0]}")
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
    
 
def get_douyin_video_detail(aweme_id):
    agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0'
    for index in range(100):
        agent = UserAgent().chrome
        if 'Android' in agent or 'android' in agent:
            continue
        else:
            break
    url = f'https://www.douyin.com/discover?modal_id={aweme_id}'
    headers = {
        'User-Agent': agent,
        'Accept': 'application/json',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Connection': 'keep-alive',
        'Priority': 'u=1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
    }
    headers['Cookie'] = load_douyin_cookie()
    res_html = None
    for index in range(2):
        try:
            res = requests.get(url=url, headers=headers, timeout=3)
            if res.status_code == 200:
                res_html = a_lxml_create_html.create_root_node(res.text)
                xpath_ = """//script[contains(text(), '"desc')]/text()"""
                res_html = res_html.xpath(xpath_)[0]
                break
            else:
                logger.info(f'响应异常 状态码: {res.status_code} ')
                continue
        except:
            logger.info(f'请求异常: {traceback.format_exc()} res: {res}')
            continue
    if res_html is None:
        return False

    try:
        desc = re.search(r'\\"desc\\":\\"(.+?)\\"', res_html)
        if desc:
            desc = desc.group(1).replace('\\n', ' ').replace('\n', ' ').replace('\\t', ' ').replace('\t', ' ').replace('\\r', ' ').replace('\r', ' ').replace('\\', '')

        video_info = re.search(r'\\"playAddr\\":\[(.+?)\]', res_html)
        if video_info:
            video_url = re.search(r'\\"src\\":\\"(.+?)\\"', video_info.group(1)).group(1).replace('\\u0026', '&')
            if video_url.startswith('https:'):
                pass
            else:
                video_url = 'https:' + video_url
        else:
            video_url = None

        imageUrl = re.search(r'\\"originCover\\":\\"(.+?)\\"', res_html)
        if imageUrl:
            imageUrl = imageUrl.group(1).replace('\\u0026', '&')
            if imageUrl.startswith('https:'):
                pass
            else:
                imageUrl = 'https:' + imageUrl

        likes = re.search(r'\\"diggCount\\":(\d+),', res_html)
        if likes:
            likes = int(likes.group(1))

        collectNum = re.search(r'\\"collectCount\\":(\d+),', res_html)
        if collectNum:
            collectNum = int(collectNum.group(1))

        commentNum = re.search(r'\\"commentCount\\":(\d+),', res_html)
        if commentNum:
            commentNum = int(commentNum.group(1))

        publishTime = re.search(r'\\"createTime\\":(\d+),', res_html)
        if publishTime:
            publishTime = int(publishTime.group(1))

        temp = {
            "itemId": aweme_id,
            "platform": "douyin",
            "itemUrl": url,
            "title": desc,
            "descDetail": desc,
            "originVideo": video_url,
            "normalVideo": video_url,
            "audio": None,
            'imageUrl': imageUrl,
            'likes': likes,
            'collectNum': collectNum,
            'commentNum': commentNum,
            'lastUpdateTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(publishTime)),
            'publishTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(publishTime)),

            'crawlTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'createTime': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.info(f'aweme_id: {aweme_id} video_info: {temp}')
        return temp

    except:
        logger.error(f'解析异常: {traceback.format_exc()}')
        return False


if __name__ == '__main__':
    # print(generate_random_str())
    # print(generate_request_params(url='https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=7344748942900333824&aid=1128&version_name=23.5.0&device_platform=android&os_version=2333',
    #                               user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'))
    print(get_douyin_origin_video(aweme_id='7367231723253370139'))
