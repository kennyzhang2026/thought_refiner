# 思路提炼助手 - 部署配置指南

## 📋 项目结构

```
thought_refiner/
├── app.py                     # Streamlit 主应用
├── deepseek_client.py         # DeepSeek API 客户端
├── feishu_client.py           # 飞书多维表格客户端
├── requirements.txt           # Python 依赖
├── SETUP_GUIDE.md            # 本文件
├── .streamlit/
│   └── secrets.toml          # 配置文件（需自行填写）
└── DEVELOPMENT_SKILLS.md     # 开发技能文档
```

## 🔧 环境配置步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 DeepSeek API

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号并创建 API Key
3. 复制 API Key 到配置文件中

### 3. 配置飞书应用

#### 3.1 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app/)
2. 点击「创建企业自建应用」
3. 填写应用名称（如"思路提炼助手"）
4. 在「凭证与基础信息」中获取 **App ID** 和 **App Secret**

#### 3.2 配置权限

在「权限管理」中添加以下权限：

- `bitable:record:app:create`（在多维表格中新增记录）
- `bitable:record:app:read`（读取多维表格记录）

#### 3.3 发布应用

1. 在「版本管理与发布」中创建版本
2. 填写版本号和更新说明
3. 点击「申请发布」
4. 在飞书管理后台审核通过

#### 3.4 获取多维表格信息

1. 打开目标多维表格
2. 从 URL 中复制 `app_token` 和 `table_id`：
   ```
   https://feishu.cn/base/XXXXXXXXX?table=YYYYYYYY
                          │              │
                    app_token      table_id
   ```

#### 3.5 多维表格字段设置

确保你的多维表格包含以下字段：

| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 时间 | 日期 | 自动填充 |
| 原始思路 | 文本 | 用户输入的原始内容 |
| 提炼结果 | 文本 | AI提炼后的内容 |
| 版本数 | 数字 | 迭代次数 |
| 标签 | 多选 | 标记为"思路提炼" |

### 4. 配置文件

编辑 `.streamlit/secrets.toml` 文件，填入所有配置值：

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key"
FEISHU_APP_ID = "your_feishu_app_id"
FEISHU_APP_SECRET = "your_feishu_app_secret"
FEISHU_APP_TOKEN = "your_bitable_app_token"
FEISHU_TABLE_ID = "your_bitable_table_id"
```

**注意**：不要将包含真实密钥的 secrets.toml 提交到 Git！

## 🚀 本地运行

```bash
streamlit run app.py
```

应用将在 http://localhost:8501 启动。

## ☁️ 部署到 Streamlit Cloud

### 1. 准备代码仓库

1. 在 GitHub 上创建新仓库
2. 将代码推送到仓库：
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/thought-refiner.git
   git push -u origin main
   ```

**注意**：不要提交 `.streamlit/secrets.toml` 文件！

### 2. 部署到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 点击「New app」
3. 选择你的 GitHub 仓库
4. 在「Advanced settings」->「Secrets」中配置：

   ```toml
   DEEPSEEK_API_KEY = "your_key"
   FEISHU_APP_ID = "your_app_id"
   FEISHU_APP_SECRET = "your_secret"
   FEISHU_APP_TOKEN = "your_token"
   FEISHU_TABLE_ID = "your_table_id"
   ```

5. 点击「Deploy」

## 📝 使用流程

1. **输入思路**：在文本框中输入你的想法
2. **点击提炼**：AI自动分析并提炼要点
3. **查看结果**：查看结构化的提炼结果
4. **迭代优化**：
   - 满意 → 输入 `OK` 保存到飞书
   - 不满意 → 输入修改意见，AI会基于之前的结果调整
5. **循环**：直到满意为止

## 🐛 故障排查

### 问题1: DeepSeek API 调用失败

**排查**：
- 检查 API Key 是否正确
- 检查网络连接
- 查看 DeepSeek 平台状态

### 问题2: 飞书保存失败

**排查**：
- 检查 App ID 和 App Secret 是否正确
- 确认应用已发布并通过审核
- 检查多维表格字段名称是否匹配
- 查看应用是否有足够的权限

### 问题3: 页面加载缓慢

**排查**：
- 首次加载需要安装依赖，耐心等待
- DeepSeek API 响应时间约为 2-5 秒

## 💡 优化建议

1. **Prompt 优化**：可以修改 `app.py` 中的 `REFINE_SYSTEM_PROMPT` 来调整 AI 的输出风格
2. **界面定制**：修改 CSS 样式来匹配你的品牌
3. **功能扩展**：可以添加导出 Markdown、PDF 等功能

## 📞 需要帮助？

- DeepSeek API: https://platform.deepseek.com/
- 飞书开放平台: https://open.feishu.cn/
- Streamlit 文档: https://docs.streamlit.io/
