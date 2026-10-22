import json
import time
import datetime
import requests
import random
import sys
from pymongo import MongoClient
import re
import threadpool
from urllib.parse import quote
import configparser
import os
import undetected_chromedriver as uc
import douyin_video
from credentials import add_optional_cookie_header, get_required_env, load_douyin_cookie, load_tiktok_cookie_header

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
        elif path_config.get('Mongo_username', None) and path_config.get('Mongo_password', None):
            # mongodb有认证
            client = MongoClient(host=path_config['Mongo_host_server'], port=int(path_config['Mongo_port']), username=path_config['Mongo_username'], password=path_config['Mongo_password'], authSource='admin', authMechanism='SCRAM-SHA-256')
        else:
            # mongodb无认证
            client = MongoClient(host=path_config['Mongo_host_server'], port=int(path_config['Mongo_port']))
        self.db = client['handling_vedio']
        self.collection = self.db['vedios']
        self.info = {'video_id': None, 'video_title': None, 'video_url': None, 'audio_url': None,
                     'update_timestamp': None}
        self.youtube_results = []
        self.tiktok_results = []
        self.douyin_results = []
        self.arg = sys.argv[1]
        self.tiktok_cookies_file = os.environ.get('TIKTOK_COOKIES_FILE', crawlers_config.get('Tiktok_cookies_file', 'tiktok_cookies.json'))
        self.douyin_cookies_file = os.environ.get('DOUYIN_COOKIES_FILE', crawlers_config.get('Douyin_cookies_file', 'douyin_cookies.txt'))
        self.request_timeout = (
            crawlers_config.getfloat('Request_connect_timeout', fallback=5.0),
            crawlers_config.getfloat('Request_read_timeout', fallback=20.0),
        )
        if crawlers_config['Proxy_switch'] == 'False':
            self.proxy = None
        elif crawlers_config['Use_socks5_proxy'] == 'True':
            self.proxy = {"http": crawlers_config['Socks5_proxy'], "https": crawlers_config['Socks5_proxy']}
        elif crawlers_config['Use_simple_proxy'] == 'True':
            simple_proxy = crawlers_config['Simple_proxy']
            if '://' not in simple_proxy:
                simple_proxy = 'http://' + simple_proxy
            self.proxy = {"http": simple_proxy, "https": simple_proxy}
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
                with open(self.tiktok_cookies_file, 'w', encoding='utf-8') as f:
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
        # 旧版废弃
        # for i in range(MAX_PAGE):
        #     try:
        #         temp, has_more = self.tiktok_search_video(search_keywords, offset=12 * i)
        #     except:
        #         continue
        #     if has_more == 1:
        #         for one in temp:
        #             video_list.append(one)
        #     else:
        #         for one in temp:
        #             video_list.append(one)
        #         break

        # 新版
        video_list.extend(self.tiktok_search_video_remote(search_keywords))
        # new_video_list = []
        # for video in video_list:
        #     video_id = video['video_id']
        #     if self.collection.find_one({'video_id': video_id}) is None or (time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 30 * 60):
        #         new_video_list.append(video)
        #     else:
        #         continue
        print(f'tiktok需要更新视频数量: {len(video_list)}')
        if video_list:
            # 旧版废弃
            # params = [(None, {'video_id': video['video_id']}) for video in new_video_list]
            # pool = threadpool.ThreadPool(MAX_THREAD)
            # tasks = threadpool.makeRequests(self.tiktok_video_info, params, self.save_result_tiktok)
            # [pool.putRequest(req) for req in tasks]
            # pool.wait()
            # for video in new_video_list:
            #     for task in tasks:
            #         if video['video_id'] == task.kwds['video_id']:
            #             for result in self.tiktok_results:
            #                 if result['request_id'] == task.requestID:
            #                     video['video_url'] = result['results']
            #                 else:
            #                     continue
            #         else:
            #             continue
            for video in video_list:
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
        video_list = []
        try:
            video_list = self.youtube_search_video(search_keywords)
        except:
            pass
        new_video_list = []
        for video in video_list:
            video_id = video['video_id']
            if self.collection.find_one({'video_id': video_id}) is None or (
                    time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 30 * 60):
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
            try:
                temp, has_more = self.douyin_search_video(search_keywords, offset=12 * i)
            except:
                continue
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
                    time.time() - self.collection.find_one({'video_id': video_id})['video_update_time'] > 30 * 60):
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
        cookiestr = load_tiktok_cookie_header(self.tiktok_cookies_file)
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
            print(f'res: {res}')
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

    def tiktok_search_video_remote(self, search_keywords, pages=3):
        print('search_keywords: ', search_keywords)
        url = f'http://185.212.58.40:7758/tiktok_search'
        headers = {
            "Content-Type": "application/json",
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
        headers['cookie'] = f'token={get_required_env("TIKTOK_REMOTE_API_TOKEN")}'
        data = {"keyword": search_keywords, "sort": 0, "platform": "tiktok", "pages": pages}
        res = self.simple_post(url=url, headers=headers, data_json=json.dumps(data))
        if res is not None:
            print(f'res: {res}')
            results = []
            target = json.loads(res)
            for video in target['data']:
                temp = {'keywords': search_keywords, 'video_id': video['video_id'], 'video_pic': video['cover'],
                        'video_title': video['description']
                        }
                if re.search(r'(.+?)#', video['description']):
                    temp['video_title'] = re.search(r'(.+?)#', video['description']).group(1)
                elif re.search(r'(.+?)@', video['description']):
                    temp['video_title'] = re.search(r'(.+?)@', video['description']).group(1)
                else:
                    pass
                temp['video_playtime'] = None
                temp['video_watch_num'] = video['play_count']
                temp['video_h5_url'] = video['download_no_watermark_addr']
                temp['video_url'] = video['download_no_watermark_addr']
                temp['video_datafrom'] = 'tiktok'
                temp['video_update_time'] = time.time()
                temp['audio_url'] = None
                print(temp)
                results.append(temp)
            return results
        else:
            raise Exception(f'tiktok: 更新: {search_keywords} 失败!!! 请检查接口')

    def tiktok_video_info(self, video_id):
        openudid = ''.join(random.sample('0123456789abcdef', 16))
        uuid = ''.join(random.sample('01234567890123456', 16))
        req_ticket = str(int(time.time() * 1000))
        ts = int(time.time())
        url = f'https://api-h2.tiktokv.com/aweme/v1/feed/?aweme_id={video_id}&version_name=37.0.4&version_code=370004&build_number=37.0.4&manifest_version_code=2023700040&update_version_code=2023700040&openudid={openudid}&uuid={uuid}&_rticket={req_ticket}&ts={ts}&device_brand=Redmi&device_type=Redmi%20K30%20Pro%20Zoom%20Edition&device_platform=android&resolution=1080*1920&dpi=420&os_version=10&os_api=29&carrier_region=US&sys_region=US%C2%AEion=US&app_name=trill&app_language=en&language=en&timezone_name=America/New_York&timezone_offset=-14400&channel=googleplay&ac=wifi&mcc_mnc=310260&is_my_cn=0&aid=1180&ssmix=a&as=a1qwert123&cp=cbfhckdckkde1'
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
        url = f'https://www.youtube.com/youtubei/v1/search?key={get_required_env("YOUTUBE_API_KEY")}&prettyPrint=false'
        headers = {
            'authority': 'www.youtube.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'x-goog-visitor-id': 'CgtuT0xFZHFlU0d3TSi09ZGbBg%3D%3D'
        }
        add_optional_cookie_header(headers, 'YOUTUBE_COOKIE')
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
            'referer': 'https://www.youtube.com/results?search_query=jk%E7%BE%8E%E5%A5%B3',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'
        }
        add_optional_cookie_header(headers, 'YOUTUBE_COOKIE')
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
        cookies = load_douyin_cookie(self.douyin_cookies_file)
        headers = {
            'authority': 'www.douyin.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'referer': 'https://www.douyin.com/search/%E7%83%AD%E9%97%A8?publish_time=0&sort_type=0&source=switch_tab&type=video',
            'cookie': cookies
        }
        res = self.simple_get(url=url, headers=headers)
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
                    video = video['aweme_info']
                    temp = {'keywords': keywords, 'video_id': video['aweme_id'],
                            'video_pic': video['video']['cover']['url_list'][0], 'video_title': video['desc']}
                    if re.search(r'(.+?)#', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)#', video['desc']).group(1)
                    elif re.search(r'(.+?)@', video['desc']):
                        temp['video_title'] = re.search(r'(.+?)@', video['desc']).group(1)
                    else:
                        pass
                    temp['video_h5_url'] = video['video']['play_addr']['url_list'][-1]
                    try:
                        # 提取抖音无水印视频
                        temp['video_h5_url'] = douyin_video.get_douyin_origin_video(aweme_id=video['aweme_id'])['originVideo']
                    except:
                        continue
                    temp['video_playtime'] = None
                    temp['video_watch_num'] = video['statistics']['digg_count']
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
                request_options = {'url': url, 'headers': headers, 'data': data_json, 'timeout': self.request_timeout}
                if self.proxy:
                    request_options['proxies'] = self.proxy
                res = requests.post(**request_options)
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
                request_options = {'url': url, 'headers': headers, 'timeout': self.request_timeout}
                if self.proxy:
                    request_options['proxies'] = self.proxy
                if cookies is not None:
                    request_options['cookies'] = cookies
                res = requests.get(**request_options)
                if res.status_code < 300:
                    print(f'请求 {url} 成功! {res.status_code}')
                    return res.text
                else:
                    print(f'请求 {url} 响应异常 状态码为: {res.status_code}, 开始重试, 重试次数:{i + 1}')
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
    # crawler.tiktok_search_video_remote('beautiful girls')
    # crawler.tiktok_video_info('7462168953985486098')
    crawler.tiktok_crawler('love')
    # crawler.youtube_crawler('funny')

    # crawler.douyin_search_video('今日热点')
    # crawler.douyin_crawler('小姐姐短视频')
