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
        cookie = f'csrf_session_id=d7ee7cb6dd02be8dcbc16a59d8622bed; __live_version__=%221.1.1.7793%22; webcast_local_quality=null; live_use_vvc=%22false%22; bd_ticket_guard_client_web_domain=2; store-region=cn-gd; store-region-src=uid; ttwid=1%7Cew2pGD0-_59z9Q2hDGpEGZla0DwYQpmz-CRd8r7I8qo%7C1709894493%7C4384e326b20a95134bf9ed9eb679aa6d2f8d19bb079b12865e16e05b89e0b2ff; douyin.com; device_web_cpu_core=8; device_web_memory_size=8; xgplayer_device_id=75207733943; xgplayer_user_id=779808914697; xg_device_score=7.568284552297575; dy_swidth=1440; dy_sheight=900; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; passport_csrf_token=d2493f8362f4c7d54bf28282c2b563bf; passport_csrf_token_default=d2493f8362f4c7d54bf28282c2b563bf; s_v_web_id=verify_lw66uj9x_y69HTWBr_NOK0_4O0k_As0k_vZiOREH3U5SC; odin_tt=c30f2f3f8ce5a3d66818390cc2ce531dc578acc581b43601e97b9cd9d737b1b5642d163d93173928f0c69279cd5a3a2a978e9d059378f7711cc3707b169224739e58938a491b6d6b1972cc898c2bd370; download_guide=%223%2F20240514%2F0%22; pwa2=%220%7C0%7C3%7C0%22; strategyABtestKey=%221716191929.837%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.6%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; __ac_nonce=0664b1ac00069d4e6b59a; __ac_signature=_02B4Z6wo00f01M8PmbgAAIDDnfC5oKKbvQTPL50AAFWOfY3sK4syRJ51Q0cdPtRg7G3nSPInoGv7BO69RZ1JoeeHqpu4qOO2NSmHBKyJjMLQn1zeJnI7eFZxfUY4A1x-D9grQ3yY5HrKiKUAb1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCSXhkaUpMcXVPaGRHZmUxbmFGS1VmYTltMktDQ3pJcHhCdEVGSmN2MkRqOVZWR3ZiZ0haRXZGUUNQZjV3b3puWGlBVm1vM1FDTmFYZXFZMUgzKzJkNTA9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; msToken={msToken}; WallpaperGuide=%7B%22showTime%22%3A1716198086855%2C%22closeTime%22%3A0%2C%22showCount%22%3A2%2C%22cursor1%22%3A19%2C%22cursor2%22%3A0%7D; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1440%2C%5C%22screen_height%5C%22%3A900%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22'
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
        'Cookie': 'stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1440%2C%5C%22screen_height%5C%22%3A900%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; device_web_cpu_core=8; device_web_memory_size=8; architecture=amd64; ttwid=1%7Cv7inYAEhpVECT20eOy-a2_BdBfZkWBvpdEymhDIHnjs%7C1716279001%7C93a4b6196a95b8568941bdd0bb1bf93af103908ba7cb5fe16d0b9b259741fc96; douyin.com; dy_swidth=1440; dy_sheight=900; s_v_web_id=verify_lwg47ldo_LyJ99Eyh_ew4d_4rLO_8VVI_meQLZqoQGxgK; csrf_session_id=016c5a56119c97c31db3baf7c7825624; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; strategyABtestKey=%221716279012.564%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; passport_csrf_token=8c71a834616440e38e1cf0cc24160955; passport_csrf_token_default=8c71a834616440e38e1cf0cc24160955; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQ0tMeEVRZ1Z0S09Za1hNZkErZ2plamdqcDgzT3ArWnVuZXVOTWRudnVaNzFyK3pCcEJ1U3BMT0VZMVNvY05hUVhLbEdHZUtIWlAwUmFZZ2p1TUZXVFE9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; bd_ticket_guard_client_web_domain=2; home_can_add_dy_2_desktop=%221%22; download_guide=%221%2F20240521%2F0%22; pwa2=%220%7C0%7C1%7C0%22; msToken=UM6Muw4zaVmxCquQOXSnyWJrbmYtNasaSMdVGz-LI2OlmwPAaqfRIbrAo9uhD_CzT_x7Dabee7YsMIgxY5Q3M4zbCG0GdU6P7JyJG0_o91eaikZ3IrtqGUe3Het3fA==; IsDouyinActive=false',
        'Priority': 'u=1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'TE': 'trailers'
    }
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
    print(get_douyin_origin_video(aweme_id='7350291791045790991'))
