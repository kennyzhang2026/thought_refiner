# 🚀 技能复用指南

> 如何将本项目的开发技能应用到新项目中

---

## 📖 理解技能文档的作用

### DEVELOPMENT_SKILLS.md 是什么？

这是一份**知识库文档**，记录了：
- ✅ 开发模式和最佳实践
- ✅ 可复用的代码片段
- ✅ 常见问题的解决方案
- ✅ 架构设计思路

### 它不是什么？

- ❌ 不是可以直接 `import` 的 Python 包
- ❌ 不是可以自动应用的配置文件
- ❌ 不是框架或库

---

## 🎯 三种技能复用方式

### 方式 1: 复制核心代码模块（推荐）

**适用场景**: 需要相同功能的新项目

#### 步骤：

1. **创建新项目结构**
```bash
mkdir my-new-project
cd my-new-project
mkdir clients utils .streamlit
```

2. **复制可复用的客户端代码**
```bash
# 从本项目复制到新项目
cp clients/gemini_client.py ../my-new-project/clients/
cp clients/feishu_client.py ../my-new-project/clients/
```

3. **根据新需求修改**
```python
# 例如：修改 gemini_client.py 中的模型优先级
priority_keywords = [
    "gemini-2.0-flash",    # 改为优先使用 Flash（更快更便宜）
    "gemini-1.5-pro",      # Pro 作为备选
]
```

4. **复制配置模板**
```bash
cp .streamlit/secrets.toml.example ../my-new-project/.streamlit/
```

---

### 方式 2: 参考文档手写代码

**适用场景**: 需要类似功能但实现细节不同

#### 步骤：

1. **打开 DEVELOPMENT_SKILLS.md**
2. **找到相关章节**（例如：3.1 智能模型选择）
3. **阅读代码示例和设计思路**
4. **根据自己的需求改写**

**示例**：

假设你要集成 OpenAI 而不是 Gemini：

```python
# 参考 DEVELOPMENT_SKILLS.md 第 3.1 节
# 改写为 OpenAI 版本

class OpenAIClient:
    def _get_best_available_model(self):
        """自动选择最优 OpenAI 模型"""
        try:
            # 1. 获取可用模型
            models = openai.Model.list()
            available = [m.id for m in models.data]

            # 2. 定义优先级
            priority = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

            # 3. 匹配逻辑（复用原有思路）
            for keyword in priority:
                for model_id in available:
                    if keyword in model_id:
                        return model_id

            return "gpt-3.5-turbo"  # 兜底
        except Exception as e:
            return "gpt-3.5-turbo"
```

---

### 方式 3: 创建共享代码库（高级）

**适用场景**: 多个项目需要复用相同代码

#### 步骤：

1. **创建独立的 Python 包**
```bash
mkdir ai-assistant-toolkit
cd ai-assistant-toolkit
```

2. **提取通用代码**
```
ai-assistant-toolkit/
├── setup.py
├── ai_toolkit/
│   ├── __init__.py
│   ├── clients/
│   │   ├── base_client.py      # 抽象基类
│   │   ├── gemini_client.py
│   │   └── feishu_client.py
│   └── utils/
│       ├── message_converter.py
│       └── config_validator.py
```

3. **在新项目中安装**
```bash
# 本地安装
pip install -e ../ai-assistant-toolkit

# 或发布到 PyPI
pip install ai-assistant-toolkit
```

4. **在新项目中使用**
```python
from ai_toolkit.clients import GeminiClient, FeishuClient
from ai_toolkit.utils import MessageConverter

client = GeminiClient()
response = client.generate_content("Hello")
```

---

## 📦 推荐的复用清单

### 必须复用的核心代码

| 文件 | 用途 | 修改难度 |
|------|------|----------|
| `clients/gemini_client.py` | AI 模型客户端 | ⭐ 简单 |
| `clients/feishu_client.py` | 飞书 API 客户端 | ⭐ 简单 |
| `.streamlit/secrets.toml` | 配置模板 | ⭐ 简单 |

### 可选复用的工具代码

| 文件 | 用途 | 修改难度 |
|------|------|----------|
| `utils/prompts.py` | 提示词管理 | ⭐⭐ 中等 |
| `utils/router.py` | 路由逻辑 | ⭐⭐⭐ 复杂 |

### 参考但不直接复用

| 文件 | 用途 | 建议 |
|------|------|------|
| `app.py` | 主应用逻辑 | 参考 UI 设计思路，重新编写 |
| `requirements.txt` | 依赖列表 | 根据实际需求调整 |

---

## 🛠️ 实战案例：创建新项目

### 场景：创建一个 Notion + OpenAI 的聊天助手

#### 第 1 步：复制项目结构

```bash
mkdir notion-openai-assistant
cd notion-openai-assistant
mkdir clients utils .streamlit
touch app.py requirements.txt
```

#### 第 2 步：复制并修改客户端

```bash
# 复制 Gemini 客户端作为模板
cp ../deepseek-gemini-feishu-assistant/clients/gemini_client.py \
   clients/openai_client.py
```

**修改 `openai_client.py`**:
```python
import openai
import streamlit as st

class OpenAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or st.secrets.get("OPENAI_API_KEY")
        openai.api_key = self.api_key

        # 复用智能模型选择的思路
        self.model_name = self._get_best_available_model()

    def _get_best_available_model(self):
        """参考 DEVELOPMENT_SKILLS.md 第 3.1 节"""
        try:
            models = openai.Model.list()
            available = [m.id for m in models.data]

            priority = ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
            for keyword in priority:
                for model_id in available:
                    if keyword in model_id:
                        return model_id
            return "gpt-3.5-turbo"
        except:
            return "gpt-3.5-turbo"

    def generate_content(self, prompt, chat_history=[]):
        """参考 DEVELOPMENT_SKILLS.md 第 3.3 节"""
        messages = self._build_history(chat_history)
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    def _build_history(self, chat_history):
        """复用对话历史管理逻辑"""
        messages = []
        for msg in chat_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return messages
```

#### 第 3 步：创建 Notion 客户端

```bash
# 参考飞书客户端的结构
cp ../deepseek-gemini-feishu-assistant/clients/feishu_client.py \
   clients/notion_client.py
```

**修改 `notion_client.py`**:
```python
import requests
import time
from typing import Dict, List

class NotionClient:
    """参考 DEVELOPMENT_SKILLS.md 第 4 章"""

    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    def add_chat_record(self, user_msg: str, ai_msg: str):
        """参考飞书的批量写入逻辑"""
        url = f"{self.base_url}/pages"

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "User Question": {
                    "title": [{"text": {"content": user_msg}}]
                },
                "AI Answer": {
                    "rich_text": [{"text": {"content": ai_msg}}]
                },
                "Timestamp": {
                    "date": {"start": time.strftime("%Y-%m-%d")}
                }
            }
        }

        response = requests.post(url, headers=self._headers, json=payload)
        return response.json()
```

#### 第 4 步：复制 UI 框架

```python
# app.py - 参考原项目的 Streamlit 结构

import streamlit as st
from clients.openai_client import OpenAIClient
from clients.notion_client import NotionClient

# 复用页面配置（DEVELOPMENT_SKILLS.md 第 2.1 节）
st.set_page_config(page_title="Notion AI Assistant", layout="wide")

# 复用 CSS 隐藏样式（直接复制）
hide_streamlit_style = """
<style>
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 复用 Session State 管理（DEVELOPMENT_SKILLS.md 第 2.3 节）
if "messages" not in st.session_state:
    st.session_state.messages = []

if "openai_client" not in st.session_state:
    st.session_state.openai_client = OpenAIClient()

# 复用聊天界面（DEVELOPMENT_SKILLS.md 第 2.4 节）
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("输入问题..."):
    # ... 后续逻辑
```

#### 第 5 步：配置文件

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
NOTION_API_KEY = "secret_..."
NOTION_DATABASE_ID = "xxx..."
```

---

## 📝 技能文档的正确使用方式

### ✅ 推荐做法

1. **放在项目根目录作为参考**
```bash
my-new-project/
├── DEVELOPMENT_SKILLS.md  # 复制过来作为参考文档
├── app.py
├── clients/
└── utils/
```

2. **在开发时查阅**
- 遇到问题时搜索相关章节
- 参考代码示例和最佳实践
- 学习设计思路而不是死记硬背

3. **根据项目需求定制**
- 不要盲目复制所有代码
- 理解原理后改写成适合自己的版本
- 保持代码简洁，只添加需要的功能

### ❌ 不推荐做法

1. **不要直接复制整个项目**
```bash
# ❌ 错误做法
cp -r deepseek-gemini-feishu-assistant my-new-project
```

2. **不要期望"一键应用"**
- 技能文档不是自动化工具
- 需要理解后手动实现

3. **不要忽略业务差异**
- 每个项目的需求不同
- 盲目复用可能导致过度设计

---

## 🎓 学习路径建议

### 第 1 周：理解核心概念
- 阅读 DEVELOPMENT_SKILLS.md 第 1-3 章
- 理解模块化设计和客户端封装
- 运行原项目，观察功能实现

### 第 2 周：动手实践
- 创建一个简单的新项目
- 复用 1-2 个核心模块
- 修改配置使其运行起来

### 第 3 周：深度定制
- 根据新需求修改代码
- 添加新功能
- 解决遇到的问题

### 第 4 周：总结提炼
- 记录自己的改进点
- 更新技能文档
- 形成自己的代码库

---

## 🔗 相关资源

- [DEVELOPMENT_SKILLS.md](./DEVELOPMENT_SKILLS.md) - 完整技能文档
- [README.md](./README.md) - 项目说明
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南

---

## ❓ 常见问题

### Q1: 我必须使用 Streamlit 吗？

**A**: 不是。技能文档中的很多模式（如客户端封装、错误处理）可以应用到任何 Python Web 框架：
- Flask/FastAPI: 复用客户端代码
- Django: 复用业务逻辑
- Gradio: 复用 UI 设计思路

### Q2: 我可以只复用部分代码吗？

**A**: 当然可以！推荐做法：
- 只需要 AI 功能 → 复用 `gemini_client.py`
- 只需要存储功能 → 复用 `feishu_client.py`
- 只需要 UI 设计 → 参考 `app.py` 的 CSS 和布局

### Q3: 如何保持代码更新？

**A**: 两种方式：
1. **定期同步**: 每月检查原项目更新，手动合并改进
2. **Git Submodule**: 将共享代码作为子模块引入

```bash
# 方式 2 示例
git submodule add https://github.com/your/ai-toolkit.git shared
```

### Q4: 技能文档需要放在新项目里吗？

**A**: 建议放，但不是必须：
- ✅ 放在项目里：方便团队成员查阅
- ✅ 放在个人知识库：跨项目复用
- ✅ 两者都做：最佳实践

---

**最后更新**: 2026-02-08
