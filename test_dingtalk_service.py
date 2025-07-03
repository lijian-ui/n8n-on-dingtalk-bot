#!/usr/bin/env python3
"""
钉钉服务测试脚本
用于测试消息发送功能
"""

import logging
from utils.token_manager import TokenManager
from services.dingtalk_service import DingTalkService
from config import Config

def setup_logger():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    return logging.getLogger(__name__)

def test_dingtalk_service():
    """测试钉钉服务"""
    logger = setup_logger()
    
    # 验证配置
    try:
        Config.validate()
        logger.info("配置验证通过")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return
    
    # 创建Token管理器
    token_manager = TokenManager(Config.CLIENT_ID, Config.CLIENT_SECRET)
    
    # 创建钉钉服务
    dingtalk_service = DingTalkService(Config.ROBOT_CODE)
    
    # 获取access_token
    access_token = token_manager.get_token()
    if not access_token:
        logger.error("获取access_token失败")
        return
    
    logger.info("access_token获取成功")
    
    # 测试用的会话ID（需要替换为实际的群会话ID）
    test_conversation_id = "your_test_conversation_id_here"
    
    # 测试消息
    test_messages = [
        {
            "title": "🤖 测试消息",
            "content": "这是一条测试消息\n\n- 支持Markdown格式\n- 支持换行\n- 支持列表"
        },
        {
            "title": "📝 代码示例",
            "content": "```python\nprint('Hello, World!')\n```\n\n这是一个Python代码示例。"
        },
        {
            "title": "🔗 链接测试",
            "content": "这是一个链接：[钉钉开放平台](https://open-dev.dingtalk.com)"
        }
    ]
    
    logger.info("开始测试钉钉服务...")
    
    for i, message in enumerate(test_messages, 1):
        logger.info(f"\n--- 测试 {i}: {message['title']} ---")
        
        try:
            # 发送Markdown消息
            success = dingtalk_service.send_markdown_message(
                access_token=access_token,
                open_conversation_id=test_conversation_id,
                title=message['title'],
                content=message['content']
            )
            
            if success:
                logger.info(f"✅ 消息发送成功: {message['title']}")
            else:
                logger.error(f"❌ 消息发送失败: {message['title']}")
                
        except Exception as e:
            logger.error(f"❌ 测试异常: {e}")
    
    logger.info("测试完成")
    logger.info("\n注意：请将 test_conversation_id 替换为实际的群会话ID进行测试")

if __name__ == '__main__':
    test_dingtalk_service() 