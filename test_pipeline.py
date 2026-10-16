import asyncio
import os
import sys
from pathlib import Path

# Đảm bảo in tiếng Việt và emoji không bị lỗi font trên Windows PowerShell
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from config.settings import settings
from src.scriptwriter import ScriptWriter
from src.flow_automation import FlowAutomation
from src.video_processor import VideoProcessor
from src.youtube_uploader import YouTubeUploader

async def run_full_pipeline_test():
    topic = "Đột phá Siêu Chip AI và Mô hình Ngôn ngữ Thế hệ Mới 2026"
    print("=" * 65)
    print(f"🎬 BẮT ĐẦU CHẠY THỬ NGHIỆM QUY TRÌNH TOÀN DIỆN (A -> Z)")
    print(f"📌 Chủ đề: {topic}")
    print("=" * 65)

    # 1. AI Lên Kịch bản & Prompt phân cảnh
    print("\n[BƯỚC 1] 📝 Đang khởi tạo kịch bản và prompt phân cảnh...")
    writer = ScriptWriter()
    script = writer.generate_script(topic)
    print(f"  ✓ Tiêu đề video: {script.get('title')}")
    print(f"  ✓ Số phân cảnh: {len(script.get('scenes', []))} cảnh")
    for s in script.get('scenes', []):
        print(f"    - Cảnh {s.get('scene_number')}: {s.get('narration_vi')[:45]}...")
        print(f"      Prompt: {s.get('image_prompt_en')[:55]}...")

    # 2. Tạo hình ảnh/video các phân cảnh
    print("\n[BƯỚC 2] 🎨 Đang tạo footage/clip cho từng phân cảnh...")
    flow = FlowAutomation()
    scene_clips = []
    for s in script.get('scenes', []):
        clip_path = await flow.generate_scene_media(s, output_prefix="test_run")
        scene_clips.append(clip_path)
        print(f"  ✓ Đã hoàn tất footage cảnh {s.get('scene_number')}: {clip_path}")

    # 3. Lồng tiếng Edge TTS & Xuất video hoàn chỉnh
    print("\n[BƯỚC 3] 🎙️ Đang tạo giọng đọc tiếng Việt MC & ghép nối video 1080p...")
    processor = VideoProcessor(voice="vi-VN-NamMinhNeural")
    final_video_path = await processor.process_full_video(script, scene_clips)
    
    file_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
    print(f"  ✓ Đã xuất xưởng video thành công!")
    print(f"    - Đường dẫn: {final_video_path}")
    print(f"    - Dung lượng: {file_size_mb:.2f} MB")

    # 4. Tự động duyệt và đăng tải lên YouTube
    print("\n[BƯỚC 4] 🚀 Đang kích hoạt mô-đun đăng tải lên YouTube...")
    uploader = YouTubeUploader()
    upload_url = uploader.upload_video(
        video_path=final_video_path,
        title=script.get("title"),
        description=script.get("description"),
        tags=script.get("tags")
    )

    print("\n" + "=" * 65)
    print(f"🎉 HOÀN THÀNH QUY TRÌNH THỬ NGHIỆM THÀNH CÔNG RỰC RỠ!")
    print(f"🎥 Video thành phẩm: {final_video_path}")
    print(f"🔗 Link đăng tải: {upload_url}")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_full_pipeline_test())
