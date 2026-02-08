"""
DeepSeek API 客户端模块
使用 OpenAI SDK 兼容模式调用 DeepSeek API
"""

import openai
from typing import Optional, Dict, Any
import logging

# 配置日志
logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API 客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: DeepSeek API Key
            base_url: API 基础 URL，默认为 DeepSeek 官方 API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        
        if api_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化 OpenAI 客户端"""
        try:
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info("DeepSeek 客户端初始化成功")
        except Exception as e:
            logger.error(f"DeepSeek 客户端初始化失败: {e}")
            self.client = None
    
    def get_response(self, 
                    message: str, 
                    model: str = "deepseek-chat",
                    system_prompt: Optional[str] = None,
                    temperature: float = 0.7,
                    max_tokens: int = 2000) -> Dict[str, Any]:
        """
        获取 DeepSeek 的文本回复
        
        Args:
            message: 用户输入的消息
            model: 使用的模型，默认为 deepseek-chat
            system_prompt: 系统提示词
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成 token 数
            
        Returns:
            Dict 包含响应内容或错误信息
        """
        if not self.client:
            return {
                "success": False,
                "error": "DeepSeek 客户端未初始化，请检查 API Key",
                "content": None
            }
        
        try:
            # 构建消息列表
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            # 提取回复内容
            content = response.choices[0].message.content
            
            logger.info(f"DeepSeek 响应成功，token 使用: {response.usage.total_tokens}")
            
            return {
                "success": True,
                "content": content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except openai.AuthenticationError as e:
            logger.error(f"DeepSeek 认证失败: {e}")
            return {
                "success": False,
                "error": f"API Key 认证失败: {str(e)}",
                "content": None
            }
        except openai.RateLimitError as e:
            logger.error(f"DeepSeek 请求频率限制: {e}")
            return {
                "success": False,
                "error": f"请求频率超限: {str(e)}",
                "content": None
            }
        except openai.APIConnectionError as e:
            logger.error(f"DeepSeek 连接错误: {e}")
            return {
                "success": False,
                "error": f"网络连接错误: {str(e)}",
                "content": None
            }
        except openai.APIError as e:
            logger.error(f"DeepSeek API 错误: {e}")
            return {
                "success": False,
                "error": f"API 调用错误: {str(e)}",
                "content": None
            }
        except Exception as e:
            logger.error(f"DeepSeek 未知错误: {e}")
            return {
                "success": False,
                "error": f"未知错误: {str(e)}",
                "content": None
            }


def get_deepseek_response(message: str, api_key: str, **kwargs) -> Dict[str, Any]:
    """
    快速获取 DeepSeek 响应的便捷函数
    
    Args:
        message: 用户输入的消息
        api_key: DeepSeek API Key
        **kwargs: 其他参数传递给 DeepSeekClient.get_response
        
    Returns:
        Dict 包含响应内容或错误信息
    """
    client = DeepSeekClient(api_key)
    return client.get_response(message, **kwargs)


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 测试函数
    def test_deepseek():
        """测试 DeepSeek 客户端"""
        print("=== DeepSeek 客户端测试 ===")
        
        # 使用测试 API Key（实际使用时需要替换为真实 Key）
        test_api_key = "test_key_123"
        
        # 创建客户端
        client = DeepSeekClient(test_api_key)
        
        # 测试未初始化情况
        print("1. 测试未初始化客户端:")
        result = client.get_response("你好")
        print(f"   结果: {result}")
        
        # 测试错误处理
        print("\n2. 测试错误处理:")
        # 这里会返回认证错误，因为使用了测试 Key
        result = client.get_response("你好")
        print(f"   结果: {result.get('error', '无错误')}")
        
        print("\n=== 测试完成 ===")
    
    test_deepseek()