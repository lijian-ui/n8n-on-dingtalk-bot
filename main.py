#!/usr/bin/env python3
"""
钉钉AI机器人主程序
功能：接收钉钉消息 -> 调用n8n Webhook获取AI回复 -> 发送Markdown消息到钉钉群
"""

import logging
import signal
import sys
import asyncio
from typing import Optional

import dingtalk_stream

from config import Config
from services.ai_service import AIService
from handlers.ai_card_handler import AICardHandler

# 全局变量
client: Optional[dingtalk_stream.DingTalkStreamClient] = None
handler: Optional[AICardHandler] = None
ai_service: Optional[AIService] = None

def setup_logger():
    """设置日志配置"""
    logger = logging.getLogger()
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'
        )
    )
    
    logger.addHandler(console_handler)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    return logger

async def shutdown():
    global ai_service
    if ai_service:
        await ai_service.close()
        logging.getLogger(__name__).info("AIService已关闭")

def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭"""
    logger = logging.getLogger(__name__)
    logger.info(f"收到信号 {signum}，开始优雅关闭...")
    
    if client:
        logger.info("关闭钉钉流式客户端...")
        client.stop()
    
    if handler:
        logger.info("关闭AI处理器...")
        asyncio.create_task(handler.close())
    
    # 新增：关闭AIService
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(shutdown())
    else:
        loop.run_until_complete(shutdown())
    
    logger.info("程序已关闭")
    sys.exit(0)

def validate_config():
    """验证配置"""
    try:
        Config.validate()
        logger = logging.getLogger(__name__)
        logger.info("配置验证通过")
        return True
    except ValueError as e:
        print(f"配置错误: {e}")
        print("\n请检查以下环境变量:")
        print("- DINGTALK_CLIENT_ID: 钉钉应用的AppKey")
        print("- DINGTALK_CLIENT_SECRET: 钉钉应用的AppSecret")
        print("- DINGTALK_ROBOT_CODE: 机器人的RobotCode")
        print("- N8N_WEBHOOK_URL: n8n webhook的URL地址")
        print("\n您可以在 .env 文件中设置这些变量，或者直接在环境变量中设置。")
        return False

def main():
    """主函数"""
    global client, handler, ai_service
    
    # 设置日志
    logger = setup_logger()
    logger.info("启动钉钉AI机器人...")
    
    # 验证配置
    if not validate_config():
        sys.exit(1)
    
    try:
        # 创建钉钉流式客户端
        credential = dingtalk_stream.Credential(Config.CLIENT_ID, Config.CLIENT_SECRET)
        client = dingtalk_stream.DingTalkStreamClient(credential)
        
        # 创建AI服务
        ai_service = AIService(Config.N8N_WEBHOOK_URL, Config.N8N_API_KEY)
        # 创建AI卡片处理器
        handler = AICardHandler(ai_service)
        
        # 注册消息处理器
        client.register_callback_handler(
            dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
            handler
        )
        
        # 设置信号处理器
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("钉钉AI机器人启动成功，开始监听消息...")
        logger.info(f"机器人名称: {Config.BOT_NAME}")
        logger.info(f"n8n Webhook: {Config.N8N_WEBHOOK_URL}")
        
        # 启动客户端
        client.start_forever()
        
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"程序运行异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 