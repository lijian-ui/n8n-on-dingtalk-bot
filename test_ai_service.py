#!/usr/bin/env python3
"""
AI服务测试脚本
用于测试n8n webhook连接和响应解析
"""

import asyncio
import logging
from services.ai_service import AIService
from config import Config

def setup_logger():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    )
    return logging.getLogger(__name__)

async def test_ai_service():
    """测试AI服务"""
    logger = setup_logger()
    
    # 验证配置
    try:
        Config.validate()
        logger.info("配置验证通过")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return
    
    # 创建AI服务
    ai_service = AIService(Config.N8N_WEBHOOK_URL, Config.N8N_API_KEY)
    
    # 测试消息
    test_messages = [
        "你好，请介绍一下你自己",
        "今天天气怎么样？",
        "请帮我写一个Python函数",
        "什么是人工智能？"
    ]
    
    logger.info("开始测试AI服务...")
    
    for i, message in enumerate(test_messages, 1):
        logger.info(f"\n--- 测试 {i}: {message} ---")
        
        try:
            # 调用AI服务
            response = await ai_service.get_ai_response(
                user_message=message,
                user_id="test_user_001",
                conversation_id="test_conversation_001"
            )
            
            if response:
                logger.info(f"✅ AI回复: {response}")
            else:
                logger.error("❌ 获取AI回复失败")
                
        except Exception as e:
            logger.error(f"❌ 测试异常: {e}")
        
        # 等待一下再发送下一个请求
        await asyncio.sleep(2)
    
    # 关闭服务
    await ai_service.close()
    logger.info("测试完成")

if __name__ == '__main__':
    asyncio.run(test_ai_service()) 