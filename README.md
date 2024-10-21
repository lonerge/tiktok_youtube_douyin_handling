# 🚨 注意!!! 🚨
> **项目仅供学习交流**  
> **更新内容：**  
> - ✨ 新增抖音无水印视频提取功能，需安装 **Node.js** 环境  
> - 🌐 开启 TikTok/YouTube 爬虫功能，需境外 IP 支持  
> - 🍪 若抖音爬虫失效，请手动更新 **Cookies**  
> - 📦 所需第三方库详见 `requirements.txt`

---

# 📺 预览及功能介绍

- **预览链接：** [🎥 视频列表](http://185.212.58.40:5050/video_list)  
- **功能介绍：**  
  - 🔍 **无水印视频抓取**：支持抓取 TikTok、YouTube 和抖音视频  
  - 📤 **视频发布**：支持将 TikTok/YouTube 视频发布至抖音，或将抖音视频发布到 TikTok/YouTube  
  - ⚙️ **发布视频工具**：使用 Selenium 进行自动化登录及发布操作

---

# 💻 运行环境

- **Python 3**
- **Node.js**
- **PyExecJS** (用于执行 JS)
- **Flask** (提供 Web 服务)
- **Selenium** (用于登录及视频发布)
- **Requests** (HTTP 请求库)
- **Threadpool** (多线程处理)
- **MongoDB** (用于存储视频数据)

⚠️ 默认 MongoDB 数据库无密码验证（如需，请自行修改），数据库名需为：`handling_video`，表名为：`videos`

---

# 🚀 启动程序

### 1. 开启指定视频爬虫
- 🕒 **建议配置 Crontab，每 4 小时执行一次**  
    - **本地测试：**  
      ```bash
      python3 -u timing_crawl.py test
      ```
    - **服务器部署：**  
      ```bash
      python3 -u timing_crawl.py server
      ```

### 2. 开启 Web 服务（确保先开启爬虫）
- **本地测试：**  
  ```bash
  python3 -u run_server.py test

# 🌐 Web 页面

### 1. 视频列表页面
- **示例链接：** [🎥 视频列表](http://185.212.58.40:5050/video_list)  
- **功能介绍：**
  - 📜 分页显示：每页最多展示 50 个视频，`pageSize` 固定为 50  
  - 🔗 点击视频后，自动跳转至对应的视频播放页面

---

### 2. 视频播放页面
- **示例链接：** [▶️ 视频播放](http://185.212.58.40:5050/video?video_id=7056631930162400512)  
- **功能介绍：**
  - ▶️ **播放视频**
  - 💾 **下载视频**（可选择下载到服务器或本地）
  - 🚛 **搬运视频**（点击后跳转至搬运页面）
  - 🏷️ **视频标签**：显示视频来源及分类关键字

---

### 3. 视频发布页面
- **示例链接：** [📤 视频发布](http://185.212.58.40:5050/handling)  
- **功能介绍：**
  - ▶️ **播放视频**
  - 🎬 **合成视频**
  - 📤 **发布视频**至指定平台
  - **发布规则：**
    - **YouTube/TikTok** → **抖音**：需扫码登录抖音账号。若出现短信验证码提示，需进一步操作
    - **抖音** → **YouTube**：需使用 Google 账号密码登录
    - **抖音** → **TikTok**：需使用注册 TikTok 的邮箱进行登录

---

# ⚙️ 配置文件 (详情见 `config.ini`)

---

### 1. 🐛 爬虫配置 (`Crawlers`)

```ini
# 抓取视频的关键字，多个关键字以逗号分隔
Keywords_english = hot
Keywords_chinese = 小姐姐

# 是否开启各爬虫
Tiktok_crawler = True
Youtube_crawler = True
Douyin_crawler = True

# 爬虫最大线程数量
Max_thread = 2

# TikTok/Douyin 搜索结果分页数，最多抓取 3 页（默认抓取 1 页）
Max_page = 1

# 是否使用代理（默认不开启，需运行在境外 IP 机器上）
Proxy_switch = False

# 是否使用 HTTP/HTTPS 代理
Use_simple_proxy = False
Simple_proxy = 127.0.0.1:9494

# 是否使用 SOCKS5 代理
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494
```

### 2. 🔐 登录配置 (`Login`)

```ini
# 是否使用代理（默认关闭，需要运行在境外 IP 机器上）
Proxy_switch = False

# 是否启用 HTTP/HTTPS 代理
Use_simple_proxy = False
Simple_proxy = http://127.0.0.1:9494

# 是否启用 SOCKS5 代理
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494

# 发布视频的最大等待时间（单位：秒，默认 180 秒）
Max_upload_time = 180
```

### 3. 🌐 Web API 配置 (`Web_API`)

```ini
# API 地址（一般测试环境设置为 0.0.0.0）
Host = 0.0.0.0

# API 默认运行端口
Port = 5050
```

### 4. 🗂️ 路径/地址配置 (`Path`)

```ini
# 测试环境 MongoDB 地址
Mongo_host_local = 127.0.0.1

# 服务器环境 MongoDB 地址
Mongo_host_server = 127.0.0.1

# 服务器环境 MongoDB 端口
Mongo_port = 27017

# Chrome 日志目录（相对路径，可根据需求修改）
Chrome_log = chrome_logs/

# 视频保存地址与报错截屏地址（相对路径，可根据需求修改）
Video_path = static/videos/
Error_path = static/errors/

# 必须指定的谷歌浏览器版本号
chrome_version = 119
```

# 📝 备注

---

### 1. 🐛 爬虫
- 采集到的 TikTok 视频链接为短效链接，有效期不足 6 小时，因此需要安排定时任务，每 4 小时采集一次。  
  （TikTok 关键字搜索视频接口会自动更新部分视频，定时采集可以实现定时获取包含关键字的热门视频。）

- 采集到的 YouTube 视频链接同样为短效链接，有效期不足 6 小时，需安排定时任务，每 4 小时采集一次。  
  （返回的视频中不含音频，发布前需要合成视频与相应的音频，或添加新的音频。）

- 采集到的抖音视频有长效链接和短效链接，但无法在线播放（原因未知）。  
  在播放前需先点击下载按钮，将视频下载到服务器或本地后方可播放，每 4 小时采集一次。

---

### 2. 🌐 Web 网页
- **视频页面（第一个页面）**  
  包含以下功能：
  - 💾 下载按钮（下载图标）
  - ❤️ 搬运按钮（爱心图片）
  - ▶️ 下一个视频按钮（下一个图标）

- **搬运页面（点击搬运按钮后）**  
  包含以下功能：
  - 🔐 登录区域（支持二维码登录、账号密码登录、编辑视频标题）
  - 🎬 合成视频按钮（仅针对 YouTube 视频需要合并）
  - 📤 发布按钮（点击即可发布视频）

- 后端使用 Flask，前后端交互采用 JavaScript 的 AJAX POST 请求进行数据传输。

---
