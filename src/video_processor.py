import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import edge_tts
try:
    from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from config.settings import settings

class VideoProcessor:
    def __init__(self, voice: str = "vi-VN-NamMinhNeural"):
        """
        voice: Giọng đọc Microsoft Edge TTS tiếng Việt:
        - "vi-VN-NamMinhNeural" (Nam - giọng MC truyền cảm, tin tức rất chuẩn)
        - "vi-VN-HoaiMyNeural" (Nữ - giọng chuẩn đài truyền hình)
        """
        self.voice = voice

    async def generate_speech(self, text: str, output_path: str) -> str:
        """
        Tạo file audio giọng đọc tiếng Việt bằng Edge TTS (hoàn toàn miễn phí, không cần API Key).
        """
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        return output_path

    async def process_full_video(self, script_data: Dict[str, Any], scene_video_paths: List[str]) -> str:
        """
        Ghép toàn bộ video cảnh quay và lồng giọng đọc tiếng Việt theo từng phân cảnh.
        """
        scenes = script_data.get("scenes", [])
        if not scenes:
            raise ValueError("Kịch bản không có phân cảnh (scenes).")

        final_clips = []
        safe_title = "".join(c for c in script_data.get("title", "ai_video") if c.isalnum() or c in (' ', '_', '-')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:35]
        output_final_path = settings.VIDEOS_DIR / f"final_{safe_title}.mp4"

        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            narration = scene.get("narration_vi", "")
            
            # 1. Tạo audio giọng đọc cho phân cảnh
            audio_path = settings.TEMP_DIR / f"audio_scene_{scene_num}.mp3"
            if narration:
                await self.generate_speech(narration, str(audio_path))
            
            # 2. Xử lý video clip của phân cảnh
            video_clip_path = scene_video_paths[idx] if idx < len(scene_video_paths) else scene_video_paths[-1]
            clip = VideoFileClip(video_clip_path)

            if os.path.exists(audio_path):
                audio_clip = AudioFileClip(str(audio_path))
                target_duration = audio_clip.duration + 0.5 # thêm 0.5s nghỉ giữa các cảnh

                # Điều chỉnh độ dài video cho khớp chính xác với giọng đọc
                if clip.duration < target_duration:
                    loop_count = int(target_duration // clip.duration) + 1
                    try:
                        clip = clip.loop(n=loop_count)
                    except AttributeError:
                        from moviepy.video.fx import Loop
                        clip = clip.with_effects([Loop(n=loop_count)])

                # Cắt đúng độ dài target_duration
                if hasattr(clip, "subclipped"):
                    clip = clip.subclipped(0, target_duration)
                else:
                    clip = clip.subclip(0, target_duration)

                # Gắn audio
                if hasattr(clip, "with_audio"):
                    clip = clip.with_audio(audio_clip)
                else:
                    clip = clip.set_audio(audio_clip)

            final_clips.append(clip)

        # 3. Nối các cảnh lại thành video hoàn chỉnh
        print("[*] Đang ghép các phân cảnh thành video cuối cùng...")
        final_video = concatenate_videoclips(final_clips, method="compose")
        
        final_video.write_videofile(
            str(output_final_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None
        )

        # Đóng tài nguyên clip
        for c in final_clips:
            c.close()
        final_video.close()

        print(f"[+] Xuất video thành công: {output_final_path}")
        return str(output_final_path)

if __name__ == "__main__":
    processor = VideoProcessor()
    print("VideoProcessor module initialized.")
