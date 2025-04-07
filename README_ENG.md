# 🚨 ATTENTION!!! 🚨
> **Project for learning and communication purposes only**  
> **Updates:**  
> - ✨ Added Douyin watermark-free video extraction feature, requires **Node.js** environment  
> - 🌐 Enabled TikTok/YouTube crawler functionality, requires overseas IP support  
> - 🍪 If Douyin crawler fails, please manually update **Cookies**  
> - 📦 Required third-party libraries are listed in `requirements.txt`

---

# 📺 Preview and Features

- **Preview Link:** [🎥 Video List](http://185.212.58.40:5050/video_list)  
- **Features:**  
  - 🔍 **Watermark-free Video Scraping**: Supports TikTok, YouTube, and Douyin videos  
  - 📤 **Video Publishing**: Supports publishing TikTok/YouTube videos to Douyin, or Douyin videos to TikTok/YouTube  
  - ⚙️ **Video Publishing Tool**: Uses Selenium for automated login and publishing operations

---

# 💻 Running Environment

- **Python 3**
- **Node.js**
- **PyExecJS** (for executing JS)
- **Flask** (provides Web service)
- **Selenium** (for login and video publishing)
- **Requests** (HTTP request library)
- **Threadpool** (multi-threading processing)
- **MongoDB** (for storing video data)

⚠️ Default MongoDB database has no password verification (modify if needed), database name must be: `handling_video`, collection name: `videos`

---

# 🚀 Starting the Program

### 1. Start Specific Video Crawler
- 🕒 **Recommended to configure Crontab, execute every 4 hours**  
    - **Local Testing:**  
      ```bash
      python3 -u timing_crawl.py test
      ```
    - **Server Deployment:**  
      ```bash
      python3 -u timing_crawl.py server
      ```

### 2. Start Web Service (ensure crawler is running first)
- **Local Testing:**  
  ```bash
  python3 -u run_server.py test

# 🌐 Web Pages

### 1. Video List Page
- **Example Link:** [🎥 Video List](http://185.212.58.40:5050/video_list)  
- **Features:**
  - 📜 Pagination: Maximum 50 videos per page, `pageSize` is fixed at 50  
  - 🔗 Click on video to automatically jump to corresponding video playback page

---

### 2. Video Playback Page
- **Example Link:** [▶️ Video Playback](http://185.212.58.40:5050/video?video_id=7056631930162400512)  
- **Features:**
  - ▶️ **Play Video**
  - 💾 **Download Video** (can choose to download to server or local)
  - 🚛 **Repost Video** (click to jump to repost page)
  - 🏷️ **Video Tags**: Shows video source and category keywords

---

### 3. Video Publishing Page
- **Example Link:** [📤 Video Publishing](http://185.212.58.40:5050/handling)  
- **Features:**
  - ▶️ **Play Video**
  - 🎬 **Merge Video**
  - 📤 **Publish Video** to specified platform
  - **Publishing Rules:**
    - **YouTube/TikTok** → **Douyin**: Need to scan QR code to login to Douyin account. If SMS verification code appears, further operation is required
    - **Douyin** → **YouTube**: Need to login with Google account password
    - **Douyin** → **TikTok**: Need to login with registered TikTok email

---

# ⚙️ Configuration File (Details in `config.ini`)

---

### 1. 🐛 Crawler Configuration (`Crawlers`)

```ini
# Keywords for video scraping, multiple keywords separated by commas
Keywords_english = hot
Keywords_chinese = 小姐姐

# Whether to enable each crawler
Tiktok_crawler = True
Youtube_crawler = True
Douyin_crawler = True

# Maximum thread count for crawler
Max_thread = 2

# TikTok/Douyin search results page count, maximum 3 pages (default 1 page)
Max_page = 1

# Whether to use proxy (default off, needs to run on overseas IP machine)
Proxy_switch = False

# Whether to use HTTP/HTTPS proxy
Use_simple_proxy = False
Simple_proxy = 127.0.0.1:9494

# Whether to use SOCKS5 proxy
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494
```

### 2. 🔐 Login Configuration (`Login`)

```ini
# Whether to use proxy (default off, needs to run on overseas IP machine)
Proxy_switch = False

# Whether to enable HTTP/HTTPS proxy
Use_simple_proxy = False
Simple_proxy = http://127.0.0.1:9494

# Whether to enable SOCKS5 proxy
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494

# Maximum wait time for video publishing (in seconds, default 180 seconds)
Max_upload_time = 180
```

### 3. 🌐 Web API Configuration (`Web_API`)

```ini
# API address (usually set to 0.0.0.0 for test environment)
Host = 0.0.0.0

# API default running port
Port = 5050
```

### 4. 🗂️ Path/Address Configuration (`Path`)

```ini
# Test environment MongoDB address
Mongo_host_local = 127.0.0.1

# Server environment MongoDB address
Mongo_host_server = 127.0.0.1

# Server environment MongoDB port
Mongo_port = 27017

# Chrome log directory (relative path, can be modified as needed)
Chrome_log = chrome_logs/

# Video save address and error screenshot address (relative path, can be modified as needed)
Video_path = static/videos/
Error_path = static/errors/

# Required Google Chrome version number
chrome_version = 119
```

# 📝 Notes

---

### 1. 🐛 Crawler
- Collected TikTok video links are short-lived, valid for less than 6 hours, so need to schedule tasks to collect every 4 hours.  
  (TikTok keyword search video interface automatically updates some videos, scheduled collection can regularly obtain popular videos containing keywords.)

- Collected YouTube video links are also short-lived, valid for less than 6 hours, need to schedule tasks to collect every 4 hours.  
  (Returned videos don't contain audio, need to merge video with corresponding audio or add new audio before publishing.)

- Collected Douyin videos have long-lived and short-lived links, but cannot be played online (reason unknown).  
  Need to click download button before playing, download video to server or local first, collect every 4 hours.

---

### 2. 🌐 Web Pages
- **Video Page (First Page)**  
  Contains the following features:
  - 💾 Download button (download icon)
  - ❤️ Repost button (heart icon)
  - ▶️ Next video button (next icon)

- **Repost Page (After clicking repost button)**  
  Contains the following features:
  - 🔐 Login area (supports QR code login, account password login, edit video title)
  - 🎬 Merge video button (only needed for YouTube videos)
  - 📤 Publish button (click to publish video)

- Backend uses Flask, frontend-backend interaction uses JavaScript AJAX POST requests for data transmission.

--- 