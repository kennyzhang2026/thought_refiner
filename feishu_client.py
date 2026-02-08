"""
飞书多维表格 API 客户端模块
用于将对话记录保存到飞书多维表格
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
import uuid

# 配置日志
logger = logging.getLogger(__name__)

class FeishuClient:
    """飞书多维表格 API 客户端"""
    
    # 飞书API端点
    TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    BITABLE_URL = "https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    def __init__(self, app_id: str, app_secret: str, app_token: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_token = app_token
        self._access_token = None
        self._token_expiry = 0
        self.max_retries = 3
        self.retry_delay = 1
        logger.info("飞书客户端初始化完成")
    
    def _get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        current_time = time.time()
        if (not force_refresh and self._access_token and current_time < self._token_expiry - 300):
            return self._access_token
        
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        headers = {"Content-Type": "application/json; charset=utf-8"}
        
        try:
            response = requests.post(self.TOKEN_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    self._access_token = data.get("tenant_access_token")
                    self._token_expiry = current_time + 7200
                    return self._access_token
        except Exception as e:
            logger.error(f"获取令牌错误: {e}")
        return None
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        for attempt in range(self.max_retries):
            try:
                token = self._get_tenant_access_token()
                if not token: return None
                
                headers = kwargs.get('headers', {})
                headers['Authorization'] = f'Bearer {token}'
                kwargs['headers'] = headers
                
                response = requests.request(method, url, **kwargs)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0: return data
            except Exception:
                time.sleep(self.retry_delay)
        return None
    
    def add_record_to_bitable(self, table_id: str, fields: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        if isinstance(fields, dict): fields_list = [fields]
        else: fields_list = fields
        
        url = self.BITABLE_URL.format(app_token=self.app_token, table_id=table_id)
        payload = {"records": [{"fields": field_data} for field_data in fields_list]}
        
        response_data = self._make_request_with_retry(
            method="POST",
            url=url + "/batch_create",
            headers={"Content-Type": "application/json; charset=utf-8"},
            json=payload,
            timeout=30
        )
        
        if response_data:
            return {"success": True, "error": None}
        return {"success": False, "error": "API 请求失败"}
    
    def format_chat_record(self, user_question: str, ai_answer: str, model_used: str = "unknown") -> List[Dict[str, Any]]:
        session_id = str(uuid.uuid4())
        current_time = int(time.time() * 1000)
        
        user_record = {
            "sectionID": session_id,
            "时间": current_time,
            "role": "user",
            "user_question": user_question,
            "AI_answer": "",
            "tags": ["AI助手存档"]
        }
        
        ai_record = {
            "sectionID": session_id,
            "时间": current_time,
            "role": "assistant",
            "user_question": "",
            "AI_answer": f"{ai_answer}\n\n---\n*使用模型: {model_used}*",
            "tags": [model_used]
        }
        return [user_record, ai_record]
