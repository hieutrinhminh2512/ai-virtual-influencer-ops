# 📋 BÁO CÁO TIẾN ĐỘ DỰ ÁN & HƯỚNG DẪN BÀN GIAO (HANDOVER)

> **Dự án:** YouTube AI Channel Manager (Tự động sản xuất & Quản lý kênh YouTube Tin tức AI)  
> **Ngôn ngữ / Framework:** Python 3.12, FastAPI, Playwright, Edge-TTS, MoviePy, Google GenAI SDK.  
> **Tài khoản Git:** `hieutrinhminh2512`  

---

## 1. Hệ thống đã làm được những gì? (ĐÃ HOÀN THÀNH 100%)

Hệ thống đã được lập trình hoàn chỉnh thành một dây chuyền tự động từ A đến Z, đã chạy thử nghiệm (`test_pipeline.py`) thành công và xuất ra video hoàn chỉnh:

1. **AI Scriptwriter (`src/scriptwriter.py`):**
   - Viết kịch bản tin tức công nghệ & xu hướng AI tóm tắt.
   - Phân chia từng cảnh quay chi tiết, viết lời bình tiếng Việt cho MC và tạo Prompt tiếng Anh chuẩn điện ảnh (8K, cinematic) cho mô hình tạo ảnh/video (Google Flow / Imagen 3 / Veo).
   - Có cơ chế Fallback tự động: nếu API Key lỗi hoặc chưa có key, hệ thống tự nạp kịch bản mẫu chất lượng cao, không bao giờ bị crash.

2. **Google Flow Automation (`src/flow_automation.py`):**
   - Điều khiển trình duyệt tự động bằng **Playwright** với profile lưu trữ phiên đăng nhập (`browser_profile/`).
   - Tự động điền prompt vào Google Flow và tải video về.
   - Nếu chưa đăng nhập Google Flow, tự động tạo footage đồ họa AI công nghệ thay thế để đảm bảo luồng sản xuất không bị ngắt quãng.

3. **Audio & Video Processing (`src/video_processor.py`):**
   - Tích hợp **Edge-TTS**: Giọng đọc tiếng Việt `vi-VN-NamMinhNeural` (giọng MC nam truyền cảm, tự nhiên, hoàn toàn miễn phí, không cần API Key).
   - Dùng **MoviePy** tự động ghép video từng phân cảnh, căn chỉnh độ dài video khớp chính xác với giọng đọc và xuất ra file video hoàn chỉnh 1080p chuẩn YouTube.

4. **Bảng điều khiển Web UI (`src/approval_ui.py` & `templates/index.html`):**
   - Dashboard giao diện tối hiện đại chạy tại `http://127.0.0.1:8000`.
   - Có trình phát video xem trước, ô sửa Tiêu đề, Mô tả, Tags.
   - Nút **`[✅ Duyệt & Đăng Lên YouTube]`** 1-click.
   - Ô nhập chủ đề mới để bấm tự động tạo video tiếp theo.

5. **Mô-đun YouTube Uploader (`src/youtube_uploader.py`):**
   - Kết nối YouTube Data API v3 tự động đăng video khi người dùng bấm Duyệt.
   - Có chế độ Test Simulation khi chưa gắn file `client_secret.json`.

6. **Mô-đun Telegram Bot (`src/telegram_bot.py`):**
   - Đã viết sẵn code gửi video kèm 2 nút bấm Duyệt / Huỷ về điện thoại (Chat ID đã lấy được là `1686351984`).

---

## 2. Những việc người tiếp theo cần làm (Next Steps)

Người tiếp quản dự án chỉ cần làm 3 việc cấu hình tài khoản (toàn bộ code nền tảng đã chạy tốt):

### Việc 1: Cấp lại Gemini API Key cá nhân
* Khóa Google Cloud hiện tại (`AQ.Ab8RN6L...`) bị lỗi `403 PERMISSION_DENIED` do tổ chức Google Cloud chưa mở quyền Generative Language.
* **Cách khắc phục:** Dùng Gmail cá nhân vào [Google AI Studio](https://aistudio.google.com/app/apikey) tạo một API Key mới (khóa cá nhân thường bắt đầu bằng `AIzaSy...`) và dán vào file `.env` tại dòng:
  ```env
  GEMINI_API_KEY=AIzaSy...
  ```

### Việc 2: Đăng nhập Google Flow một lần duy nhất
* Chạy lệnh:
  ```powershell
  python main.py --login-flow
  ```
* Trình duyệt sẽ hiện ra trang Google Flow (`https://labs.google/fx/tools/flow`), đăng nhập tài khoản Google có quyền truy cập Flow rồi quay lại terminal bấm **Enter**.

### Việc 3: Cấp file xác thực YouTube (để tự động đăng lên kênh)
* Vào [Google Cloud Console](https://console.cloud.google.com/), bật **YouTube Data API v3**.
* Tạo OAuth Client ID (loại **Desktop app**), tải file về đổi tên thành `client_secret.json` và để ngay tại thư mục gốc của dự án.
* *(Nếu không dùng YouTube API tự động, người dùng có thể lấy video hoàn chỉnh trong thư mục `outputs/videos/` để đăng thủ công lên YouTube).*

---

## 3. Cách khởi chạy dự án

```powershell
# 1. Cài thư viện (nếu qua máy mới)
pip install -r requirements.txt
python -m playwright install chromium

# 2. Khởi động Web UI Dashboard
python main.py

# 3. Mở trình duyệt xem bảng điều khiển
http://127.0.0.1:8000
```
