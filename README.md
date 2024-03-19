# 注意!!!:
- 开启tiktok/youtube爬虫, 需要境外ip; 
- 如果douyin爬虫失效, 可手动更新cookies;


# 预览及功能介绍
<details>
<summary>预览及功能介绍</summary>

- 预览: [video_list](http://173.242.115.60:5050/video_list)

</details>
- 无水印视频抓取: 包括tiktok视频; youtube视频; 抖音视频
- 视频搬运: tiktok/youtube的视频搬运到抖音; 抖音的视频搬运到tiktok获取youtube平台
- 搬运中的发布视频使用的selenium



# 运行环境:
- python3
- flask(提供web服务功能)
- selenium(登录及发布视频)
- requests(请求库)
- threadpool(线程池,多线程请求)
- mongodb(存储视频数据)
- 默认 mongodb 数据库无密码验证(有则自行修改); 必须建立数据库名: handling_vedio     表名: vedios



# 启动程序(默认启动路径为项目内)
- 开启指定视频爬虫(最好设置在crontab 四个小时执行一次)

        本地测试: python3 -u timing_crawl.py test
    
        部署在服务器: python3 -u timing_crawl.py server
  

- 开启web服务(开启之前,需要先开启爬虫)

        本地测试: python3 -u run_server.py test
        
        部署在服务器: python3 -u run_server.py server
        
        服务器后台启动: nohup python3 -u run_server.py server &
  

# Web 页面

- 1.视频列表页面:
        
        例如: http://bosshr.top:5050/video_list
        实现分页, 每页最多为50个, pagesize为固定50
        点击视频即可跳转到视频播放页面
            
- 2.视频播放页面:

        例如:http://bosshr.top:5050/video?video_id=7056631930162400512
        功能: 播放视频; 下载视频(下载到服务器或者本地) ; 搬运视频(点击跳转到搬运页面); 
        视频标签: 视频来源; 该视频的分类关键字
          
- 3.视频搬运页面:
        
        例如:http://bosshr.top:5050/handling
        功能: 播放视频; 合成视频; 发布视频到指定平台
        发布视频: 来源是youtube或tiktok的视频 发布到抖音平台; 来源是抖音的视频,可选择发布到tiktok或者youtube平台(点击选择按钮即可选择要发布的平台)
        登录: 来源是youtube或tiktok的视频 发布到抖音平台 登录需扫描二维码登录(如果出现短信验证码, 后续需要输入);
             来源是抖音的视频,发布到youtube平台需要账号密码登录(google账号)
             来源是抖音的视频, 发布到tiktok平台需要邮箱登录(注册tiktok的邮箱)


# 配置文件(详情见config.ini配置)
- Crawlers: 爬虫的配置项: 

        # 抓取视频的关键字 ,分割
        Keywords_english = hot
        Keywords_chinese = 小姐姐
        # 是否开启某爬虫抓取
        Tiktok_crawler = True
        Youtube_crawler = True
        Douyin_crawler = True
        # 爬虫发送请求时最大线程数量
        Max_thread = 2
        # # tiktok douyin 关键字搜索视频结果分页数,最多为3(默认最多抓取3页)
        Max_page = 1
        # 是否使用代理(默认不开启,需要运行在境外ip机器上; 开启时需要配置下面代理详情)
        Proxy_switch = False
        # http/https协议都使用以下代理(示例代理不可用, 需要境外ip, 并设下面Use为True)
        Use_simple_proxy = False
        Simple_proxy = 127.0.0.1:9494
        # socks5协议使用以下代理(示例代理不可用,需要境外ip, 并设下面Use为True)
        Use_socks5_proxy = False
        Socks5_proxy = socks5://127.0.0.1:9494


- Login : 模拟登录配置项:
    
        # 是否使用代理(默认不开启,需要运行在境外ip机器上; 开启时需要配置下面代理详情)
        Proxy_switch = False
        # http/https协议都使用以下代理(示例代理不可用, 需要境外ip, 并设下面Use为True)
        Use_simple_proxy = False
        Simple_proxy = http://127.0.0.1:9494
        # socks5协议使用以下代理(示例代理不可用,需要境外ip, 并设下面Use为True)
        Use_socks5_proxy = False
        Socks5_proxy = socks5://127.0.0.1:9494
        # 发布视频时,最大等待时间, 默认为180s, 超出时间, 发布视频失败
        Max_upload_time = 180


- Web_API : web服务配置项:
        
        # API地址, 一般测试环境为0.0.0.0
        Host = 0.0.0.0
        # API默认运行端口
        Port = 5050


- Path : 路径/地址配置项:
  
        # 测试环境 mongodb 地址 
        Mongo_host_local = 127.0.0.1

        # 服务器环境 mongodb 地址 
        Mongo_host_server = 127.0.0.1
        # 服务器环境 mongodb 端口 
        Mongo_port = 27017

        # chrome log 目录 这里是相对路径 可修改
        Chrome_log = chrome_logs/

        视频保存地址 报错截屏地址 这里是相对路径 可修改
        Video_path = static/videos/
        Error_path = static/errors/
        谷歌浏览器的版本号 必须
        chrome_version = 119
        

         



# 备注
- 爬虫: 
  
        采集到的tiktok视频链接为短效链接, 有效期不到6h, 所以安排定时任务, 每4h采集一次(tiktok关键字搜索视频接口自动更新部分视频, 定时采集实现了定时获取包含关键字的热门视频)
        
        采集到的youtube视频链接为短效链接, 有效期不到6h, 安排定时任务, 每4h采集一次; 返回的视频中不含音频, 发布前需要合成视频和相应的音频, 或者添加新的音频
        
        采集到的抖音视频有长效链接和短效链接, 但无法在线播放(原因未知) 播放前先点击下载按钮,下载到服务器或本地, 即可播放; 每4h采集一次; 

- web网页:
  
        视频页面(第一个页面)包含功能: 下载按钮(下载图标); 搬运按钮(爱心图片); 下一个视频按钮(下一个图标)   
        
        搬运页面(点击搬运按钮之后)包含功能: 登录区域(包含二维码登录, 账号密码登录, 编辑视频标题); 合成视频按钮(只有youtube的视频才需要合并); 发布按钮(点击即可发布视频)
    
        后端使用flask, 前后端交互, 采用js的ajax POST请求传输数据

        



