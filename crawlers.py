import json
import time
import datetime
import requests
import random
from selenium import webdriver
import sys
from pymongo import MongoClient
import re
import threadpool
from urllib.parse import quote
import configparser
import os
import undetected_chromedriver as uc

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
crawlers_config = config['Crawlers']
path_config = config['Path']
# 请求时最大线程数
MAX_THREAD = int(crawlers_config['Max_thread'])
# tiktok douyin 关键字搜索视频结果分页,最多为3
MAX_PAGE = int(crawlers_config['Max_page'])


class Crawlers(object):
    def __init__(self):
        print(f'初始化爬虫...')
        self.tiktok_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
        self.tiktok_api_headers = {
            'user-agent': 'com.ss.android.ugc.trill/2613 (Linux; U; Android 10; en_US; Pixel 4; Build/QQ3A.200805.001; Cronet/58.0.2991.0)'}
        if sys.argv[1] == 'test':
            client = MongoClient(host=path_config['Mongo_host_local'], port=int(path_config['Mongo_port']))
        else:
            client = MongoClient(host=path_config['Mongo_host_server'], port=int(path_config['Mongo_port']))
        self.db = client['handling_vedio']
        self.collection = self.db['vedios']
        self.info = {'video_id': None, 'video_title': None, 'video_url': None, 'audio_url': None,
                     'update_timestamp': None}
        self.youtube_results = []
        self.tiktok_results = []
        self.douyin_results = []
        self.arg = sys.argv[1]
        if crawlers_config['Proxy_switch'] == 'False':
            self.proxy = None
        elif crawlers_config['Use_socks5_proxy'] == 'True':
            self.proxy = {"http": crawlers_config['Socks5_proxy'], "https": crawlers_config['Socks5_proxy']}
        elif crawlers_config['Use_simple_proxy'] == 'True':
            self.proxy = {"http": 'http://' + crawlers_config['Socks5_proxy'],
                          "https": 'https://' + crawlers_config['Socks5_proxy']}
        else:
            self.proxy = None

    def update_tiktok_cookies(self):
        print('chrome 正在启动', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        opt = uc.ChromeOptions()
        opt.add_argument('--no-first-run')
        opt.add_argument('--no-service-autorun')
        opt.add_argument('--password-store=basic')
        opt.add_argument('--lang=en-US')
        opt.add_argument('--mute-audio')
        opt.add_argument('--disable-gpu')
        opt.add_argument('--headless')
        _browser = uc.Chrome(options=opt, version_main=int(path_config['chrome_version']))
        print('chrome 启动成功', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        _browser.implicitly_wait(10)
        _browser.get('https://www.tiktok.com/foryou?is_copy_url=1&is_from_webapp=v1')
        time.sleep(random.uniform(2, 3))
        cookies = _browser.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        if len(cookies) > 0:
            try:
                _browser.quit()
                with open('tiktok_cookies.json', 'w') as f:
                    f.write(json.dumps(cookies))
            except:
                pass
            return cookies
        else:
            try:
                _browser.quit()
            except:
                pass
            return None

    def tiktok_crawler(self, search_keywords):
        self.tiktok_results = []
        # 先关键词搜索视频
        video_list = []
        for i in range(MAX_PAGE):
            temp, has_more = self.tiktok_search_video(search_keywords, offset=12 * i)
            if has_more == 1:
                for one in temp:
                    video_list.append(one)
            else:
                for one in temp:
                    video_list.append(one)
                break
        new_video_list = []
        for video in video_list:
            video_id = video['video_id']
            if self.collection.find_one({'video_id': video_id}) is None or (
                    time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 5 * 60 * 60):
                new_video_list.append(video)
            else:
                continue
        print(f'tiktok需要更新视频数量: {len(new_video_list)}')
        if new_video_list:
            params = [(None, {'video_id': video['video_id']}) for video in new_video_list]
            pool = threadpool.ThreadPool(MAX_THREAD)
            tasks = threadpool.makeRequests(self.tiktok_video_info, params, self.save_result_tiktok)
            [pool.putRequest(req) for req in tasks]
            pool.wait()
            for video in new_video_list:
                for task in tasks:
                    if video['video_id'] == task.kwds['video_id']:
                        for result in self.tiktok_results:
                            if result['request_id'] == task.requestID:
                                video['video_url'] = result['results']
                            else:
                                continue
                    else:
                        continue
            for video in new_video_list:
                video_id = video['video_id']
                if 'video_url' in video.keys():
                    if video['video_url'] is not None and video['video_url'] != '':
                        if self.collection.find_one({'video_id': video_id}):
                            del video['video_id']
                            self.collection.update_one({'video_id': video_id}, {'$set': video})
                            print(f'更新数据: {video_id}')
                        else:
                            self.collection.insert_one(video)
                            print(f'写入数据: {video_id}')
                    else:
                        print(f'tiktok video_url is None... skip saving')
                        continue
                else:
                    print(f'tiktok video_url is not in keys... skip saving')
                    continue
        else:
            print(f' 采集tiktok视频出现异常, keywords:{search_keywords}')

    def youtube_crawler(self, search_keywords):
        self.youtube_results = []
        video_list = self.youtube_search_video(search_keywords)
        new_video_list = []
        for video in video_list:
            video_id = video['video_id']
            if self.collection.find_one({'video_id': video_id}) is None or (
                    time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 4 * 60 * 60):
                new_video_list.append(video)
            else:
                continue
        print(f'youtube需要更新视频数量: {len(new_video_list)}')
        # print(new_video_list)
        if new_video_list is not None:
            params = [(None, {'video_id': video['video_id']}) for video in new_video_list]
            pool = threadpool.ThreadPool(MAX_THREAD)
            tasks = threadpool.makeRequests(self.youtube_video_info, params, self.save_result)
            [pool.putRequest(req) for req in tasks]
            pool.wait()
            for video in new_video_list:
                for task in tasks:
                    if video['video_id'] == task.kwds['video_id']:
                        for result in self.youtube_results:
                            if result['request_id'] == task.requestID:
                                video['video_url'] = result['results']['video_url']
                                video['audio_url'] = result['results']['audio_url']
                            else:
                                continue
                    else:
                        continue

            for video in new_video_list:
                video_id = video['video_id']
                if 'video_url' in video.keys():
                    if video['video_url'] is not None and video['video_url'] != '':
                        if self.collection.find_one({'video_id': video_id}):
                            del video['video_id']
                            self.collection.update_one({'video_id': video_id}, {'$set': video})
                        else:
                            self.collection.insert_one(video)
                    else:
                        continue
                else:
                    continue
        else:
            print(f' 采集youtube视频出现异常, keywords:{search_keywords}')

    def douyin_crawler(self, search_keywords):
        self.douyin_results = []
        video_list = []
        for i in range(MAX_PAGE):
            temp, has_more = self.douyin_search_video(search_keywords, offset=12 * i)
            if has_more == 1:
                for one in temp:
                    video_list.append(one)
            else:
                for one in temp:
                    video_list.append(one)
                break
        new_video_list = []
        for video in video_list:
            video_id = video['video_id']
            if self.collection.find_one({'video_id': video_id}) is None or (
                    time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 5 * 60 * 60):
                new_video_list.append(video)
            else:
                continue
        print(f'douyin 需要更新视频数量: {len(new_video_list)}')
        if new_video_list:
            for video in new_video_list:
                video_id = video['video_id']
                if 'video_url' in video.keys():
                    if video['video_url'] is not None and video['video_url'] != '':
                        if self.collection.find_one({'video_id': video_id}):
                            del video['video_id']
                            self.collection.update_one({'video_id': video_id}, {'$set': video})
                        else:
                            self.collection.insert_one(video)
                    else:
                        print(f'douyin video_url is None... skip saving')
                        continue
                else:
                    print(f'douyin video_url is not in keys... skip saving')
                    continue
        else:
            print(f'douyin 没有 需要更新视频, keywords:{search_keywords}')

    def save_result(self, request, result):
        self.youtube_results.append({'request_id': request.requestID, 'results': result})

    def save_result_tiktok(self, request, result):
        self.tiktok_results.append({'request_id': request.requestID, 'results': result})

    def tiktok_search_video(self, search_keywords, offset=0):
        cookiestr = "tt_csrf_token=poZiJA2w-g7ubYxO-IPYptHs43-fevP82K6c; tt_chain_token=LV3vyP9xkzu1olcUYxoMPA==; csrf_session_id=3c385bce12441f6a9adcb2b02b5e5dae; passport_csrf_token=13925ec1d3411be9048f73be0f660a95; passport_csrf_token_default=13925ec1d3411be9048f73be0f660a95; s_v_web_id=verify_lojksyop_PltyvHfO_6w5N_4DwS_AewM_sS6alf5MtDVD; multi_sids=7169356242610357254%3Af0585c4b10a9490c77eb0c414da470d4; cmpl_token=AgQQAPO8F-RO0rNARSMFN90__yRRexJef4A3YNODxQ; passport_auth_status=8dba23d8f1a6f74eb79aafed4c6e10fa%2C; passport_auth_status_ss=8dba23d8f1a6f74eb79aafed4c6e10fa%2C; sid_guard=f0585c4b10a9490c77eb0c414da470d4%7C1699110824%7C15552000%7CThu%2C+02-May-2024+15%3A13%3A44+GMT; uid_tt=afcd0f90ff8631face19e3f8a187453648b65e7c99ecafec77e51b179432c6a4; uid_tt_ss=afcd0f90ff8631face19e3f8a187453648b65e7c99ecafec77e51b179432c6a4; sid_tt=f0585c4b10a9490c77eb0c414da470d4; sessionid=f0585c4b10a9490c77eb0c414da470d4; sessionid_ss=f0585c4b10a9490c77eb0c414da470d4; sid_ucp_v1=1.0.0-KGMyNGM5ZmQ1NjE5MjE5MTM1MDI4MDVkZmMzNGQyNDA2YzQyOGFiY2MKHwiGiJToyPCqv2MQqL-ZqgYYswsgDDCDlvubBjgIQBIQAxoGbWFsaXZhIiBmMDU4NWM0YjEwYTk0OTBjNzdlYjBjNDE0ZGE0NzBkNA; ssid_ucp_v1=1.0.0-KGMyNGM5ZmQ1NjE5MjE5MTM1MDI4MDVkZmMzNGQyNDA2YzQyOGFiY2MKHwiGiJToyPCqv2MQqL-ZqgYYswsgDDCDlvubBjgIQBIQAxoGbWFsaXZhIiBmMDU4NWM0YjEwYTk0OTBjNzdlYjBjNDE0ZGE0NzBkNA; store-idc=alisg; store-country-code=sg; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=aL8uKtxviSyE5Urayg680oYvSQPlHCptrUNu0A50vNQtWjxDn4k0qL-IzEX_F4uVsDIH11h4Ld7xteVoPEN7X7j5TpZp2AeEw_xdP6-J6kGm74x_TW9Ij_I3lY3AFJZ0MXNRy_cIwqzy_AB1AfqtHlGTJ5cBi2x7vLVYGH-cRklp2purLxVRb7ofeJHQpvLhORGDpzCBdxuMjKpCDB992PzCMUCmyyibEyxIFy_TUZXquRhmcIkfRoVAbq5TwsdA6W2QpAyaN8ZS1MOkSpBqXMO8U6nF89XZnB49yiC_4YEC7x09_LUw_Uj9-idt6McglSyxzzEMNzShHjALyWNhEh-Y0sAsghC-R1yvn6Wl0-99AjqtiGl47AaKBeshO0J2hC_ojih5sqQUKgjSA2VZDatSRSHkNp535QMMUwVj_WTX7uSxwZpVPYkcxdz82kiC5Y0ayiA0YBDh8l0wpwNzo9jei5k53k5ojd3RsRkT6oYD2eFoUiDmcDH_CKf_-YVN; ttwid=1%7CPslqeUeyVJmPPQ_m2XdO-inB7WkSqW2h4e4P_ZxGZeE%7C1700471632%7C1f004ba9a4192e255a3ae80910ca98fc48f925429cd67d5b589b4eacbb8caa6a; msToken=nUPQqImtDM_NQKZgj14YiSn9x7sxb4MXPRmXJMP_0TK0jJvblzEEiTafq9tZclma4bfTjqX13vgK-TtsF1v1yP-Gm9kOpenFhlDPiC-1kyhH85JV8iPiKKIpPkUyn2D820hIe0LXf_mstVI=; odin_tt=7fa11e3dd2ce551f6d7a6aad704d6109f70424f6a6bf1c944e4d98b28535f26140e2f6f9eb8e4b5a1e719f71f52036e62ce8ddf8f49376ef581420643b8b0cb3595e9d0213e4ac88f9c1aa7a8569eb5e"
        keywords = search_keywords
        search_keywords = quote(search_keywords, safe='')
        print('search_keywords: ', search_keywords)
        url = f'https://www.tiktok.com/api/search/general/full/?aid=1988&app_language=zh-Hans&app_name=tiktok_web&browser_language=zh-CN&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F118.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&device_id=7291677034442016263&device_platform=web_pc&device_type=web_h264&focus_state=false&from_page=search&history_len=2&is_fullscreen=false&is_page_visible=true&keyword={search_keywords}&offset={offset}&os=mac&priority_region=&referer=&region=SG&screen_height=900&screen_width=1440&search_id=20231019143145139F4D25AFEB59234776&tz_name=Asia%2FShanghai&web_search_code=%7B%22tiktok%22%3A%7B%22client_params_x%22%3A%7B%22search_engine%22%3A%7B%22ies_mt_user_live_video_card_use_libra%22%3A1%2C%22mt_search_general_user_live_card%22%3A1%7D%7D%2C%22search_server%22%3A%7B%7D%7D%7D&webcast_language=zh-Hans'
        headers = {
            'authority': 'www.tiktok.com',
            'referer': 'https://www.tiktok.com/search?q=beautiful%20woman&t=1670318209758',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'cookie': cookiestr
        }
        res = self.simple_get(url=url, headers=headers)
        if res is None or res == '':
            print(f'直接请求失败, 开始curl请求...')
            curl_code = f"curl 'https://www.tiktok.com/api/search/general/full/?aid=1988&app_language=zh-Hans&app_name=tiktok_web&browser_language=zh-CN&browser_name=Mozilla&browser_online=true&browser_platform=MacIntel&browser_version=5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F118.0.0.0%20Safari%2F537.36&channel=tiktok_web&cookie_enabled=true&device_id=7291677034442016263&device_platform=web_pc&device_type=web_h264&focus_state=false&from_page=search&history_len=2&is_fullscreen=false&is_page_visible=true&keyword={search_keywords}&offset={offset}&os=mac&priority_region=&referer=&region=SG&screen_height=900&screen_width=1440&search_id=20231019143145139F4D25AFEB59234776&tz_name=Asia%2FShanghai&web_search_code=%7B%22tiktok%22%3A%7B%22client_params_x%22%3A%7B%22search_engine%22%3A%7B%22ies_mt_user_live_video_card_use_libra%22%3A1%2C%22mt_search_general_user_live_card%22%3A1%7D%7D%2C%22search_server%22%3A%7B%7D%7D%7D&webcast_language=zh-Hans' \
                    -H 'cookie: {cookiestr}' \
                    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' \
                    --compressed"
            res_curl = os.popen(curl_code).read()
            try:
                json.loads(res_curl)
                res = res_curl
            except:
                res = None
        has_more = 0
        if res is not None:
            results = []
            target = json.loads(res)
            if target['status_code'] < 300:
                if 'has_more' in target.keys():
                    if target['has_more'] == 1:
                        has_more = 1
                if 'data' not in target.keys():
                    return results, False
                videos = target['data']
                for video in videos:
                    if 'item' in video.keys():
                        video = video['item']
                    else:
                        continue
                    temp = {'keywords': keywords, 'video_id': video['id'], 'video_pic': video['video']['cover'],
                            'video_title': video['desc']
                            }
                    if re.search(r'(.+?)#', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)#', video['desc']).group(1)
                    elif re.search(r'(.+?)@', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)@', video['desc']).group(1)
                    else:
                        pass
                    temp['video_playtime'] = None
                    temp['video_watch_num'] = video['stats']['playCount']
                    temp['video_h5_url'] = video['video']['playAddr']
                    temp['video_datafrom'] = 'tiktok'
                    temp['video_update_time'] = time.time()
                    temp['audio_url'] = None
                    print(temp)
                    results.append(temp)
                return results, has_more
            else:
                raise Exception(f'tiktok: 更新: {search_keywords} 失败!!! 接口返回异常')
        else:
            raise Exception(f'tiktok: 更新: {search_keywords} 失败!!! 请检查接口')

    def tiktok_video_info(self, video_id):
        openudid = ''.join(random.sample('0123456789abcdef', 16))
        uuid = ''.join(random.sample('01234567890123456', 16))
        ts = int(time.time())
        url = f'https://api-h2.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}&version_name=26.1.3&version_code=2613&build_number=26.1.3&manifest_version_code=2613&update_version_code=2613&{openudid}=6273a5108e49dfcb&uuid={uuid}&_rticket=1667123410000&ts={ts}&device_brand=Google&device_type=Pixel%204&device_platform=android&resolution=1080*1920&dpi=420&os_version=10&os_api=29&carrier_region=US&sys_region=US%C2%AEion=US&app_name=trill&app_language=en&language=en&timezone_name=America/New_York&timezone_offset=-14400&channel=googleplay&ac=wifi&mcc_mnc=310260&is_my_cn=0&aid=1180&ssmix=a&as=a1qwert123&cp=cbfhckdckkde1'
        headers = self.tiktok_api_headers
        res = self.simple_get(url, headers)
        # input('test:::')
        if res is not None:
            data = json.loads(res)
            video_info = data['aweme_list'][0]
            video_url = None
            if 'play_addr' in video_info['video'].keys():
                if len(video_info['video']['play_addr']['url_list']) > 0:
                    video_url = video_info['video']['play_addr']['url_list'][0]
                else:
                    pass
            elif 'play_addr_265' in video_info['video'].keys():
                video_url = video_info['video']['play_addr_265']['url_list'][0]

            elif 'play_addr_h264' in video_info['video'].keys():
                video_url = video_info['video']['play_addr_264']['url_list'][0]
            else:
                pass
            print(f'tiktok video_url: {video_url}')
            return video_url
        else:
            print(f'tiktok 获取 {video_id} 详情失败!!!')
            return None

    def youtube_search_video(self, search_keywords):
        url = 'https://www.youtube.com/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false'
        headers = {
            'cookie': 'GPS=1; YSC=yqtzdPPcyKw; VISITOR_INFO1_LIVE=nOLEdqeSGwM; PREF=tz=Asia.Shanghai&f6=40000000; ST-cbjpxi=oq=funny&gs_l=youtube.12.0.0i512i433k1j0i512i433i131k1l4j0i512i433k1j0i512i3k1j0i512k1j0i512i433k1l2j0i512k1l4.9687.10621.0.16257.7.7.0.0.0.0.331.650.3-2.4.0....0...1ac.1j4.64.youtube..3.2.650.0..0i433i131k1.325.fYjIXqBJKd4&itct=CA0Q7VAiEwi588CKv5P7AhXQ_TgGHUB3BNI%3D&csn=MC4wMzU2OTczOTgwOTM3NTg0OQ..&endpoint=%7B%22clickTrackingParams%22%3A%22CA0Q7VAiEwi588CKv5P7AhXQ_TgGHUB3BNI%3D%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fresults%3Fsearch_query%3Dfunny%2Bvideo%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_SEARCH%22%2C%22rootVe%22%3A4724%7D%7D%2C%22searchEndpoint%22%3A%7B%22query%22%3A%22funny%20video%22%7D%7D',
            'authority': 'www.youtube.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-goog-visitor-id': 'CgtuT0xFZHFlU0d3TSi09ZGbBg%3D%3D'
        }
        country = random.choice(['US', 'SG', 'JP'])
        ip = random.choice(['172.53.173.232', '172.105.229.161', '182.125.229.161', '192.53.173.232'])
        data = {"context": {
            "client": {"hl": "zh-CN", "gl": f"{country}", "remoteHost": f"{ip}", "deviceMake": "", "deviceModel": "",
                       "visitorData": "CgtuT0xFZHFlU0d3TSi09ZGbBg%3D%3D",
                       "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36,gzip(gfe)",
                       "clientName": "WEB", "clientVersion": "2.20221103.04.00", "osName": "Windows",
                       "osVersion": "10.0",
                       "originalUrl": f"https://www.youtube.com/results?search_query={search_keywords}",
                       "platform": "DESKTOP", "clientFormFactor": "UNKNOWN_FORM_FACTOR", "configInfo": {
                    "appInstallData": "CLT1kZsGENSDrgUQm8quBRCZxq4FEJ_QrgUQsoj-EhCpp64FELjUrgUQt9yuBRCHkf4SEOK5rgUQuIuuBRCR-PwSENi-rQU%3D"},
                       "userInterfaceTheme": "USER_INTERFACE_THEME_DARK", "timeZone": "Asia/Shanghai",
                       "browserName": "Chrome", "browserVersion": "107.0.0.0",
                       "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                       "deviceExperimentId": "ChxOekUyTVRrNE5ESXlNamd5TWpBeU16WTNOdz09ELT1kZsG",
                       "screenWidthPoints": 1272, "screenHeightPoints": 1297, "screenPixelDensity": 1,
                       "screenDensityFloat": 1, "utcOffsetMinutes": 480, "memoryTotalKbytes": "8000000",
                       "mainAppWebInfo": {"graftUrl": "/results?search_query=funny+video",
                                          "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                                          "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                                          "isWebNativeShareAvailable": True}}, "user": {"lockedSafetyMode": False},
            "request": {"useSsl": True, "internalExperimentFlags": [], "consistencyTokenJars": []},
            "clickTracking": {"clickTrackingParams": "CA0Q7VAiEwi588CKv5P7AhXQ_TgGHUB3BNI="}, "adSignalsInfo": {
                "params": [{"key": "dt", "value": "1667529402961"}, {"key": "flash", "value": "0"},
                           {"key": "frm", "value": "0"}, {"key": "u_tz", "value": "480"},
                           {"key": "u_his", "value": "2"}, {"key": "u_h", "value": "1440"},
                           {"key": "u_w", "value": "2560"}, {"key": "u_ah", "value": "1400"},
                           {"key": "u_aw", "value": "2560"}, {"key": "u_cd", "value": "24"},
                           {"key": "bc", "value": "31"}, {"key": "bih", "value": "1297"},
                           {"key": "biw", "value": "1256"},
                           {"key": "brdim", "value": "0,0,0,0,2560,0,2560,1400,1272,1297"},
                           {"key": "vis", "value": "1"}, {"key": "wgl", "value": "true"},
                           {"key": "ca_type", "value": "image"}]}}, "query": f"{search_keywords}",
            "webSearchboxStatsUrl": "/search?oq=funny&gs_l=youtube.12.0.0i512i433k1j0i512i433i131k1l4j0i512i433k1j0i512i3k1j0i512k1j0i512i433k1l2j0i512k1l4.9687.10621.0.16257.7.7.0.0.0.0.331.650.3-2.4.0....0...1ac.1j4.64.youtube..3.2.650.0..0i433i131k1.325.fYjIXqBJKd4"}

        res = self.simple_post(url=url, headers=headers, data_json=json.dumps(data))
        if res is not None:
            # with open('youtube.json', 'w', encoding='utf-8')as f:
            #     f.write(res)
            target = json.loads(res)
            try:
                all_video = \
                    target['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                        'contents'][0]['itemSectionRenderer']['contents']
                target_video = filter(lambda x: 'videoRenderer' in x.keys(), all_video)
                target_video = [one['videoRenderer'] for one in target_video]
                video_list = []
                for video in target_video:
                    video_id = video['videoId']
                    video_datafrom = 'youtube'
                    video_update_time = time.time()
                    video_h5_url = f'https://www.youtube.com/watch?v={video_id}'
                    if len(video['thumbnail']['thumbnails']) > 0:
                        video_pic = video['thumbnail']['thumbnails'][-1]['url']
                    else:
                        video_pic = None
                    if len(video['title']['runs']) > 0:
                        video_title = video['title']['runs'][0]['text']
                        if re.search(r'(.+?)#', video_title):
                            video_title = re.search(r'(.+?)#', video_title).group(1)
                        elif re.search(r'(.+?)@', video_title):
                            video_title = re.search(r'(.+?)@', video_title).group(1)
                        else:
                            pass
                    else:
                        video_title = None
                    if 'lengthText' in video.keys():
                        if 'simpleText' in video['lengthText'].keys():
                            video_playtime = video['lengthText']['simpleText']
                        else:
                            video_playtime = None
                    else:
                        video_playtime = None
                    if 'viewCountText' in video.keys():
                        if 'simpleText' in video['viewCountText'].keys():
                            video_watch_num = video['viewCountText']['simpleText']
                        else:
                            video_watch_num = None
                    else:
                        video_watch_num = None
                    temp = {'keywords': search_keywords, 'video_id': video_id, 'video_pic': video_pic,
                            'video_title': video_title, 'video_playtime': video_playtime,
                            'video_watch_num': video_watch_num, 'video_h5_url': video_h5_url,
                            'video_datafrom': video_datafrom, 'video_update_time': video_update_time}
                    print(temp)
                    video_list.append(temp)
                return video_list
            except Exception as e:
                print(f'{url} 响应内容异常: {e}')
                return None

        else:
            raise Exception(f'youtube: 更新: {search_keywords} 失败!!! 请检查接口')

    def youtube_video_info(self, video_id):
        headers = {
            'cookie': 'VISITOR_INFO1_LIVE=9qZVrzB27uI; PREF=f4=4000000&tz=Asia.Shanghai; _ga=GA1.2.621834420.1648121145; _gcl_au=1.1.1853038046.1648121145; NID=511=Zc1APdmEbCD-iqVNVgI_vD_0S3LVI3XSfl-wUZEvvMU2MLePFKsQCaKUlUtchHSg-kWEVMGOhWUbxpQMwHeIuLjhxaslwniMh1OsjVfmOeTfhpwcRYpMgqpZtNQ7qQApY21xEObCvIez6DCMbjRhRQ5P7siOD3X87QX0CFyUxmY; OTZ=6430350_24_24__24_; GPS=1; YSC=0E115KqM_-I; GOOGLE_ABUSE_EXEMPTION=ID=d02004902c3d0f4d:TM=1648620854:C=r:IP=47.57.243.77-:S=YmZXPW7dxbu83bDuauEpXpE; CONSISTENCY=AGDxDeNysJ2boEmzRP4v6cwgg4NsdN4-FYQKHCGhA0AeW1QjFIU1Ejq1j8l6lwAc6c-pYTJiSaQItZ1M6QeI1pQ3wictnWXTOZ6_y8EKlt0Y_JdakwW6srR39-NLuPgSgXrXwtS0XTUGXpdnt4k3JjQ',
            'referer': 'https://www.youtube.com/results?search_query=jk%E7%BE%8E%E5%A5%B3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
        }
        url = f'https://www.youtube.com/watch?v={video_id}'
        response = self.simple_get(url=url, headers=headers)
        if response is not None:
            json_str = re.findall('var ytInitialPlayerResponse = (.*?);var', response)[0]
            json_data = json.loads(json_str)
            video_url = None
            audio_url = None
            new_list = []
            for one in json_data['streamingData']['adaptiveFormats']:
                if 'url' in one.keys():
                    new_list.append(one)
                else:
                    continue
            if len(new_list) > 0:
                video_url = new_list[0]['url']
                for data in new_list:
                    if 'height' in data.keys():
                        if data['height'] == 1080:
                            video_url = data['url']
                            break
                        else:
                            continue
                    else:
                        continue
                audio_url = new_list[-1]['url']
                for i in range(len(new_list) - 1, -1, -1):
                    if 'audio' in new_list[i]['mimeType'] and 'LOW' in new_list[i]['audioQuality']:
                        audio_url = new_list[i]['url']
                        break
                    else:
                        continue
                print(f'youtube video_url: {video_url}\naudio_url: {audio_url}')
                video_streaming_data = json_data['streamingData']['adaptiveFormats']
                return {'video_url': video_url, 'audio_url': audio_url}
            else:
                return {'video_url': video_url, 'audio_url': audio_url}

        else:
            print(f'获取 {video_id} 详情失败!!!')
            return {'video_url': None, 'audio_url': None}

    def douyin_search_video(self, search_keywords, offset=0):
        keywords = search_keywords
        search_keywords = quote(search_keywords)
        print(search_keywords)
        url = f'https://www.douyin.com/aweme/v1/web/search/item/?device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_video_web&sort_type=0&publish_time=0&keyword={search_keywords}&search_source=switch_tab&query_correct_type=1&is_filter_search=0&from_group_id=&offset={offset}&count=20&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=2560&screen_height=1440&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=107.0.0.0&browser_online=true&engine_name=Blink&engine_version=107.0.0.0&os_name=Windows&os_version=10&cpu_core_num=12&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=0&webid=7163531063863133732'
        try:
            # 读取抖音cookies
            with open('douyin_cookies.txt', 'r', encoding='utf-8') as file:
                cookies = file.read()
        except:
            cookies = None
            raise Exception(f'请复制抖音cookies到 douyin_cookies.txt!!!')
        headers = {
            'authority': 'www.douyin.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'referer': 'https://www.douyin.com/search/%E7%83%AD%E9%97%A8?publish_time=0&sort_type=0&source=switch_tab&type=video',
            'cookie': cookies
        }
        res = self.simple_get(url=url, headers=headers)
        # print('res: ', res)
        has_more = 0
        if res is not None:
            target = json.loads(res)
            if target['status_code'] < 300:
                if 'has_more' in target.keys():
                    if target['has_more'] == 1:
                        has_more = 1
                videos = target['data']
                results = []
                for video in videos:
                    video = video['aweme_info']
                    temp = {}
                    temp['keywords'] = keywords
                    temp['video_id'] = video['aweme_id']
                    temp['video_pic'] = video['video']['cover']['url_list'][0]
                    temp['video_title'] = video['desc']
                    if re.search(r'(.+?)#', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)#', video['desc']).group(1)
                    elif re.search(r'(.+?)@', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)@', video['desc']).group(1)
                    else:
                        pass
                    temp['video_playtime'] = None
                    temp['video_watch_num'] = video['statistics']['digg_count']
                    temp['video_h5_url'] = video['video']['play_addr']['url_list'][-1]
                    temp['video_datafrom'] = '抖音'
                    temp['video_update_time'] = time.time()
                    temp['audio_url'] = None
                    temp['video_url'] = temp['video_h5_url']
                    print(temp)
                    results.append(temp)
                return results, has_more
            else:
                raise Exception(f'tiktok: 更新: {search_keywords} 失败!!! 接口返回异常')
        else:
            raise Exception(f'tiktok: 更新: {search_keywords} 失败!!! 请检查接口')

    def simple_post(self, url, data_json, headers):
        for i in range(5):
            try:
                if self.proxy:
                    res = requests.post(url=url, headers=headers, data=data_json, proxies=self.proxy)
                else:
                    res = requests.post(url=url, headers=headers, data=data_json)
                if res.status_code < 300:
                    print(f'请求 {url} 成功! {res.status_code}')
                    return res.text
                else:
                    print(f'请求 {url} 响应异常 状态码为: {res.status_code}, 开始重试, 重试次数:{i + 1}')
                    time.sleep(random.uniform(0.5, 1))
                    continue
            except:
                print(f'请求 {url} 发生错误, 开始重试, 重试次数:{i + 1}')
                time.sleep(random.uniform(0.5, 1))
                continue
        raise Exception(f'接口: {url} 异常, 终止任务!')

    def simple_get(self, url, headers, cookies=None):
        for i in range(5):
            try:
                if self.proxy:
                    if cookies:
                        res = requests.get(url=url, headers=headers, cookies=cookies)
                    else:
                        res = requests.post(url=url, headers=headers, proxies=self.proxy)
                else:
                    if cookies:
                        res = requests.get(url=url, headers=headers, cookies=cookies)
                    else:
                        res = requests.get(url=url, headers=headers)
                if res.status_code < 300:
                    print(f'请求 {url} 成功! {res.status_code}')
                    return res.text
                else:
                    print(f'请求 {url} 响应异常 状态码为: {res.status_code} {res.text}, 开始重试, 重试次数:{i + 1}')
                    time.sleep(random.uniform(0.5, 1))
                    continue
            except Exception as e:
                print(f'请求 {url} 发生错误, 开始重试, 重试次数:{i + 1} error: {e}')
                time.sleep(random.uniform(0.5, 1))
                continue
        raise Exception(f'接口: {url} 异常, 终止任务!')


if __name__ == '__main__':
    crawler = Crawlers()
    # crawler.update_tiktok_cookies()
    # for i in range(10):
    # crawler.youtube_search_video('funny video')
    #     time.sleep(1)

    # crawler.youtube_video_info('cZ81NTPz3Fs')
    # for i in range(3):
    # crawler.youtube_crawler('funny video')
    #     time.sleep(3)
    # crawler.tiktok_search_video('beautiful girls', offset=0)
    # crawler.tiktok_video_info('7166533046601059585')
    # crawler.tiktok_crawler('funny')
    # crawler.youtube_crawler('funny')

    # crawler.douyin_search_video('小姐姐短视频')
    crawler.douyin_crawler('小姐姐短视频')
