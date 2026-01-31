import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import logging

class TelegramBot:
    def __init__(self, token, channel_id):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
        self.logger = logging.getLogger(__name__)

    async def send_news(self, summary, original_url, title):
        """
        Sends the Myanmar summary to the Telegram channel.
        Includes the original article link.
        """
        message = (
            f"<b>{title}</b>\n\n"
            f"{summary}\n\n"
            f"🔗 <a href='{original_url}'>Original Article</a>"
        )
        
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            return True
        except Exception as e:
            self.logger.error(f"Error sending message to Telegram: {e}")
            return False
