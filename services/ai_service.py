import json
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import re
from config import Config

logger = logging.getLogger(__name__)

class AIService:
    """AI服务类，负责调用n8n webhook获取AI回复"""
    
    def __init__(self, webhook_url: str, api_key: str = None):
        self.webhook_url = webhook_url
        self.api_key = api_key
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def get_ai_response(self, user_message: str, user_id: str = None, 
                            conversation_id: str = None) -> Optional[str]:
        """
        调用n8n webhook获取AI回复
        :param user_message: 用户消息内容
        :param user_id: 用户ID
        :param conversation_id: 会话ID
        :return: AI回复内容，失败返回None
        """
        session = await self._get_session()
        
        # 构建请求数据
        payload = {
            "message": user_message,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # 如果配置了API key，添加到请求头
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            logger.info(f"调用n8n webhook: {self.webhook_url}")
            logger.debug(f"请求数据: {payload}")
            
            async with session.post(
                self.webhook_url,
                json=payload,
                headers=headers
            ) as response:
                
                if response.status == 200:
                    response_data = await response.json()
                    logger.info("n8n webhook调用成功")
                    logger.info(f"收到的原始响应数据: {response_data}")
                    
                    # 解析响应数据，根据n8n的实际返回格式调整
                    ai_response = self._parse_ai_response(response_data)
                    return ai_response
                else:
                    error_text = await response.text()
                    logger.error(f"n8n webhook调用失败: HTTP {response.status}, {error_text}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"网络请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"获取AI回复异常: {e}")
            return None
    
    def _parse_ai_response(self, response_data: Dict[str, Any]) -> Optional[str]:
        """
        解析n8n返回的AI回复数据
        根据实际的n8n webhook返回格式调整此方法
        """
        try:
            data_to_parse = response_data
            # n8n webhook 经常返回包含单个元素的列表
            if isinstance(response_data, list) and response_data:
                data_to_parse = response_data[0]

            # 常见的响应格式示例，请根据实际情况调整
            if isinstance(data_to_parse, dict):
                # 格式1: {"response": "AI回复内容"}
                if "response" in data_to_parse:
                    return data_to_parse["response"]
                
                # 格式2: {"data": {"reply": "AI回复内容"}}
                elif "data" in data_to_parse and isinstance(data_to_parse["data"], dict):
                    if "reply" in data_to_parse["data"]:
                        return data_to_parse["data"]["reply"]
                
                # 格式3: {"message": "AI回复内容"}
                elif "message" in data_to_parse:
                    return data_to_parse["message"]
                
                # 格式4: n8n Respond to Webhook 节点的常见格式 {"output": "AI回复内容"}
                elif "output" in data_to_parse:
                    return data_to_parse["output"]

                # 格式5: 直接返回字符串内容
                elif "content" in data_to_parse:
                    return data_to_parse["content"]
            
            # 如果响应是字符串，直接返回
            elif isinstance(data_to_parse, str):
                return data_to_parse
            
            logger.warning(f"无法解析AI响应格式: {response_data}")
            return None
            
        except Exception as e:
            logger.error(f"解析AI响应异常: {e}")
            return None
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("AI服务HTTP会话已关闭")

    async def stream_reply(self, incoming_message) -> str:
        """
        伪流式返回n8n回复内容，供AI卡片handler实时更新。
        :param incoming_message: ChatbotMessage对象
        :yield: AI回复内容分段
        """
        user_message = getattr(getattr(incoming_message, 'text', None), 'content', '')
        user_id = getattr(incoming_message, 'sender_staff_id', None)
        conversation_id = getattr(incoming_message, 'conversation_id', None)
        try:
            ai_response = await asyncio.wait_for(
                self.get_ai_response(user_message, user_id, conversation_id),
                timeout=Config.N8N_WEBHOOK_TIMEOUT  # 支持env配置
            )
            if not ai_response:
                logger.warning(f"n8n webhook返回空内容，user_message={user_message}, user_id={user_id}, conversation_id={conversation_id}")
                yield "AI回复为空，请稍后重试。"
                return
        except asyncio.TimeoutError:
            logger.error(f"n8n webhook调用超时（30秒），user_message={user_message}, user_id={user_id}, conversation_id={conversation_id}")
            yield "AI思考时间较长，请稍后再试。"
            return
        except Exception as e:
            logger.error(f"n8n webhook调用异常: {e}, user_message={user_message}, user_id={user_id}, conversation_id={conversation_id}")
            yield f"AI服务异常：{e}"
            return
        # 简单按句号、换行分段模拟流式
        segments = re.split(r'(。|！|？|\n)', ai_response)
        buffer = ''
        for seg in segments:
            buffer += seg
            if seg in ['。', '！', '？', '\n']:
                yield buffer
                buffer = ''
        if buffer:
            yield buffer 
