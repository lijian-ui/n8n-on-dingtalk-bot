import logging
import asyncio
from typing import Optional
import dingtalk_stream
from dingtalk_stream import AckMessage

from utils.token_manager import TokenManager
from services.ai_service import AIService
from services.dingtalk_service import DingTalkService
from config import Config

logger = logging.getLogger(__name__)

class AIChatbotHandler(dingtalk_stream.ChatbotHandler):
    """AI聊天机器人处理器"""
    
    def __init__(self, config: Config):
        super(dingtalk_stream.ChatbotHandler, self).__init__()
        self.config = config
        self.token_manager = TokenManager(config.CLIENT_ID, config.CLIENT_SECRET)
        self.ai_service = AIService(config.N8N_WEBHOOK_URL, config.N8N_API_KEY)
        self.dingtalk_service = DingTalkService(config.ROBOT_CODE)
    
    async def process(self, callback: dingtalk_stream.CallbackMessage):
        """
        处理钉钉消息回调
        :param callback: 回调消息对象
        :return: 处理结果
        """
        try:
            # 解析消息
            incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
            
            # 提取消息内容
            user_message = self._extract_user_message(incoming_message)
            if not user_message:
                logger.warning("无法提取用户消息内容")
                return AckMessage.STATUS_OK, 'OK'
            
            # 获取用户信息
            user_id = getattr(incoming_message, 'sender_staff_id', None)
            user_name = getattr(incoming_message, 'sender_nick', None)
            conversation_id = incoming_message.conversation_id
            
            logger.info(f"收到用户消息: {user_name}({user_id}): {user_message}")
            
            # 异步处理AI回复
            asyncio.create_task(self._process_ai_response(
                user_message, user_id, user_name, conversation_id
            ))
            
            return AckMessage.STATUS_OK, 'OK'
            
        except Exception as e:
            logger.error(f"处理消息异常: {e}")
            return AckMessage.STATUS_OK, 'OK'  # 返回OK避免重试
    
    def _extract_user_message(self, message) -> Optional[str]:
        """
        从钉钉消息中提取用户输入内容
        :param message: 钉钉消息对象
        :return: 用户消息内容
        """
        try:
            # 获取消息内容
            text_content = getattr(getattr(message, 'text', None), 'content', '').strip()
            
            # 移除@机器人的部分
            if text_content.startswith('@'):
                # 查找第一个空格，移除@部分
                space_index = text_content.find(' ')
                if space_index > 0:
                    text_content = text_content[space_index:].strip()
            
            return text_content if text_content else None
            
        except Exception as e:
            logger.error(f"提取用户消息异常: {e}")
            return None
    
    async def _process_ai_response(self, user_message: str, user_id: str, 
                                 user_name: str, conversation_id: str):
        """
        异步处理AI回复
        :param user_message: 用户消息
        :param user_id: 用户ID
        :param user_name: 用户名
        :param conversation_id: 会话ID
        """
        try:
            # 调用AI服务获取回复
            ai_response = await self.ai_service.get_ai_response(
                user_message, user_id, conversation_id
            )
            
            if not ai_response:
                logger.error("获取AI回复失败")
                await self._send_error_message(conversation_id, user_name)
                return
            
            # 获取access_token
            access_token = self.token_manager.get_token()
            if not access_token:
                logger.error("获取access_token失败")
                await self._send_error_message(conversation_id, user_name)
                return
            
            # 格式化并发送Markdown消息
            title, content = self.dingtalk_service.format_markdown_content(
                ai_response, user_name
            )
            
            success = self.dingtalk_service.send_markdown_message(
                access_token, conversation_id, title, content
            )
            
            if success:
                logger.info(f"AI回复发送成功: {user_name}")
            else:
                logger.error(f"AI回复发送失败: {user_name}")
                await self._send_error_message(conversation_id, user_name)
                
        except Exception as e:
            logger.error(f"处理AI回复异常: {e}")
            await self._send_error_message(conversation_id, user_name)
    
    async def _send_error_message(self, conversation_id: str, user_name: str):
        """
        发送错误消息
        :param conversation_id: 会话ID
        :param user_name: 用户名
        """
        try:
            access_token = self.token_manager.get_token()
            if access_token:
                error_message = f"抱歉，我暂时无法回复您的问题，请稍后再试。"
                if user_name:
                    error_message = f"@{user_name} {error_message}"
                
                self.dingtalk_service.send_text_message(
                    access_token, conversation_id, error_message
                )
        except Exception as e:
            logger.error(f"发送错误消息异常: {e}")
    
    async def close(self):
        """关闭资源"""
        await self.ai_service.close() 
