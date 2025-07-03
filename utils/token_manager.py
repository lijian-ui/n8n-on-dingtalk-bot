import time
import logging
from alibabacloud_dingtalk.oauth2_1_0.client import Client as DingTalkOAuthClient
from alibabacloud_dingtalk.oauth2_1_0 import models as oauth_models
from alibabacloud_tea_openapi import models as open_api_models

logger = logging.getLogger(__name__)

class TokenManager:
    """钉钉Access Token管理器"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._token_cache = {"token": None, "expire": 0}
    
    def get_token(self) -> str:
        """
        获取access_token，带本地缓存，2小时有效，提前200秒刷新
        :return: access_token字符串，获取失败返回None
        """
        now = time.time()
        
        # 检查缓存是否有效
        if self._token_cache["token"] and now < self._token_cache["expire"]:
            logger.debug("使用缓存的access_token")
            return self._token_cache["token"]
        
        # 重新获取token
        logger.info("重新获取access_token")
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        
        client = DingTalkOAuthClient(config)
        request = oauth_models.GetAccessTokenRequest(
            app_key=self.client_id,
            app_secret=self.client_secret
        )
        
        try:
            response = client.get_access_token(request)
            token = getattr(response.body, "access_token", None)
            expire_in = getattr(response.body, "expire_in", 7200)
            
            if token:
                self._token_cache["token"] = token
                self._token_cache["expire"] = now + expire_in - 200  # 提前200秒刷新
                logger.info("access_token获取成功")
                return token
            else:
                logger.error("获取access_token失败：响应中没有token")
                return None
                
        except Exception as err:
            logger.error(f"获取access_token异常: {err}")
            return None
    
    def clear_cache(self):
        """清除token缓存"""
        self._token_cache = {"token": None, "expire": 0}
        logger.info("已清除token缓存") 