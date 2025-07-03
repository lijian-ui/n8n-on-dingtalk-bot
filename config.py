import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # 钉钉应用配置
    CLIENT_ID = os.getenv('DINGTALK_CLIENT_ID', '')
    CLIENT_SECRET = os.getenv('DINGTALK_CLIENT_SECRET', '')
    ROBOT_CODE = os.getenv('DINGTALK_ROBOT_CODE', '')
    
    # n8n Webhook配置
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
    N8N_API_KEY = os.getenv('N8N_API_KEY', '')  # 如果需要认证
    N8N_WEBHOOK_TIMEOUT = int(os.getenv('N8N_WEBHOOK_TIMEOUT', '30'))
    
    # 机器人配置
    BOT_NAME = os.getenv('BOT_NAME', 'AI助手')
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        required_fields = [
            'CLIENT_ID', 'CLIENT_SECRET', 'ROBOT_CODE', 'N8N_WEBHOOK_URL'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必要的配置项: {', '.join(missing_fields)}")
        
        return True 