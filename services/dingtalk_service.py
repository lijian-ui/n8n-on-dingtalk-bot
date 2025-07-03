import json
import logging
from typing import Optional
from alibabacloud_dingtalk.robot_1_0.client import Client as DingTalkRobotClient
from alibabacloud_dingtalk.robot_1_0 import models as robot_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

logger = logging.getLogger(__name__)

class DingTalkService:
    """钉钉服务类，负责发送消息到钉钉群"""
    
    def __init__(self, robot_code: str):
        self.robot_code = robot_code
        self.config = open_api_models.Config()
        self.config.protocol = 'https'
        self.config.region_id = 'central'
        self.client = DingTalkRobotClient(self.config)
    
    def send_markdown_message(self, access_token: str, open_conversation_id: str, 
                            title: str, content: str) -> bool:
        """
        发送Markdown消息到钉钉群
        :param access_token: 钉钉access_token
        :param open_conversation_id: 群会话ID
        :param title: 消息标题
        :param content: Markdown内容
        :return: 发送是否成功
        """
        try:
            # 构建Markdown消息参数
            msg_param = json.dumps({
                "title": title,
                "text": content
            }, ensure_ascii=False)
            
            # 设置请求头
            headers = robot_models.OrgGroupSendHeaders()
            headers.x_acs_dingtalk_access_token = access_token
            
            # 构建请求
            request = robot_models.OrgGroupSendRequest(
                msg_param=msg_param,
                msg_key="sampleMarkdown",  # Markdown消息类型
                open_conversation_id=open_conversation_id,
                robot_code=self.robot_code
            )
            
            # 发送消息
            response = self.client.org_group_send_with_options(
                request,
                headers,
                util_models.RuntimeOptions()
            )
            
            logger.info("Markdown消息发送成功")
            logger.debug(f"发送响应: {response}")
            return True
            
        except Exception as err:
            logger.error(f"发送Markdown消息失败: {err}")
            return False
    
    def send_text_message(self, access_token: str, open_conversation_id: str, 
                         content: str) -> bool:
        """
        发送文本消息到钉钉群
        :param access_token: 钉钉access_token
        :param open_conversation_id: 群会话ID
        :param content: 文本内容
        :return: 发送是否成功
        """
        try:
            # 构建文本消息参数
            msg_param = json.dumps({
                "content": content
            }, ensure_ascii=False)
            
            # 设置请求头
            headers = robot_models.OrgGroupSendHeaders()
            headers.x_acs_dingtalk_access_token = access_token
            
            # 构建请求
            request = robot_models.OrgGroupSendRequest(
                msg_param=msg_param,
                msg_key="sampleText",  # 文本消息类型
                open_conversation_id=open_conversation_id,
                robot_code=self.robot_code
            )
            
            # 发送消息
            response = self.client.org_group_send_with_options(
                request,
                headers,
                util_models.RuntimeOptions()
            )
            
            logger.info("文本消息发送成功")
            logger.debug(f"发送响应: {response}")
            return True
            
        except Exception as err:
            logger.error(f"发送文本消息失败: {err}")
            return False
    
    def format_markdown_content(self, ai_response: str, user_name: str = None) -> tuple:
        """
        格式化AI回复为Markdown内容
        :param ai_response: AI回复内容
        :param user_name: 用户名
        :return: (title, content) 元组
        """
        title = f"🤖 {self._get_bot_name()} 回复"
        if user_name:
            title += f" @{user_name}"
        
        # 格式化内容，确保Markdown格式正确
        content = ai_response.strip()
        
        # 如果内容太长，进行截断
        max_length = 2000  # 钉钉Markdown消息长度限制
        if len(content) > max_length:
            content = content[:max_length-3] + "..."
        
        return title, content
    
    def _get_bot_name(self) -> str:
        """获取机器人名称"""
        return "AI助手"  # 可以从配置中获取 