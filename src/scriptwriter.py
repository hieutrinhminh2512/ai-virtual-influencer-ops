import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
from config.settings import settings
from config.prompts import TECH_AI_NEWS_PROMPT

class ScriptWriter:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def generate_script(self, topic: str, duration: str = "1-2 phút (4 phân cảnh)") -> Dict[str, Any]:
        """
        Tạo kịch bản tin tức AI & Công nghệ dựa trên chủ đề yêu cầu.
        """
        if not self.api_key:
            print("[!] Chưa có GEMINI_API_KEY trong .env. Đang tự động sử dụng kịch bản tin tức AI mẫu để test quy trình...")
            return self._generate_mock_script(topic)

        prompt = TECH_AI_NEWS_PROMPT.format(topic=topic, duration=duration)
        
        # Thử sử dụng google-genai SDK mới nhất, nếu chưa có thì dùng requests
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
            )
            raw_text = response.text
        except Exception as e_genai:
            try:
                # Fallback to direct REST API call with gemini-3.8-flash
                import requests
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                res = requests.post(url, json=payload, timeout=60)
                res.raise_for_status()
                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e_rest:
                print(f"[!] Lỗi khi gọi Gemini API ({e_genai} / {e_rest}). Sử dụng kịch bản mẫu...")
                return self._generate_mock_script(topic)

        parsed_json = self._clean_and_parse_json(raw_text)
        
        # Lưu file kịch bản vào thư mục outputs/scripts/
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:30]
        script_file = settings.SCRIPTS_DIR / f"script_{safe_topic}.json"
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(parsed_json, f, ensure_ascii=False, indent=2)

        parsed_json["script_path"] = str(script_file)
        return parsed_json

    def _generate_mock_script(self, topic: str) -> Dict[str, Any]:
        """Tạo kịch bản mẫu chất lượng cao cho chế độ test thử nghiệm."""
        mock_data = {
            "title": f"Bản Tin AI 2026: {topic} - Cuộc Đua Công Nghệ Mới Nhất",
            "description": f"Tổng hợp tin tức công nghệ mới nhất về {topic}. Trí tuệ nhân tạo đang thay đổi thế giới với tốc độ chưa từng có.\n\n#AI #Technology #TechNews #Vietnam",
            "tags": ["AI", "Trí tuệ nhân tạo", "Công nghệ mới", "Gemini", "OpenAI", "Tech News", "Xu hướng 2026", "Shorts"],
            "scenes": [
                {
                    "scene_number": 1,
                    "narration_vi": "Chào mừng các bạn đến với bản tin công nghệ AI hôm nay. Cơn sốt trí tuệ nhân tạo đang bước sang một kỷ nguyên hoàn toàn mới.",
                    "visual_description": "Logo AI phát sáng công nghệ cao",
                    "image_prompt_en": "Cinematic shot of a glowing AI cybernetic neural brain, 8k resolution, futuristic laboratory, neon blue and purple dramatic lighting, photorealistic",
                    "video_motion_prompt_en": "Camera slowly pushes towards glowing neural core"
                },
                {
                    "scene_number": 2,
                    "narration_vi": "Các tập đoàn công nghệ hàng đầu vừa công bố những bước đột phá chưa từng có, tối ưu hóa năng suất lên gấp nhiều lần.",
                    "visual_description": "Trung tâm dữ liệu siêu máy tính thế hệ mới",
                    "image_prompt_en": "Massive supercomputer server room with fiber optic lasers, futuristic architecture, hyper-detailed, unreal engine 5 render, cinematic lighting",
                    "video_motion_prompt_en": "Drone flythrough between glowing server racks"
                },
                {
                    "scene_number": 3,
                    "narration_vi": "Tương lai công nghệ đang mở ra ngay trước mắt. Đừng quên bấm theo dõi để không bỏ lỡ những bước nhảy vọt tiếp theo của thời đại AI!",
                    "visual_description": "Hình ảnh robot tương lai kết nối con người",
                    "image_prompt_en": "Futuristic humanoid android standing in smart city at sunset, cinematic bokeh, 4k ultra realistic, cyber aesthetic",
                    "video_motion_prompt_en": "Robot turns head towards camera with subtle smile"
                }
            ]
        }
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')[:30]
        script_file = settings.SCRIPTS_DIR / f"script_mock_{safe_topic}.json"
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(mock_data, f, ensure_ascii=False, indent=2)
        mock_data["script_path"] = str(script_file)
        return mock_data

    def _clean_and_parse_json(self, text: str) -> Dict[str, Any]:
        """
        Làm sạch phản hồi từ Gemini và trích xuất JSON.
        """
        text = text.strip()
        # Loại bỏ markdown ```json ... ```
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        # Tìm chuỗi JSON đầu tiên bằng regex nếu văn bản có chứa thêm lời chào
        json_match = re.search(r'(\{[\s\S]*\})', text)
        if json_match:
            text = json_match.group(1)

        try:
            return json.loads(text)
        except json.JSONDecodeError as err:
            raise ValueError(f"Không thể phân tích phản hồi JSON từ Gemini: {err}\nVăn bản gốc:\n{text}")

if __name__ == "__main__":
    writer = ScriptWriter()
    # Test mẫu
    test_script = {
        "title": "OpenAI & Google chạy đua siêu AI mới nhất 2026",
        "description": "Cập nhật đột phá công nghệ mới...",
        "tags": ["AI", "Tech", "News"],
        "scenes": []
    }
    print("ScriptWriter module initialized.")
