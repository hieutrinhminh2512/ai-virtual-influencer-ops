import os
import asyncio
from typing import Dict, Any, Callable, Optional
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config.settings import settings

class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.app = None
        self.approval_callback: Optional[Callable] = None
        self.pending_tasks: Dict[str, Dict[str, Any]] = {}

    def set_approval_callback(self, callback: Callable):
        """Đăng ký hàm xử lý khi người dùng bấm Duyệt (upload YouTube)."""
        self.approval_callback = callback

    async def initialize(self):
        if not self.token:
            print("[!] TELEGRAM_BOT_TOKEN chưa được cấu hình. Tính năng Telegram Bot sẽ tạm tắt.")
            return False

        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CallbackQueryHandler(self._handle_callback))
        await self.app.initialize()
        await self.app.start()
        print("[+] Telegram Bot đã khởi chạy và sẵn sàng nhận lệnh.")
        return True

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            f"🤖 *Xin chào! Tôi là trợ lý quản lý kênh YouTube tự động.*\n"
            f"ID cuộc trò chuyện của bạn là: `{chat_id}`\n\n"
            f"Hãy dán Chat ID này vào file `.env` (TELEGRAM_CHAT_ID={chat_id}) để nhận thông báo duyệt video.",
            parse_mode="Markdown"
        )

    async def send_approval_request(self, task_id: str, video_path: str, metadata: Dict[str, Any]):
        """
        Gửi video hoặc thông báo kèm nút Duyệt / Huỷ lên Telegram.
        """
        if not self.token or not self.chat_id:
            print("[!] Chưa điền TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID, bỏ qua gửi Telegram.")
            return

        self.pending_tasks[task_id] = {
            "video_path": video_path,
            "metadata": metadata
        }

        title = metadata.get("title", "Video mới")
        desc = metadata.get("description", "")[:200]
        tags = ", ".join(metadata.get("tags", [])[:5])

        caption = (
            f"🎬 *VIDEO MỚI CHỜ BẠN DUYỆT*\n\n"
            f"📌 *Tiêu đề:* {title}\n"
            f"📝 *Mô tả:* {desc}...\n"
            f"🏷 *Tags:* {tags}\n\n"
            f"Vui lòng chọn thao tác bên dưới:"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Duyệt & Đăng lên YouTube", callback_data=f"approve_{task_id}"),
                InlineKeyboardButton("❌ Huỷ / Làm lại", callback_data=f"reject_{task_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            bot = self.app.bot if self.app else None
            if not bot:
                from telegram import Bot
                bot = Bot(token=self.token)

            # Nếu file < 50MB gửi video trực tiếp, nếu lớn hơn gửi tin nhắn thông báo
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            if file_size_mb <= 45:
                with open(video_path, 'rb') as vf:
                    await bot.send_video(
                        chat_id=self.chat_id,
                        video=vf,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
            else:
                await bot.send_message(
                    chat_id=self.chat_id,
                    text=f"{caption}\n\n*(File video {file_size_mb:.1f}MB đã lưu tại: {video_path})*",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            print(f"[+] Đã gửi yêu cầu duyệt video sang Telegram chat ID: {self.chat_id}")
        except Exception as e:
            print(f"[!] Lỗi khi gửi Telegram: {e}")

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        if data.startswith("approve_"):
            task_id = data.replace("approve_", "")
            task = self.pending_tasks.get(task_id)
            await query.edit_message_caption(caption="⏳ *Đang đăng tải video lên kênh YouTube của bạn... Vui lòng chờ.*", parse_mode="Markdown")
            
            if self.approval_callback and task:
                try:
                    video_url = await self.approval_callback(task["video_path"], task["metadata"])
                    await query.edit_message_caption(
                        caption=f"🎉 *ĐÃ ĐĂNG THÀNH CÔNG LÊN YOUTUBE!*\n\n🔗 Xem video tại: {video_url}",
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    await query.edit_message_caption(
                        caption=f"❌ *Lỗi khi đăng lên YouTube:* {str(e)}",
                        parse_mode="Markdown"
                    )
        elif data.startswith("reject_"):
            task_id = data.replace("reject_", "")
            self.pending_tasks.pop(task_id, None)
            await query.edit_message_caption(caption="❌ *Video đã bị huỷ bỏ.*", parse_mode="Markdown")

telegram_notifier = TelegramNotifier()
