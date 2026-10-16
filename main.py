import argparse
import asyncio
import uvicorn
from config.settings import settings

def run_login():
    """Mở trình duyệt để người dùng đăng nhập tài khoản Google Flow."""
    from src.flow_automation import FlowAutomation
    flow = FlowAutomation()
    asyncio.run(flow.open_browser_for_login())

def run_server():
    """Khởi động Web UI dashboard và Telegram Bot."""
    print("=" * 60)
    print("🚀 YOUTUBE AI MANAGER ĐANG KHỞI ĐỘNG...")
    print(f"👉 Bảng điều khiển Web UI: http://{settings.HOST}:{settings.PORT}")
    print(f"👉 Thư mục video thành phẩm: {settings.VIDEOS_DIR}")
    print("=" * 60)
    uvicorn.run("src.approval_ui:app", host=settings.HOST, port=settings.PORT, reload=False)

def run_cli_generation(topic: str):
    """Tạo video trực tiếp từ dòng lệnh CLI."""
    import requests
    url = f"http://{settings.HOST}:{settings.PORT}/api/generate"
    print(f"[*] Đang gửi yêu cầu tạo video: '{topic}'...")
    res = requests.post(url, json={"topic": topic})
    print(res.json())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube AI Channel Manager with Google Flow")
    parser.add_argument("--login-flow", action="store_true", help="Mở trình duyệt đăng nhập Google Flow để lưu cookie/profile")
    parser.add_argument("--create", type=str, help="Tạo video nhanh qua CLI với chủ đề chỉ định")
    parser.add_argument("--port", type=int, default=settings.PORT, help="Port cho Web UI")

    args = parser.parse_args()

    if args.login_flow:
        run_login()
    elif args.create:
        run_cli_generation(args.create)
    else:
        run_server()
