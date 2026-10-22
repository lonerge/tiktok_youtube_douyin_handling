**Ngôn ngữ: [简体中文](README.md) | [English](README_ENG.md) | Tiếng Việt**

# 🚨 LƯU Ý!!! 🚨
> **Dự án chỉ dùng cho mục đích học tập và giao lưu**  
> **Cập nhật:**  
> - ✨ Thêm tính năng tải video TikTok không logo, yêu cầu môi trường **Node.js**  
> - 🌐 Bật tính năng crawler TikTok/YouTube, yêu cầu IP nước ngoài  
> - 🍪 Nếu crawler TikTok không hoạt động, vui lòng cập nhật **Cookies** thủ công  
> - 📦 Các thư viện bên thứ ba cần thiết được liệt kê trong `requirements.txt`

---

# 📺 Xem trước và Tính năng

- **Liên kết xem trước:** [🎥 Danh sách video](http://185.212.58.40:5050/video_list)  
- **Tính năng:**  
  - 🔍 **Tải video không logo**: Hỗ trợ tải video từ TikTok, YouTube và TikTok  
  - 📤 **Đăng video**: Hỗ trợ đăng video TikTok/YouTube lên TikTok, hoặc video TikTok lên TikTok/YouTube  
  - ⚙️ **Công cụ đăng video**: Sử dụng Selenium để tự động đăng nhập và đăng video

---

# 💻 Môi trường Chạy

- **Python 3**
- **Node.js**
- **PyExecJS** (để thực thi JS)
- **Flask** (cung cấp dịch vụ Web)
- **Selenium** (để đăng nhập và đăng video)
- **Requests** (thư viện HTTP)
- **Threadpool** (xử lý đa luồng)
- **MongoDB** (để lưu trữ dữ liệu video)

⚠️ Cơ sở dữ liệu MongoDB mặc định không có xác thực mật khẩu (có thể sửa đổi nếu cần), tên cơ sở dữ liệu phải là: `handling_video`, tên bảng: `videos`

---

# 🚀 Khởi động Chương trình

### 1. Khởi động Crawler Video Cụ thể
- 🕒 **Khuyến nghị cấu hình Crontab, chạy mỗi 4 giờ**  
    - **Kiểm tra cục bộ:**  
      ```bash
      python3 -u timing_crawl.py test
      ```
    - **Triển khai máy chủ:**  
      ```bash
      python3 -u timing_crawl.py server
      ```

### 2. Khởi động Dịch vụ Web (đảm bảo crawler đang chạy)
- **Kiểm tra cục bộ:**  
  ```bash
  python3 -u run_server.py test

# 🌐 Trang Web

### 1. Trang Danh sách Video
- **Liên kết ví dụ:** [🎥 Danh sách Video](http://185.212.58.40:5050/video_list)  
- **Tính năng:**
  - 📜 Phân trang: Tối đa 50 video mỗi trang, `pageSize` cố định là 50  
  - 🔗 Nhấp vào video để tự động chuyển đến trang phát video tương ứng

---

### 2. Trang Phát Video
- **Liên kết ví dụ:** [▶️ Phát Video](http://185.212.58.40:5050/video?video_id=7056631930162400512)  
- **Tính năng:**
  - ▶️ **Phát Video**
  - 💾 **Tải Video** (có thể chọn tải về máy chủ hoặc máy cục bộ)
  - 🚛 **Chia sẻ Video** (nhấp để chuyển đến trang chia sẻ)
  - 🏷️ **Thẻ Video**: Hiển thị nguồn video và từ khóa phân loại

---

### 3. Trang Đăng Video
- **Liên kết ví dụ:** [📤 Đăng Video](http://185.212.58.40:5050/handling)  
- **Tính năng:**
  - ▶️ **Phát Video**
  - 🎬 **Ghép Video**
  - 📤 **Đăng Video** lên nền tảng chỉ định
  - **Quy tắc đăng:**
    - **YouTube/TikTok** → **TikTok**: Cần quét mã QR để đăng nhập tài khoản TikTok. Nếu hiện mã xác thực SMS, cần thao tác thêm
    - **TikTok** → **YouTube**: Cần đăng nhập bằng tài khoản Google
    - **TikTok** → **TikTok**: Cần đăng nhập bằng email đã đăng ký TikTok

---

# ⚙️ Tệp Cấu hình (Chi tiết trong `config.ini`)

---

### 1. 🐛 Cấu hình Crawler (`Crawlers`)

```ini
# Từ khóa để tải video, nhiều từ khóa phân tách bằng dấu phẩy
Keywords_english = hot
Keywords_chinese = 小姐姐

# Bật/tắt các crawler
Tiktok_crawler = True
Youtube_crawler = True
Douyin_crawler = True

# Số luồng tối đa cho crawler
Max_thread = 2

# Số trang kết quả tìm kiếm TikTok/TikTok, tối đa 3 trang (mặc định 1 trang)
Max_page = 1

# Sử dụng proxy hay không (mặc định tắt, cần chạy trên máy có IP nước ngoài)
Proxy_switch = False

# Sử dụng proxy HTTP/HTTPS hay không
Use_simple_proxy = False
Simple_proxy = 127.0.0.1:9494

# Sử dụng proxy SOCKS5 hay không
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494
```

### 2. 🔐 Cấu hình Đăng nhập (`Login`)

```ini
# Sử dụng proxy hay không (mặc định tắt, cần chạy trên máy có IP nước ngoài)
Proxy_switch = False

# Bật proxy HTTP/HTTPS hay không
Use_simple_proxy = False
Simple_proxy = http://127.0.0.1:9494

# Bật proxy SOCKS5 hay không
Use_socks5_proxy = False
Socks5_proxy = socks5://127.0.0.1:9494

# Thời gian chờ tối đa cho việc đăng video (đơn vị: giây, mặc định 180 giây)
Max_upload_time = 180
```

### 3. 🌐 Cấu hình Web API (`Web_API`)

```ini
# Địa chỉ API (thường đặt là 0.0.0.0 cho môi trường kiểm tra)
Host = 0.0.0.0

# Cổng chạy mặc định của API
Port = 5050
```

### 4. 🗂️ Cấu hình Đường dẫn/Địa chỉ (`Path`)

```ini
# Địa chỉ MongoDB môi trường kiểm tra
Mongo_host_local = 127.0.0.1

# Địa chỉ MongoDB môi trường máy chủ
Mongo_host_server = 127.0.0.1

# Cổng MongoDB môi trường máy chủ
Mongo_port = 27017

# Thư mục nhật ký Chrome (đường dẫn tương đối, có thể sửa đổi theo nhu cầu)
Chrome_log = chrome_logs/

# Địa chỉ lưu video và ảnh chụp lỗi (đường dẫn tương đối, có thể sửa đổi theo nhu cầu)
Video_path = static/videos/
Error_path = static/errors/

# Phiên bản Google Chrome bắt buộc
chrome_version = 119
```

# 📝 Ghi chú

---

### 1. 🐛 Crawler
- Liên kết video TikTok thu thập được có thời hạn ngắn, hiệu lực dưới 6 giờ, do đó cần lên lịch tác vụ, thu thập mỗi 4 giờ.  
  (Giao diện tìm kiếm video theo từ khóa TikTok tự động cập nhật một số video, thu thập theo lịch có thể thường xuyên lấy được video phổ biến chứa từ khóa.)

- Liên kết video YouTube thu thập được cũng có thời hạn ngắn, hiệu lực dưới 6 giờ, cần lên lịch tác vụ, thu thập mỗi 4 giờ.  
  (Video trả về không chứa âm thanh, cần ghép video với âm thanh tương ứng hoặc thêm âm thanh mới trước khi đăng.)

- Video TikTok thu thập được có liên kết dài hạn và ngắn hạn, nhưng không thể phát trực tuyến (lý do chưa rõ).  
  Cần nhấp nút tải xuống trước khi phát, tải video về máy chủ hoặc máy cục bộ trước, thu thập mỗi 4 giờ.

---

### 2. 🌐 Trang Web
- **Trang Video (Trang đầu tiên)**  
  Chứa các tính năng sau:
  - 💾 Nút tải xuống (biểu tượng tải xuống)
  - ❤️ Nút chia sẻ (biểu tượng trái tim)
  - ▶️ Nút video tiếp theo (biểu tượng tiếp theo)

- **Trang Chia sẻ (Sau khi nhấp nút chia sẻ)**  
  Chứa các tính năng sau:
  - 🔐 Khu vực đăng nhập (hỗ trợ đăng nhập bằng mã QR, đăng nhập bằng tài khoản mật khẩu, chỉnh sửa tiêu đề video)
  - 🎬 Nút ghép video (chỉ cần thiết cho video YouTube)
  - 📤 Nút đăng (nhấp để đăng video)

- Backend sử dụng Flask, tương tác frontend-backend sử dụng yêu cầu AJAX POST của JavaScript để truyền dữ liệu.

---
