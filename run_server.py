from gevent import pywsgi
from gevent import monkey
monkey.patch_all()
import json
import random
import time
import os
import requests
from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
import sys
from login import Login
import re
import configparser
import math
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
# 限流
limiter = Limiter(app,
                 # key_func=get_remote_address,
                  default_limits=["200 per day", "50 per hour"])
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
api_config = config['Web_API']
path_config = config['Path']
if sys.argv[1] == 'test':
    client = MongoClient(host=path_config['Mongo_host_local'], port=int(path_config['Mongo_port']))
    collection = client['handling_vedio']['vedios']
    video_path = path_config['Video_path_windows']
    error_path = path_config['Error_path_windows']
elif sys.argv[1] == 'ten':
    client = MongoClient(host=path_config['Mongo_host_local'], port=int(path_config['Mongo_port_ten']))
    collection = client['handling_vedio']['vedios']
    video_path = path_config['Video_path_ten']
    error_path = path_config['Error_path_ten']
else:
    client = MongoClient(host=path_config['Mongo_host_server'], port=int(path_config['Mongo_port']))
    collection = client['handling_vedio']['vedios']
    video_path = path_config['Video_path_server']
    error_path = path_config['Error_path_server']
LOGIN = None
PREDATA = None
PROXY = {"http": 'socks5://43.156.63.82:9494', "https": 'socks5://43.156.63.82:9494'}
USEFUL_NUM = None


@app.route('/')
def root():
    return redirect(url_for('video_list'))


@app.route('/video_list')
def video_list():
    # pagesize默认固定长度 page传递的参数,分页作用
    global USEFUL_NUM
    kill_orphan_chrome()
    useful_num = int(collection.count_documents({'video_update_time': {'$gt': time.time() - 5 * 60 * 60}}))
    print('可用视频数量: ', useful_num)
    info = {'status': 0, 'video_list': [], 'has_more': False, 'message': None, 'page': 1, 'page_index': []}
    if useful_num > 0:
        page_size = 50
        page_num = int(math.ceil(useful_num/page_size))
        info['page_index'] = [i for i in range(1, page_num+1)]
        temp = request.args.get('page', 1)
        if re.search(r'\d', str(temp)):
            page = int(temp)
        else:
            page = 1
        info['page'] = page
        info['message'] = '获取视频列表成功!'
        index = page_size*page
        if index > useful_num:
            info['has_more'] = False
        else:
            info['has_more'] = True
        videos = collection.find({'video_update_time': {'$gt': time.time() - 5 * 60 * 60}}).limit(50).skip(index - 50)
        for video in videos:
            del video['_id']
            video['video_title'] = video['video_title'].strip().replace('\n', '')
            if video['video_title']:
                if len(video['video_title']) > 40:
                    video['video_title'] = video['video_title'][:40]
            if 'has_handling' in video.keys():
                if video['has_handling'] is True:
                    video['has_handling'] = '已搬运'
                else:
                    video['has_handling'] = '未搬运'
            else:
                video['has_handling'] = '未搬运'
            info['video_list'].append(video)
    else:
        info['status'] = -1
        info['message'] = 'there is no useful video'
    return render_template('video_list.html', data=info)


@app.route('/video', methods=['GET'])
def index():
    video_id = request.args.get('video_id')
    if video_id:
        return_data = collection.find_one({'video_id': video_id})
        if return_data:
            del return_data['_id']
            video_url = return_data['video_url']
            if return_data['video_datafrom'] == '抖音' or 'douyin' in video_url:
                video_url = video_url.replace('https://', 'http://')
            print('video_url: ', video_url)
            return render_template('home.html', data=json.dumps(return_data), origin_video_url=video_url)
        else:
            return 'no data '
    else:
        return 'video_id is wrong !!!'


@app.route('/jump', methods=['POST'])
def jump():
    video_id = request.form.get('video_id')
    temp = collection.find_one({'video_id': video_id})
    if temp:
        del temp['_id']
        return render_template('home.html', data=json.dumps(temp))
    else:
        return render_template('home.html', data=json.dumps({}))


@app.route('/pre_handling', methods=['POST'])
def pre_handling_video():
    print('pre_args: ', request.form)
    global PREDATA
    PREDATA = dict(request.form)
    return 'True'


@app.route('/handling', methods=['GET', 'POST'])
def handling_video():
    print('url: ', request.url)
    print('handling form: ', request.form)
    data = PREDATA
    if data:
        video_datafrom = data['video_datafrom']
        login = Login()
        global LOGIN
        LOGIN = login
        if video_datafrom == "抖音" or video_datafrom == 'douyin':
            # login.tiktok_login()
            return render_template('handling.html', data=json.dumps(data), dict=data, video_id=data['video_id'], login_pic_url='None')
        else:
            login_pic_url = login.douyin_login()
            if login_pic_url:
                pass
            else:
                login_pic_url = ''

            return render_template('handling.html', data=json.dumps(data), dict=data, video_id=data['video_id'], login_pic_url=login_pic_url)
    else:
        return redirect(url_for('video_list'))


@app.route('/download_video', methods=['POST'])
def download_video():
    if sys.argv[1] == 'test':
        path = path_config['Web_video_path_windows']
    elif sys.argv[1] == 'ten':
        path = path_config['Web_video_path']
    else:
        path = path_config['Web_video_path_server']
    video_url = request.form.get('video_url')
    video_id = request.form.get('video_id')
    video_name = video_id + '.mp4'
    video_path = path + video_name
    if os.path.exists(video_path):
        print(f'下载: {video_id} 无需下载')
        return video_name
    else:
        video_url = video_url.replace('https://', 'http://')
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        for i in range(3):
            try:
                if 'tiktok' in video_url or 'youtube' in video_url or 'google' in video_url:
                    resp = requests.get(url=video_url, headers=headers, stream=True)
                else:
                    resp = requests.get(url=video_url, headers=headers, stream=True)
                if resp.status_code < 300:
                    with open(path + video_name, 'wb')as f:
                        f.write(resp.content)
                    print(f'下载: {video_id} 成功! ')
                    return video_name
                else:
                    continue
            except:
                print(f'下载: {video_id} 失败, 开始重试')
        return '下载失败!'


@app.route('/refresh_login_pic', methods=['POST'])
def refresh_login_pic():
    kill_orphan_chrome()
    douyin_login = Login()
    global LOGIN
    LOGIN = douyin_login
    login_pic_url = douyin_login.douyin_login()
    if login_pic_url:
        pass
    else:
        login_pic_url = '刷新失败'
    print(f'刷新登录二维码: {login_pic_url}')
    return login_pic_url


@app.route('/publish', methods=['POST'])
def publish():
    global LOGIN
    # if LOGIN:
    if sys.argv[1] == 'test':
        path = path_config['Web_video_path_windows']
    elif sys.argv[1] == 'ten':
        path = path_config['Web_video_path']
    else:
        path = path_config['Web_video_path_server']
    video_id = request.form.get('video_id')
    video_datafrom = request.form.get('video_datafrom')
    account = request.form.get('account')
    password = request.form.get('password')
    title = request.form.get('title', ' ')
    publish_platform = request.form.get('publish_platform')
    video_name = video_id + '.mp4'
    print(f'title: {title} account: {account} password: {password} publish: {publish_platform}')
    if os.path.exists(path+video_name):
        video_path = path + video_name
    else:
        video_path = LOGIN.video_path + video_name
        video_url = request.form.get('video_url')
        video_url = video_url.replace('https://', 'http://')
        print(f'video_path: {video_path} video_url: {video_url}')
        for i in range(3):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
            try:
                print(f'第{i+1}次下载视频')
                if 'tiktok' in video_url or 'youtube' in video_url or 'google' in video_url:
                    resp = requests.get(url=video_url, headers=headers, stream=True)
                else:
                    resp = requests.get(url=video_url, headers=headers, stream=True)
                if resp.status_code < 300:
                    with open(video_path, 'wb')as f:
                        f.write(resp.content)
                    print(f'下载视频完成')
                    break
                else:
                    print(f'下载视频异常, 开始重试...')
                    continue
            except Exception as e:
                print(f'下载视频异常: {e}')
                continue
    if os.path.exists(video_path):
        print(f'开始发布视频')
        try:
            if publish_platform == 'tiktok':
                if account is not None and password is not None and account != '' and password != '':
                    login = Login()
                    LOGIN = login
                    result = login.tiktok_login(account=account, password=password)
                else:
                    result = '账号或密码为空'
            elif publish_platform == 'youtube':
                if account is not None and password is not None and account != '' and password != '':
                    login = Login()
                    LOGIN = login
                    result = login.youtube_login(account=account, password=password)
                else:
                    result = '账号或密码为空'
            else:
                result = LOGIN.douyin_upload(video_path=video_path, title=title)
        except Exception as e:
            print(f'发布视频, 页面异常: {e}')
            result = '页面异常'
            if LOGIN:
                if LOGIN.broswer:
                    LOGIN.broswer.save_screenshot(error_path+'error'+str(int(time.time()))+'.png')
                    LOGIN.broswer.quit()
        if result is True:
            collection.update_one({'video_id': video_id}, {'$set': {'has_handling': True}})
            message = 'success'
        else:
            message = result
    else:
        message = '网络环境异常, 请点击下载视频后重试!'
    # else:
    #     message = '找不到可用的chrome, 请返回刷新!'
    if LOGIN:
        if LOGIN.broswer:
            LOGIN.broswer.quit()
    return message


@app.route('/hcaptcha', methods=['POST'])
def hcaptcha():
    code = request.form.get('code')
    video_id = request.form.get('video_id')
    if re.search(r'\D', code):
        print(f'请输入正确的验证码: {code}')
        return 'error code'
    else:
        if LOGIN:
            result = LOGIN.hcaptcha(code=code)
            if result is True:
                collection.update_one({'video_id': video_id}, {'$set': {'has_handling': True}})
                message = 'success'
            else:
                message = '验证失败'
        else:
            message = '验证, 无可用的chrome'
        return message


def kill_orphan_chrome():
    num = 1
    while True:
        if sys.argv[1] == 'test':
            break
        else:
            if os.popen('ps -f --ppid 1 | grep chromedriver').read():
                try:
                    os.system("ps -f --ppid 1 | grep chromedriver | awk '{print $2}' | xargs kill -9")
                except:
                    pass
            if os.popen('ps -f --ppid 1 | grep chrome').read():
                try:
                    os.system("ps -f --ppid 1 | grep chrome | awk '{print $2}' | xargs kill -9")
                except:
                    pass
            if os.popen('ps -f --ppid 1 | grep chromedriver').read() == '' and os.popen(
                    'ps -f --ppid 1 | grep chrome').read() == '':
                break
        num += 1
        time.sleep(random.uniform(0.1, 0.2))
        if num > 3:
            break


if __name__ == '__main__':
    if sys.argv[1] == 'ten':
        # app.run(host=api_config['Host'], port=int(api_config['Port']), debug=True)
        # app.run(host=api_config['Host'], port=int(api_config['Port']), debug=True)
        server = pywsgi.WSGIServer((api_config['Host'], int(api_config['Port'])), app)
        server.serve_forever()
    elif sys.argv[1] == 'test':
        app.run(host=api_config['Host'], port=int(api_config['Port']), debug=True)
    else:
        app.run(host=api_config['Server_host'], port=int(api_config['Port']))

