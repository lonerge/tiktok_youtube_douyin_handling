import json
import time
import datetime
import requests
import random
from selenium import webdriver
import sys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import configparser
import undetected_chromedriver as uc


config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')
login_config = config['Login']
path_config = config['Path']


class Login(object):
    def __init__(self):
        self.broswer = None
        self.wait = None
        self.arg = sys.argv[1]
        if self.arg == 'test':
            self.headless = False
        else:
            self.headless = True
        self.video_path = path_config['Video_path']
        self.error_path = path_config['Error_path']

        if login_config['Proxy_switch'] == 'False':
            self.proxy = None
        elif login_config['Use_simple_proxy'] == 'True':
            self.proxy = login_config['Simple_proxy']
        elif login_config['Use_socks5_proxy'] == 'True':
            self.proxy = login_config['Socks5_proxy']
        else:
            self.proxy = None
        self.agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
            "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0",
            "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; rv,2.0.1) Gecko/20100101 Firefox/4.0.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            "MAC：Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            "Windows：Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36",
            "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10"
        ]

    def kill_orphan_chrome(self):
        for i in range(2):
            if sys.argv[1] == 'test':
                try:
                    os.system(r"taskkill /f /im chromedriver.exe")
                except:
                    pass
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
            time.sleep(0.3)

    def is_element_exist_wait(self, wait, xpath):
        """
        显示等待：判断元素是否存在
        :param xpath: xpath语法
        :return: true or false
        """
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, xpath)))
            return True
        except:
            return False

    def init_broswer(self, url):
        self.kill_orphan_chrome()
        opt = webdriver.ChromeOptions()
        if self.proxy:
            opt.add_argument(f"--proxy-server={self.proxy}")

        opt = uc.ChromeOptions()
        opt.add_argument('--no-first-run')
        opt.add_argument('--no-service-autorun')
        opt.add_argument('--password-store=basic')
        opt.add_argument('--disable-gpu')
        user_data_dir = path_config['Chrome_log'] + str(time.time())
        opt.add_argument('--user-data-dir=' + user_data_dir)
        print('chrome 正在启动', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        _browser = uc.Chrome(options=opt, version_main=int(path_config['chrome_version']), user_data_dir=user_data_dir, headless=self.headless)
        print('chrome 启动成功', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        _browser.implicitly_wait(5)
        wait = WebDriverWait(_browser, timeout=5, poll_frequency=0.5)
        _browser.get(url)
        self.broswer = _browser
        self.wait = wait
        return _browser, wait

    def douyin_login(self):
        self.kill_orphan_chrome()
        url = 'https://www.douyin.com/'
        chrome = None
        wait = None
        for i in range(3):
            print(f'第 {i+1} 次初始化chrome ')
            try:
                chrome, wait = self.init_broswer(url=url)
                if 'douyin' in chrome.current_url:
                    print('chrome 正常状态...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                else:
                    continue
            except Exception as e:
                print(f'初始化chrome异常: {e}')
                if chrome:
                    chrome.quit()
                continue
        # 判断是否出现登录标签
        # 如果出现则直接保存图片扫码登录, 否则点击登录, 再保存图片扫码登录
        time.sleep(random.uniform(0.2, 0.5))
        if chrome:
            if self.is_element_exist_wait(wait, '//div[@id="login-pannel"]'):
                chrome.find_element(by='xpath', value='//*[@id="login-pannel"]//li[@aria-label="扫码登录"]').click()
                login_pic_url = chrome.find_element(by='xpath', value='//*[@id="login-pannel"]//img[@aria-label="二维码"]').get_attribute('src')
                return login_pic_url
            else:
                if self.is_element_exist_wait(wait, '//button[contains(text(), "登录")]'):
                    chrome.find_element(by='xpath', value='//button[contains(text(), "登录")]').click()
                    chrome.find_element(by='xpath', value='//*[@id="login-pannel"]//li[@aria-label="扫码登录"]').click()
                    login_pic_url = chrome.find_element(by='xpath', value='//*[@id="login-pannel"]//img[@aria-label="二维码"]').get_attribute('src')
                    return login_pic_url
                else:
                    print(f'未知加载转态!!!')
                    error_name = f'{int(time.time() * 1000)}_login_error.png'
                    chrome.save_screenshot(self.error_path+error_name)
                    chrome.quit()
                    return None
        else:
            print(f'初始化chrome失败! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            return None

    def douyin_upload(self, video_path, title):
        self.broswer.get('https://creator.douyin.com/creator-micro/content/upload')
        time.sleep(random.uniform(0.2, 0.5))
        for i in range(10):
            current_url = self.broswer.current_url
            if 'upload' in current_url and (i < 5):
                print('正常来到上传视频页面 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                break
            elif i >= 5:
                return '请先登录!!!'
            else:
                time.sleep(random.uniform(0.2, 0.5))
                continue
        if self.is_element_exist_wait(wait=self.wait, xpath='//input[@name="upload-btn"]'):
            print('选择视频, 开始上传 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            upload_button = self.broswer.find_element(by='xpath', value='//input[@name="upload-btn"]')
            upload_button.send_keys(video_path)
            time.sleep(random.uniform(0.2, 0.5))
            for j in range(5):
                if self.is_element_exist_wait(self.wait, '//div[contains(@class, "modal-button")]'):
                    self.broswer.find_element(by='xpath', value='//div[contains(@class, "modal-button")]').click()
                    print('点击modal标签 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                else:
                    time.sleep(random.uniform(0.1, 0.3))
                    continue
            for index in range(8):
                if index > 6:
                    return '未找到编辑视频标题标签'
                elif self.is_element_exist_wait(wait=self.wait, xpath='//div[@class="editor-kit-editor-container"]/div[1]/div'):
                    self.broswer.find_element(by='xpath', value='//div[@class="editor-kit-editor-container"]/div[1]/div').send_keys(title)
                    break
                else:
                    time.sleep(random.uniform(0.5, 1))
                    self.broswer.refresh()
                    continue
            print('编辑标题完成 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(random.uniform(0.2, 0.5))
            for k in range(50):
                if self.is_element_exist_wait(self.wait, '//p[contains(text(), "取消上传")]'):
                    print('等待上传视频完成 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(random.uniform(0.2, 0.4))
                    continue
                elif self.is_element_exist_wait(self.wait, '//div[contains(@class, "recommend-list")]/span'):
                    recommend_list = self.broswer.find_elements(by='xpath', value='//div[contains(@class, "recommend-list")]/span')
                    for index in range(len(recommend_list)):
                        if index < 3:
                            print('点击关联关键词标签 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                            recommend_list[index].click()
                            time.sleep(0.2)
                            continue
                        else:
                            break
                    break
                else:
                    time.sleep(random.uniform(0.2, 0.4))
                    continue
            js = "window.scrollTo(0,600)"
            self.broswer.execute_script(js)
            print('下滑页面 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            time.sleep(0.5)
            for k in range(10):
                print(f'第{k+1}次页面判断 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                # input(f'test{k+1}: ')
                # self.broswer.save_screenshot(f'test{k+1}.png')
                current_url = self.broswer.current_url
                if 'manage' in current_url:
                    print('发布成功!!! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    self.broswer.quit()
                    return True
                elif self.is_element_exist_wait(self.wait, '(//div[@class="semi-modal-footer"]//button)[1]'):
                    self.broswer.find_element(by='xpath', value='(//div[@class="semi-modal-footer"]//button)[1]').click()
                    print('点击暂不同步 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(random.uniform(0.1, 0.2))
                    continue
                elif self.is_element_exist_wait(self.wait, '//div[@class="douyin-popover__close"]'):
                    self.broswer.find_element(by='xpath', value='//div[@class="douyin-popover__close"]').click()
                    print('叉掉阻挡的文字 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(random.uniform(0.2, 0.5))
                    continue
                elif self.is_element_exist_wait(self.wait, '//div[@class="account-container"]'):
                    print('出现短信验证 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    return 'hcaptcha'
                elif self.is_element_exist_wait(self.wait, '(//div[contains(@class,"content-confirm")]/button)[1]'):
                    self.broswer.find_element(by='xpath', value='(//div[contains(@class,"content-confirm")]/button)[1]').click()
                    print('点击发布 ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(random.uniform(0.2, 0.5))
                    continue
                else:
                    time.sleep(random.uniform(0.2, 0.5))
                    continue
            file = self.error_path+str(int(time.time()))+'.png'
            self.broswer.save_screenshot(file)
            print('发布视频失败 截屏: ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.broswer.quit()
            return f'发布视频失败...'
        else:
            print(f'页面加载异常: 未找到上传视频标签 当前url: {self.broswer.current_url}')
            self.broswer.quit()
            return f'页面加载异常: 未找到上传视频标签'

    def tiktok_login(self, account, password):
        self.kill_orphan_chrome()
        url = 'https://bot.sannysoft.com/'
        chrome = None
        wait = None
        for i in range(3):
            print(f'第 {i + 1} 次初始化chrome')
            try:
                self.init_broswer(url=url)
                if 'sannysoft' in self.broswer.current_url:
                    print('chrome 正常状态...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                else:
                    continue
            except Exception as e:
                print(f'初始化chrome异常: {e}')
                if self.broswer:
                    self.broswer.quit()
                continue
        # 判断是否出现登录标签
        # 如果出现则直接保存图片扫码登录, 否则点击登录, 再保存图片扫码登录
        # time.sleep(random.uniform(0.2, 0.5))
        if self.broswer:
            index = 0
            while True:
                index += 1
                with open('stealth.min.js', mode='r') as f:
                    js = f.read()
                # 关键代码
                self.broswer.execute_cdp_cmd(
                    cmd_args={'source': js},
                    cmd="Page.addScriptToEvaluateOnNewDocument",
                )
                self.broswer.get('https://www.tiktok.com/login/phone-or-email/email')
                time.sleep(random.uniform(2, 3))
                current_url = self.broswer.current_url
                if index > 3:
                    print(f'三次登录失败!!!')
                    error_name = f'{int(time.time() * 1000)}_login_error.png'
                    self.broswer.save_screenshot(self.error_path + error_name)
                    self.broswer.quit()
                    return '三次登录失败!!!'
                elif 'login' in current_url:
                    self.broswer.find_element(by='xpath', value='//input[@name="username"]').send_keys(str(account))
                    print('输入用户名', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(3)
                    # for j in password:
                    self.broswer.find_element(by='xpath', value='//input[@autocomplete="new-password"]').send_keys(str(password))
                    time.sleep(1)
                    print('输入密码', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    # input(';;;;:')
                    self.broswer.find_element(by='xpath', value='//input[@autocomplete="new-password"]').submit()
                    time.sleep(random.uniform(5, 6))
                    continue
                else:
                    if self.broswer:
                        try:
                            self.broswer.quit()
                        except:
                            pass
                    return '登录成功!'
        else:
            print(f'初始化chrome失败! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if self.broswer:
                try:
                    self.broswer.quit()
                except:
                    pass
            return '初始化chrome失败! '

    def youtube_login(self, account, password):
        url = 'https://accounts.google.com/ServiceLogin'
        chrome = None
        wait = None
        for i in range(3):
            print(f'第 {i + 1} 次初始化chrome ')
            try:
                self.init_broswer(url=url)
                if 'accounts' in self.broswer.current_url:
                    print('chrome 正常状态...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                else:
                    if self.broswer:
                        self.broswer.quit()
                    continue
            except Exception as e:
                print(f'初始化chrome异常: {e}')
                if self.broswer:
                    self.broswer.quit()
                continue
        time.sleep(random.uniform(1, 2))
        if self.broswer:
            for i in range(10):
                # input('test:::: ')
                time.sleep(random.uniform(1, 2))
                current_url = self.broswer.current_url
                if i > 6:
                    print(f'6次未找到input 密码框,重新初始化chrome ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    break
                elif 'signin/identifier' in current_url:
                    self.broswer.find_element(by='xpath', value='//input[@type="email"]').click()
                    time.sleep(1)
                    # self.broswer.find_element(by='xpath', value='//input[@type="email"]').send_keys(account)
                    for one in account:
                        self.broswer.find_element(by='xpath', value='//input[@type="email"]').send_keys(one)
                        time.sleep(random.uniform(0.1, 0.4))
                    print(f'输入账号: {account}! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(random.uniform(1, 2))
                    self.broswer.find_element(by='xpath', value='//*[@id="identifierNext"]/div/button').click()
                    time.sleep(2)
                    continue
                elif 'challenge/pwd' in current_url:
                    if self.is_element_exist_wait(self.wait, '//*[@id="selectionc1"]'):
                        self.broswer.find_element(by='xpath', value='//input[@type="password"]').send_keys(password)
                        print(f'输入密码: {password}! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep(0.5)
                        self.broswer.find_element(by='xpath', value='//*[@id="passwordNext"]//button').click()
                        print(f'点击完成! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep(2)
                        self.broswer.get('https://studio.youtube.com/channel/')
                        time.sleep(random.uniform(1, 2))
                        break
                    else:
                        print(f'第{i + 1}次未找到input 密码框! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep(1)
                        continue
                elif 'signin/rejected' in current_url:
                    print(f'被检测... ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    return None
                else:
                    print(f'第{i+1}次未找到input 密码框! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    continue
            current_url = self.broswer.current_url
            print(f'current_url: {current_url}')
            if '/studio.youtube.com/' in current_url:
                print(f'youtube 登录成功!!!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if self.broswer:
                    try:
                        self.broswer.quit()
                    except:
                        pass
                return True
            else:
                print(f'youtube 登录失败!!!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if self.broswer:
                    try:
                        self.broswer.quit()
                    except:
                        pass
                return None
        else:
            print(f'初始化chrome失败! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if self.broswer:
                try:
                    self.broswer.quit()
                except:
                    pass
            return None

    def youtube_upload(self, video_path, title):
        for i in range(5):
            print(f'开始发布...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            login_url = 'https://studio.youtube.com/channel/'
            self.broswer.get(login_url)
            current_url = self.broswer.current_url
            time.sleep(random.uniform(1, 2))
            if 'youtube.com/channel' in current_url:
                print(f'来到发布视频页面...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if self.is_element_exist_wait(self.wait, '//*[@id="upload-button"]') or self.is_element_exist_wait(self.wait, '//*[@id="upload-icon"]'):
                    if self.is_element_exist_wait(self.wait, '//*[@id="upload-button"]'):
                        self.broswer.find_element(by='xpath', value='//*[@id="upload-button"]').click()
                    elif self.is_element_exist_wait(self.wait, '//*[@id="upload-icon"]'):
                        self.broswer.find_element(by='xpath', value='//*[@id="upload-icon"]').click()
                    else:
                        if self.broswer:
                            try:
                                self.broswer.quit()
                            except:
                                pass
                        return False
                    print(f'点击上传视频...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    time.sleep(1.5)
                    if self.is_element_exist_wait(self.wait, '//*[@id="burst"]'):
                        self.broswer.find_element(by='xpath', value='//*[contains(@id,"uploads-dialog-file")]//div[@id="content"]//input').send_keys(video_path)
                        print(f'选择视频开始上传...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        time.sleep(1)
                        for second in range(int(login_config['Max_upload_time'])):
                            time.sleep(2)
                            info = None
                            if self.is_element_exist_wait(self.wait, '//*[@id="dialog"]//ytcp-animatable[2]//span'):
                                info = self.broswer.find_element(by='xpath', value='//*[@id="dialog"]//ytcp-animatable[2]//span').text
                            if info is None:
                                continue
                            elif '检查完毕' in info:
                                for index in range(8):
                                    time.sleep(0.6)
                                    checked = None
                                    textbox = None
                                    next_button_hide = None
                                    public = None
                                    if self.is_element_exist_wait(self.wait, '//*[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]'):
                                        checked = self.broswer.find_element(by='xpath', value='//*[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]').get_attribute('aria-selected')
                                        print(f'checked : {checked}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    else:
                                        pass
                                    if self.is_element_exist_wait(self.wait, '//*[@id="textbox"]'):
                                        textbox = self.broswer.find_element(by='xpath', value='//*[@id="textbox"]').text
                                        print(f'textbox : {textbox}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    else:
                                        pass
                                    if self.is_element_exist_wait(self.wait, '//*[@id="next-button"]'):
                                        next_button_hide = self.broswer.find_element(by='xpath', value='//*[@id="next-button"]').get_attribute('aria-disabled')
                                        print(f'next_button_hide : {next_button_hide}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    else:
                                        pass
                                    if self.is_element_exist_wait(self.wait, '//*[@name="PUBLIC"]'):
                                        public = self.broswer.find_element(by='xpath', value='//*[@name="PUBLIC"]').get_attribute('aria-selected')
                                        print(f'public : {next_button_hide}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    else:
                                        pass
                                    if textbox is not None and textbox != title:
                                        self.broswer.find_element(by='xpath', value='//*[@id="textbox"]').clear()
                                        self.broswer.find_element(by='xpath', value='//*[@id="textbox"]').send_keys(title)
                                        print(f'编辑标题: {title}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        continue
                                    elif self.is_element_exist_wait(self.wait, '//*[@name="PUBLIC"]//*[@id="offRadio"]') and public == 'false':
                                        self.broswer.find_element(by='xpath', value='//*[@name="PUBLIC"]//*[@id="offRadio"]').click()
                                        print(f'点击公开...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        self.broswer.find_element(by='xpath', value='//*[@id="done-button"]').click()
                                        print(f'点击完成...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        print(f'发布完成!!!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        if self.broswer:
                                            try:
                                                self.broswer.quit()
                                            except:
                                                pass
                                        return True
                                    elif self.is_element_exist_wait(self.wait, '//*[@id="next-button"]') and next_button_hide == 'false':
                                        self.broswer.find_element(by='xpath', value='//*[@id="next-button"]').click()
                                        print(f'点击继续...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        continue
                                    elif self.is_element_exist_wait(self.wait, '//*[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]//div[@id="offRadio"]') and checked == 'false':
                                        self.broswer.find_element(by='xpath', value='//*[@id="step-badge-0"]').click()
                                        time.sleep(1)
                                        self.broswer.find_element(by='xpath', value='//*[@name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]//div[@id="offRadio"]').click()
                                        print(f'勾选 内容不是面向儿童标签...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        continue
                                    else:
                                        print(f'unknown...', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                        continue
                                if self.broswer:
                                    try:
                                        self.broswer.quit()
                                    except:
                                        pass
                                return False
                            else:
                                print(f'上传中: {info}', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                continue
                    else:
                        print(f'未找到上传区域标签', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        continue
                else:
                    print(f'未找到上传视频标签, 开始重试', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    continue
            elif 'signin/identifier' in current_url:
                print(f'登录状态丢失!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                continue
            else:
                print(f'未知加载状态!!!', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                continue
        if self.broswer:
            try:
                self.broswer.quit()
            except:
                pass
        return False

    def hcaptcha(self, code):
        self.broswer.find_element(by='xpath', value='//div[@class="account-container"]//input').send_keys(code)
        time.sleep(random.uniform(0.2, 0.5))
        self.broswer.find_element(by='xpath', value='//div[@class="account-container"]//div[contains(text(), "完成")]').click()
        time.sleep(random.uniform(0.2, 0.5))
        for k in range(6):
            current_url = self.broswer.current_url
            if 'manage' in current_url:
                print('发布成功!!! ', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.broswer.quit()
                return True
            elif self.is_element_exist_wait(self.wait, '//span[contains(text(), "暂不同步")]'):
                self.broswer.find_element(by='xpath', value='//span[contains(text(), "暂不同步")]').click()
                time.sleep(random.uniform(0.1, 0.2))
                continue
            else:
                time.sleep(random.uniform(0.2, 0.5))
                continue
        return False


if __name__ == '__main__':
    login = Login()
    # login.douyin_login()
    # input('登录中...:')
    # result = login.douyin_upload(video_path='', title='哈哈哈, 有国足那味了!')
    # print('result: ', result)
    # input('???:')

    # login.init_broswer(url='https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Dzh-CN%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=zh-CN&ec=65620', port='9898')
    result = login.tiktok_login(account=input('account: '), password=input('password: '))

    # result = login.youtube_login(account=input('account: '), password=input('password: '))
    # if result is True:
    #     login.youtube_upload(video_path='G:\\idm_download\\test1.mp4', title='beautiful girl')
    input('finally:::')