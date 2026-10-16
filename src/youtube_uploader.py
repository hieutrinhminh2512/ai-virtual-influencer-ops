import os
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config.settings import settings

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    def __init__(self, client_secret_file: Optional[str] = None):
        self.client_secret_file = Path(client_secret_file or settings.YOUTUBE_CLIENT_SECRET_FILE)
        self.token_file = settings.BASE_DIR / "youtube_token.pickle"
        self.youtube = None

    def get_authenticated_service(self):
        """
        Xác thực với Google OAuth2 cho YouTube Data API v3.
        Nếu đã xác thực 1 lần, token sẽ được lưu lại trong youtube_token.pickle.
        """
        credentials = None

        if self.token_file.exists():
            with open(self.token_file, "rb") as token:
                credentials = pickle.load(token)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not self.client_secret_file.exists():
                    raise FileNotFoundError(
                        f"Không tìm thấy file xác thực '{self.client_secret_file}'.\n"
                        f"Vui lòng vào Google Cloud Console, tạo OAuth Client ID (Desktop app) và tải file về đặt tại thư mục này."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secret_file), SCOPES
                )
                credentials = flow.run_local_server(port=0)

            # Lưu token cho các lần chạy sau
            with open(self.token_file, "wb") as token:
                pickle.dump(credentials, token)

        self.youtube = build("youtube", "v3", credentials=credentials)
        return self.youtube

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        category_id: str = "28", # 28 là danh mục Science & Technology (Khoa học & Công nghệ)
        privacy_status: Optional[str] = None
    ) -> str:
        """
        Tải video lên kênh YouTube.
        Trả về URL của video sau khi tải lên thành công.
        """
        status = privacy_status or settings.YOUTUBE_PRIVACY_STATUS
        
        # Nếu chưa có file client_secret.json, kích hoạt chế độ mô phỏng Test
        if not self.client_secret_file.exists():
            print(f"[!] [CHẾ ĐỘ TEST] Chưa tìm thấy file '{self.client_secret_file}'.")
            print(f"[*] Đang mô phỏng quá trình đóng gói và upload lên YouTube Data API v3:")
            print(f"    - Tiêu đề: {title}")
            print(f"    - Chế độ hiển thị: {status}")
            print(f"    - Thẻ Tags: {tags}")
            print(f"    - File thành phẩm: {video_path}")
            fake_id = "test_" + os.path.basename(video_path).replace(".mp4", "")
            test_url = f"https://youtu.be/{fake_id}"
            print(f"[+] [TEST THÀNH CÔNG] Video đã sẵn sàng đăng. Link mẫu: {test_url}")
            return test_url

        if not self.youtube:
            self.get_authenticated_service()

        body = {
            "snippet": {
                "title": title[:100], # YouTube giới hạn tối đa 100 ký tự cho tiêu đề
                "description": description[:5000],
                "tags": tags or ["AI", "Tech News", "Technology"],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": status, # 'private', 'unlisted', hoặc 'public'
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/*"
        )

        print(f"[*] Đang tải video lên YouTube: '{title}'...")
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            upload_status, response = request.next_chunk()
            if upload_status:
                print(f"[*] Tiến trình tải lên: {int(upload_status.progress() * 100)}%")

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        print(f"[+] Video đã được tải lên thành công!")
        print(f"[+] Link video: {video_url} (Chế độ: {status})")
        return video_url

if __name__ == "__main__":
    uploader = YouTubeUploader()
    print("YouTubeUploader module initialized.")
