import os
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from config.settings import settings
from src.scriptwriter import ScriptWriter
from src.flow_automation import FlowAutomation
from src.video_processor import VideoProcessor
from src.youtube_uploader import YouTubeUploader
from src.telegram_bot import telegram_notifier

app = FastAPI(title="YouTube AI Manager")

# Mount thư mục lưu video để xem trên trình duyệt
app.mount("/videos", StaticFiles(directory=str(settings.VIDEOS_DIR)), name="videos")

templates = Jinja2Templates(directory=str(settings.BASE_DIR / "templates"))

# Bộ nhớ lưu trữ tạm thời các task chờ duyệt và lịch sử
pending_tasks: Dict[str, Dict[str, Any]] = {}
published_history: List[Dict[str, Any]] = []

class GenerateRequest(BaseModel):
    topic: str
    duration: str = "1-2 phút (4 phân cảnh)"

class ApprovePayload(BaseModel):
    title: str
    description: str
    tags: List[str]

@app.on_event("startup")
async def startup_event():
    # Khởi tạo Telegram Bot nếu có token
    await telegram_notifier.initialize()
    
    # Gắn callback khi người dùng bấm Duyệt trên Telegram Bot
    async def on_tg_approve(video_path: str, metadata: Dict[str, Any]):
        uploader = YouTubeUploader()
        url = uploader.upload_video(
            video_path=video_path,
            title=metadata["title"],
            description=metadata["description"],
            tags=metadata.get("tags", [])
        )
        published_history.insert(0, {"title": metadata["title"], "url": url})
        return url

    # Tự động nạp các video đã có sẵn trong thư mục outputs/videos vào danh sách chờ duyệt
    for vf in settings.VIDEOS_DIR.glob("final_*.mp4"):
        tid = vf.stem.replace("final_", "")[:12]
        if tid not in pending_tasks:
            pending_tasks[tid] = {
                "id": tid,
                "created_at": datetime.datetime.fromtimestamp(vf.stat().st_mtime).strftime("%H:%M:%S %d/%m/%Y"),
                "video_filename": vf.name,
                "video_path": str(vf),
                "metadata": {
                    "title": vf.stem.replace("final_", "").replace("_", " "),
                    "description": "Video tin tức công nghệ AI tự động sản xuất.\n\n#AI #Technology #TechNews",
                    "tags": ["AI", "Trí tuệ nhân tạo", "Công nghệ mới", "Gemini", "OpenAI"]
                }
            }

@app.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "gemini_ok": bool(settings.GEMINI_API_KEY),
            "tg_ok": bool(settings.TELEGRAM_BOT_TOKEN),
            "pending_tasks": list(pending_tasks.values()),
            "published_history": published_history
        }
    )

@app.post("/api/generate")
async def generate_video_pipeline(payload: GenerateRequest):
    """
    Kích hoạt toàn bộ chuỗi sản xuất video tự động:
    1. AI viết kịch bản (Gemini)
    2. Google Flow tạo cảnh quay
    3. Ghép lồng giọng đọc (Edge TTS & MoviePy)
    4. Gửi thông báo sang Telegram & Web UI
    """
    try:
        task_id = str(uuid.uuid4())[:8]
        print(f"[*] Bắt đầu sản xuất video mới cho chủ đề: '{payload.topic}' (Task ID: {task_id})")

        # Bước 1: Tạo kịch bản
        writer = ScriptWriter()
        script = writer.generate_script(payload.topic, payload.duration)

        # Bước 2: Tạo media từng phân cảnh qua Google Flow (Playwright)
        flow = FlowAutomation()
        scene_paths = []
        for scene in script.get("scenes", []):
            clip_path = await flow.generate_scene_media(scene, output_prefix=f"task_{task_id}")
            scene_paths.append(clip_path)

        # Bước 3: Ghép video hoàn chỉnh với giọng đọc tiếng Việt
        processor = VideoProcessor()
        final_video_path = await processor.process_full_video(script, scene_paths)
        video_filename = Path(final_video_path).name

        task_data = {
            "id": task_id,
            "created_at": datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y"),
            "video_filename": video_filename,
            "video_path": final_video_path,
            "metadata": {
                "title": script.get("title", "Video tin tức AI mới"),
                "description": script.get("description", ""),
                "tags": script.get("tags", [])
            }
        }
        pending_tasks[task_id] = task_data

        # Bước 4: Gửi thông báo đến Telegram Bot nếu đã kết nối
        await telegram_notifier.send_approval_request(
            task_id=task_id,
            video_path=final_video_path,
            metadata=task_data["metadata"]
        )

        return JSONResponse({"status": "success", "task_id": task_id, "video_filename": video_filename})
    except Exception as e:
        print(f"[!] Lỗi quy trình tạo video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/approve/{task_id}")
async def approve_and_upload(task_id: str, payload: ApprovePayload):
    task = pending_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Không tìm thấy task.")

    try:
        uploader = YouTubeUploader()
        url = uploader.upload_video(
            video_path=task["video_path"],
            title=payload.title,
            description=payload.description,
            tags=payload.tags
        )
        # Chuyển vào lịch sử
        published_history.insert(0, {"title": payload.title, "url": url})
        pending_tasks.pop(task_id, None)
        return {"status": "uploaded", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reject/{task_id}")
async def reject_video(task_id: str):
    if task_id in pending_tasks:
        pending_tasks.pop(task_id)
    return {"status": "rejected"}
