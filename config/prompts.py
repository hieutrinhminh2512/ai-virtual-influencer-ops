TECH_AI_NEWS_PROMPT = """
Bạn là một chuyên gia sáng tạo nội dung YouTube hàng đầu về ngách "Tin tức công nghệ & Xu hướng AI tóm tắt" (Tech & AI News).
Nhiệm vụ của bạn là tạo kịch bản video hấp dẫn, kịch tính, ngắn gọn, súc tích và chuẩn SEO YouTube dựa trên chủ đề được cung cấp.

Chủ đề: {topic}
Thời lượng dự kiến: {duration} (khoảng 3 - 6 phân cảnh, phù hợp làm video tin tức nhanh hoặc Shorts/Video ngắn 1-3 phút).

Hãy trả về DUY NHẤT một chuỗi JSON hợp lệ với cấu trúc sau:
{{
  "title": "Tiêu đề video giật tít, hấp dẫn, chuẩn SEO YouTube (tiếng Việt)",
  "description": "Đoạn mô tả YouTube hoàn chỉnh, kèm tóm tắt nội dung và hashtag liên quan",
  "tags": ["AI", "Trí tuệ nhân tạo", "Công nghệ mới", "Gemini", "OpenAI", ... ít nhất 8 tags chuẩn SEO],
  "scenes": [
    {{
      "scene_number": 1,
      "narration_vi": "Lời bình tiếng Việt đọc truyền cảm, hấp dẫn, đóng vai trò dẫn dắt người xem...",
      "visual_description": "Mô tả cảnh quay bằng tiếng Việt để người duyệt hiểu...",
      "image_prompt_en": "Detailed cinematic prompt in English for Google Flow (Imagen 3), highly detailed, 4k, photorealistic, cybernetic, hyper-realistic, dramatic lighting...",
      "video_motion_prompt_en": "Camera slowly zooms into the glowing futuristic AI neural core, cinematic motion, smooth 60fps"
    }},
    ...
  ]
}}

LƯU Ý:
1. `narration_vi` phải viết bằng văn phong tự nhiên, cuốn hút, phát âm chuẩn cho giọng đọc TTS tiếng Việt.
2. `image_prompt_en` và `video_motion_prompt_en` viết hoàn toàn bằng TIẾNG ANH, chi tiết và mô tả phong cách điện ảnh (cinematic, 8k, unreal engine 5, dramatic lighting, futuristic tech aesthetic) để đưa vào Google Flow (Imagen & Veo).
3. Đảm bảo trả về JSON thuần túy, không bọc trong ```json ``` nếu có thể, hoặc đảm bảo cú pháp JSON hoàn toàn hợp lệ.
"""
