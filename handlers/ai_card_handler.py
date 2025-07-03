import os
import asyncio
import json
from dingtalk_stream import AckMessage, ChatbotHandler, CallbackMessage, ChatbotMessage, AICardReplier
from loguru import logger

# 这里可根据需要引入 n8n-on-dingtalk 的 ai_service/dingtalk_service 等

class AICardHandler(ChatbotHandler):
    def __init__(self, ai_service):
        super().__init__()
        self.ai_service = ai_service
        # 可扩展缓存、会话等

    async def process(self, callback_msg: CallbackMessage):
        logger.debug(callback_msg)
        incoming_message = ChatbotMessage.from_dict(callback_msg.data)
        logger.info(f"收到用户消息: {incoming_message}")
        task = asyncio.create_task(self._process_async(incoming_message))
        task.add_done_callback(self._handle_task_exception)
        return AckMessage.STATUS_OK, "OK"

    def _handle_task_exception(self, task):
        try:
            exception = task.exception()
            if exception:
                logger.error(f"异步处理任务异常: {exception}")
        except Exception as e:
            logger.error(f"处理异步任务异常时出错: {e}")

    async def _process_async(self, incoming_message: ChatbotMessage):
        try:
            if incoming_message.message_type != "text":
                self.reply_text("对不起，我目前只支持文字消息~", incoming_message)
                return

            # 统一读取卡片模板ID
            card_template_id = os.getenv("DINGTALK_AI_CARD_TEMPLATE_ID")
            content_key = "content"
            card_data = {content_key: ""}
            card_instance = AICardReplier(self.dingtalk_client, incoming_message)
            # 投放卡片
            card_instance_id = card_instance.create_and_send_card(card_template_id, card_data, callback_type="STREAM")
            # 流式更新卡片内容
            buffer = ""
            async for content_value in self.ai_service.stream_reply(incoming_message):
                buffer += content_value
                card_instance.streaming(
                    card_instance_id,
                    content_key=content_key,
                    content_value=buffer,
                    append=False,
                    finished=False,
                    failed=False,
                )
            # 最后一次 finished=True
            card_instance.streaming(
                card_instance_id,
                content_key=content_key,
                content_value=buffer,
                append=False,
                finished=True,
                failed=False,
            )
        except Exception as e:
            logger.exception(f"处理消息时发生未知错误: {e}") 