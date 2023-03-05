# 预览及功能介绍
- 预览: http://43.156.63.82:5050/video_list
- 无水印视频抓取: 包括tiktok视频; youtube视频; 抖音视频
- 视频搬运: tiktok/youtube的视频搬运到抖音; 抖音的视频搬运到tiktok获取youtube平台
- 搬运中的发布视频使用的selenium


# 注意!!!:
- 开启tiktok/youtube爬虫,需要境外ip; 
- douyin爬虫失效,可手动更新cookies;

# 运行环境:
- python3
- flask(提供web服务功能)
- selenium(登录及发布视频)
- requests(请求库)
- mongodb(存储视频数据)
- threadpool(线程池,多线程请求)



# 启动程序(默认启动路径为项目内)
- 开启指定视频爬虫(最好设置在crontab 四个小时执行一次)

        测试: python3 -u timing_crawl.py test
    
        服务器: python3 -u timing_crawl.py server
  

- 开启web服务(开启之前,需要先开启爬虫)

        测试: python3 -u run_server.py test
        
        服务器: python3 -u run_server.py server
        
        服务器后台启动: nohup python3 -u run_server.py server &
  

# Web 页面

- 1.视频列表页面:
        
        例如:http://43.156.63.82:5050/video_list
        实现分页, 每页最多为50个, pagesize为固定50
        点击视频即可跳转到视频播放页面
            
- 2.视频播放页面:

        例如:http://43.156.63.82:5050/video?video_id=7056631930162400512
        功能: 播放视频; 下载视频(下载到服务器或者本地) ; 搬运视频(点击跳转到搬运页面); 
        视频标签: 视频来源; 该视频的分类关键字
          
- 3.视频搬运页面:
        
        例如:http://43.156.63.82:5050/handling
        功能: 播放视频; 合成视频; 发布视频到指定平台
        发布视频: 来源是youtube或tiktok的视频 发布到抖音平台; 来源是抖音的视频,可选择发布到tiktok或者youtube平台(点击选择按钮即可选择要发布的平台)
        登录: 来源是youtube或tiktok的视频 发布到抖音平台 登录需扫描二维码登录(如果出现短信验证码, 后续需要输入);
             来源是抖音的视频,发布到youtube平台需要账号密码登录(google账号)
             来源是抖音的视频, 发布到tiktok平台需要邮箱登录(注册tiktok的邮箱)


# 配置文件(详情见config.ini配置)
- Crawlers: 爬虫的配置项: 

        # 抓取视频的关键字 以,分割; Keywords_english为tiktok/youtube采集关键字; Keywords_chinese为抖音采集关键字
        Keywords_english = hot,happy,comedy,funny,beautiful girl
        Keywords_chinese = 热门短视频,搞笑短视频,喜剧短视频,小姐姐短视频
        # 是否开启某爬虫抓取
        Tiktok_crawler = True
        Youtube_crawler = True
        Douyin_crawler = True
        # 爬虫发送请求时最大线程数量
        Max_thread = 2
        # #关键字搜索视频结果分页数,最多为3(默认最多抓取3页)
        Max_page = 3
        # 是否使用代理(默认不开启,需要运行在境外ip机器上; 开启时需要配置下面代理详情)
        Proxy_switch = False
        # http/https协议都使用以下代理(示例代理不可用, 需要境外ip, 并设下面Use为True)
        Use_simple_proxy = False
        Simple_proxy = 43.156.63.82:9494
        # socks5协议使用以下代理(示例代理不可用,需要境外ip, 并设下面Use为True)
        Use_socks5_proxy = False
        Socks5_proxy = socks5://43.156.63.82:9494


- Login : 模拟登录配置项:
    
        # 是否使用代理(默认不开启,需要运行在境外ip机器上; 开启时需要配置下面代理详情)
        Proxy_switch = False
        # http/https协议都使用以下代理(示例代理不可用, 需要境外ip, 并设下面Use为True)
        Use_simple_proxy = False
        Simple_proxy = http://43.156.63.82:9494
        # socks5协议使用以下代理(示例代理不可用,需要境外ip, 并设下面Use为True)
        Use_socks5_proxy = False
        Socks5_proxy = socks5://43.156.63.82:9494


- Web_API : web服务配置项:
        
        # API地址, 一般测试环境为0.0.0.0
        Host = 0.0.0.0
        # 指定服务器 server API地址 可为0.0.0.0 也可指定 如:10.41.1.8
        Server_host = 10.41.1.8
        # API默认运行端口
        Port = 5050


- Path : 路径/地址配置项:
  
        # 测试环境 mongodb 地址 
        Mongo_host_local = 127.0.0.1
        # 测试环境 mongodb 端口 
        Mongo_port_ten = 27018
        # 服务器环境 mongodb 地址 
        Mongo_host_server = 10.41.1.14
        # 服务器环境 mongodb 端口 
        Mongo_port = 27017
        # chrome log 地址
        Chrome_log = /tmp/chrome/
        # 测试环境 视频保存地址 报错截屏地址
        Video_path_windows = E:\\tmp\\douyin_login\\videos\\
        Error_path_windows = E:\\tmp\\douyin_login\\error_pic\\
        Video_path_ten = /data/logs/handling_video/videos/
        Error_path_ten = /data/logs/handling_video/
        # 服务器环境 视频保存地址 报错截屏地址
        Video_path_server = /data/logs/pyvideos/videos/
        Error_path_server = /data/logs/pyvideos/errors/
        # 测试环境 Chrome 浏览器路径
        Chrome_path = start chrome
        # 服务器环境 Chrome 浏览器路径
        Chrome_path_server = /usr/bin/google-chrome
        # 测试环境 web 项目内视频地址 
        Web_video_path_windows = E:\\codes\\Handling_Vedio\\static\\videos\\
        Web_video_path = /home/ubuntu/Handling_Vedio/static/videos/
        # 服务器环境 web 项目内视频地址 
        Web_video_path_server = /data/code/pyvideos/static/videos/  



# 备注
- 爬虫: 
  
        采集到的tiktok视频链接为短效链接, 有效期不到6h, 所以安排定时任务, 每4h采集一次(tiktok关键字搜索视频接口自动更新部分视频, 定时采集实现了定时获取包含关键字的热门视频)
        
        采集到的youtube视频链接为短效链接, 有效期不到6h, 安排定时任务, 每4h采集一次; 返回的视频中不含音频, 发布前需要合成视频和相应的音频, 或者添加新的音频
        
        采集到的抖音视频有长效链接和短效链接, 但无法在线播放(原因未知) 播放前先点击下载按钮,下载到服务器或本地, 即可播放; 每4h采集一次; 

- web网页:
  
        视频页面(第一个页面)包含功能: 下载按钮(下载图标); 搬运按钮(爱心图片); 下一个视频按钮(下一个图标)   
        
        搬运页面(点击搬运按钮之后)包含功能: 登录区域(包含二维码登录, 账号密码登录, 编辑视频标题); 合成视频按钮(只有youtube的视频才需要合并); 发布按钮(点击即可发布视频)
    
        生成一个迭代器, 包含当前所有可用的视频, 如果可用视频数量变化则重新初始化迭代器, 保证迭代器生成最新的视频

        每次访问首页, 迭代器生成下一个视频信息, 然后根据信息渲染html页面, 实现每次访问都是不重复的视频
    
        后端使用flask, 前后端交互, 采用js的ajax POST请求传输数据(GET传输失败:未知原因)

        



