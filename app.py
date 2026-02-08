"""
思路提炼助手 - Streamlit 应用
功能：输入思路 → AI提炼 → 迭代修改 → 保存到飞书
"""

import streamlit as st
import streamlit.components.v1 as components
import logging
from datetime import datetime
from deepseek_client import DeepSeekClient
from feishu_client import FeishuClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ 页面配置 ============
st.set_page_config(
    page_title="思路提炼助手",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============ 自定义CSS ============
st.markdown("""
<style>
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 标题样式 */
    .main-title {
        text-align: center;
        color: #1f1f1f;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* 提炼按钮样式 */
    .refine-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    /* 结果卡片样式 */
    .result-card {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* 状态标签 */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .status-waiting {
        background: #fff3cd;
        color: #856404;
    }

    .status-refining {
        background: #d1ecf1;
        color: #0c5460;
    }

    .status-done {
        background: #d4edda;
        color: #155724;
    }

    /* 提示信息 */
    .tip-box {
        background: #e7f3ff;
        border: 1px solid #b8daff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #004085;
    }

    /* 保存成功提示 */
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }

    /* 语音按钮样式 */
    .voice-btn-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .voice-btn {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 1.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(238, 90, 111, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .voice-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(238, 90, 111, 0.4);
    }

    .voice-btn.recording {
        background: linear-gradient(135deg, #ff4757 0%, #ff3838 100%);
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(255, 71, 87, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 71, 87, 0); }
    }

    .voice-status {
        font-size: 0.9rem;
        color: #666;
        margin-left: 0.5rem;
    }

    .voice-status.recording {
        color: #ff4757;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============ 系统提示词 ============
REFINE_SYSTEM_PROMPT = """你是一位专业的思路提炼助手。你的任务是帮助用户整理和提炼他们的想法。

请按以下步骤处理用户的输入：

1. **核心要点提炼**：提取输入中的关键观点（3-5个要点）
2. **结构化整理**：将内容组织成清晰的结构
3. **优化建议**：提供2-3条具体的改进建议
4. **总结**：用1-2句话总结核心思想

输出格式：
## 📌 核心要点
- 要点1
- 要点2
...

## 📋 结构化整理
[整理后的内容]

## 💡 优化建议
1. 建议1
2. 建议2
...

## 📝 总结
[一句话总结]

注意：
- 保持客观，不要添加用户未提及的内容
- 使用简洁清晰的语言
- 如果用户提出修改意见，请基于之前的结果进行调整
"""

# ============ 初始化Session State ============
def init_session_state():
    """初始化会话状态"""
    defaults = {
        "stage": "input",  # input, refining, review, saved
        "original_input": "",
        "refined_result": "",
        "conversation_history": [],  # 记录对话历史用于迭代
        "current_version": 0,
        "feishu_saved": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============ 工具函数 ============
def get_clients():
    """获取API客户端"""
    try:
        deepseek_client = DeepSeekClient(
            api_key=st.secrets.get("DEEPSEEK_API_KEY", "")
        )
        feishu_client = FeishuClient(
            app_id=st.secrets.get("FEISHU_APP_ID", ""),
            app_secret=st.secrets.get("FEISHU_APP_SECRET", ""),
            app_token=st.secrets.get("FEISHU_APP_TOKEN", "")
        )
        return deepseek_client, feishu_client
    except Exception as e:
        st.error(f"客户端初始化失败: {e}")
        return None, None

def refine_thought(text: str, history: list = None) -> str:
    """调用DeepSeek提炼思路"""
    deepseek_client, _ = get_clients()

    if not deepseek_client or not deepseek_client.client:
        return "错误: DeepSeek客户端未初始化，请检查API Key配置"

    # 构建消息上下文
    if history and len(history) > 0:
        # 有历史记录，构建上下文
        context = "之前的提炼结果:\n" + st.session_state.get("refined_result", "")
        full_message = f"{context}\n\n用户的修改意见:\n{text}"
    else:
        full_message = text

    with st.spinner("🤖 AI正在提炼思路中..."):
        result = deepseek_client.get_response(
            message=full_message,
            system_prompt=REFINE_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=2500
        )

    if result.get("success"):
        return result.get("content", "")
    else:
        return f"错误: {result.get('error', '未知错误')}"

def save_to_feishu(original: str, refined: str) -> bool:
    """保存到飞书多维表格"""
    _, feishu_client = get_clients()

    if not feishu_client:
        return False

    try:
        table_id = st.secrets.get("FEISHU_TABLE_ID", "")

        # 构建记录
        record = {
            "时间": int(datetime.now().timestamp() * 1000),
            "原始思路": original,
            "提炼结果": refined,
            "版本数": st.session_state.get("current_version", 1),
            "标签": ["思路提炼"]
        }

        result = feishu_client.add_record_to_bitable(table_id, record)
        return result.get("success", False)

    except Exception as e:
        logger.error(f"保存到飞书失败: {e}")
        return False

# ============ UI组件 ============
def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-title">💡 思路提炼助手</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">输入你的想法，AI帮你提炼要点、优化结构</p>', unsafe_allow_html=True)

def render_status_badge():
    """渲染状态标签"""
    stage = st.session_state.get("stage", "input")

    status_map = {
        "input": ("📝 等待输入", "status-waiting"),
        "refining": ("🤖 提炼中...", "status-refining"),
        "review": ("👀 等待确认", "status-waiting"),
        "saved": ("✅ 已保存", "status-done")
    }

    text, css_class = status_map.get(stage, ("未知", "status-waiting"))
    st.markdown(f'<span class="status-badge {css_class}">{text}</span>', unsafe_allow_html=True)

def render_voice_input():
    """渲染语音输入组件"""
    # 使用HTML和JS实现语音录入
    voice_html = """
    <div class="voice-btn-container">
        <button id="voiceBtn" class="voice-btn" onclick="toggleRecording()" title="点击开始语音输入">
            🎤
        </button>
        <span id="voiceStatus" class="voice-status">点击麦克风开始语音输入</span>
    </div>

    <script>
        let recognition = null;
        let isRecording = false;

        // 检查浏览器是否支持语音识别
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'zh-CN';
            recognition.continuous = true;
            recognition.interimResults = true;

            recognition.onstart = function() {
                isRecording = true;
                document.getElementById('voiceBtn').classList.add('recording');
                document.getElementById('voiceStatus').textContent = '正在录音... (再次点击停止)';
                document.getElementById('voiceStatus').classList.add('recording');
            };

            recognition.onend = function() {
                isRecording = false;
                document.getElementById('voiceBtn').classList.remove('recording');
                document.getElementById('voiceStatus').textContent = '点击麦克风开始语音输入';
                document.getElementById('voiceStatus').classList.remove('recording');
            };

            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }

                // 获取当前文本框内容
                const textArea = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
                if (textArea && finalTranscript) {
                    const currentValue = textArea.value;
                    textArea.value = currentValue + (currentValue ? ' ' : '') + finalTranscript;
                    // 触发input事件让Streamlit检测到变化
                    textArea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };

            recognition.onerror = function(event) {
                console.error('语音识别错误:', event.error);
                document.getElementById('voiceStatus').textContent = '语音识别出错，请重试';
                isRecording = false;
                document.getElementById('voiceBtn').classList.remove('recording');
            };
        } else {
            document.getElementById('voiceStatus').textContent = '您的浏览器不支持语音识别';
            document.getElementById('voiceBtn').disabled = true;
        }

        function toggleRecording() {
            if (!recognition) {
                alert('您的浏览器不支持语音识别功能，请使用 Chrome、Edge 或 Safari 浏览器');
                return;
            }

            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
    </script>
    """
    st.components.v1.html(voice_html, height=70)

def render_input_stage():
    """渲染输入阶段"""
    st.markdown("### 📝 输入你的想法")

    # 语音输入提示
    st.caption("🎤 支持语音输入，点击下方麦克风按钮")

    user_input = st.text_area(
        "",
        placeholder="在这里输入你的想法、笔记或任何需要整理的内容...\n\n比如：\n- 会议记录\n- 项目思路\n- 读书笔记\n- 问题分析\n\n或者点击下方的 🎤 按钮开始语音输入",
        height=200,
        key="input_text"
    )

    # 语音录入按钮和开始提炼按钮并排
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # 语音输入组件
        render_voice_input()

    with col3:
        if st.button("🚀 开始提炼", use_container_width=True, type="primary"):
            # 获取最新的输入值（包括语音输入的）
            user_input = st.session_state.get("input_text", "")
            if not user_input.strip():
                st.warning("⚠️ 请输入内容后再点击提炼")
                return

            # 更新状态
            st.session_state["stage"] = "refining"
            st.session_state["original_input"] = user_input
            st.session_state["conversation_history"] = []

            # 调用提炼
            result = refine_thought(user_input)

            if result.startswith("错误:"):
                st.error(result)
                st.session_state["stage"] = "input"
            else:
                st.session_state["refined_result"] = result
                st.session_state["current_version"] = 1
                st.session_state["stage"] = "review"

            st.rerun()

def render_review_stage():
    """渲染审核/迭代阶段"""
    st.markdown("### 📋 提炼结果")

    # 显示原始输入（可折叠）
    with st.expander("📄 查看原始输入"):
        st.markdown(st.session_state.get("original_input", ""))

    # 显示提炼结果
    result = st.session_state.get("refined_result", "")
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.markdown(result)
    st.markdown('</div>', unsafe_allow_html=True)

    # 版本信息
    version = st.session_state.get("current_version", 1)
    if version > 1:
        st.caption(f"📝 第 {version} 个版本")

    # 分隔线
    st.markdown("---")

    # 操作区域
    st.markdown("### 💬 下一步操作")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**满意吗？输入OK保存**")
        user_feedback = st.text_input(
            "",
            placeholder="输入 OK 保存到飞书，或输入修改意见继续优化...",
            key="feedback_input"
        )

        if st.button("✅ 提交", use_container_width=True):
            if not user_feedback.strip():
                st.warning("请输入内容")
                return

            feedback = user_feedback.strip().lower()

            if feedback == "ok":
                # 保存到飞书
                st.session_state["stage"] = "refining"
                st.rerun()

                original = st.session_state.get("original_input", "")
                refined = st.session_state.get("refined_result", "")

                if save_to_feishu(original, refined):
                    st.session_state["stage"] = "saved"
                    st.session_state["feishu_saved"] = True
                    st.success("🎉 已成功保存到飞书多维表格！")
                else:
                    st.error("❌ 保存到飞书失败，请检查配置")
                    st.session_state["stage"] = "review"

                st.rerun()
            else:
                # 继续迭代
                st.session_state["stage"] = "refining"
                st.rerun()

                # 调用DeepSeek进行修改
                history = st.session_state.get("conversation_history", [])
                new_result = refine_thought(user_feedback, history)

                if new_result.startswith("错误:"):
                    st.error(new_result)
                else:
                    # 更新历史记录
                    history.append({
                        "version": version,
                        "feedback": user_feedback,
                        "result": new_result
                    })
                    st.session_state["conversation_history"] = history
                    st.session_state["refined_result"] = new_result
                    st.session_state["current_version"] = version + 1
                    st.session_state["stage"] = "review"

                st.rerun()

    with col2:
        st.markdown("**或选择其他操作**")

        if st.button("🔄 重新开始", use_container_width=True):
            # 重置状态
            st.session_state["stage"] = "input"
            st.session_state["original_input"] = ""
            st.session_state["refined_result"] = ""
            st.session_state["conversation_history"] = []
            st.session_state["current_version"] = 0
            st.session_state["feishu_saved"] = False
            st.rerun()

def render_saved_stage():
    """渲染保存完成阶段"""
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ 保存成功！")
    st.markdown("你的思路提炼结果已保存到飞书多维表格。")
    st.markdown('</div>', unsafe_allow_html=True)

    # 显示最终内容
    st.markdown("### 📋 最终提炼结果")
    st.markdown(st.session_state.get("refined_result", ""))

    if st.button("🔄 开始新的提炼", use_container_width=True):
        # 重置所有状态
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        init_session_state()
        st.rerun()

def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🛠️ 使用说明")

        st.markdown("""
        ### 工作流程
        1. **输入思路** - 在文本框中输入你的想法
        2. **AI提炼** - 点击按钮，AI自动提炼要点
        3. **查看结果** - 查看结构化整理后的内容
        4. **迭代优化** - 不满意可以提出修改意见
        5. **确认保存** - 输入 OK 保存到飞书

        ### 快捷键
        - `Enter` 在文本框内换行
        - 点击按钮提交

        ### 支持的输入
        - 会议记录
        - 项目思路
        - 读书笔记
        - 问题分析
        - 任何需要整理的文字
        """)

        st.markdown("---")

        # 状态显示
        st.markdown("### 📊 当前状态")
        stage = st.session_state.get("stage", "input")
        stage_names = {
            "input": "等待输入",
            "refining": "提炼中",
            "review": "等待确认",
            "saved": "已保存"
        }
        st.info(f"当前阶段: {stage_names.get(stage, '未知')}")

        version = st.session_state.get("current_version", 0)
        if version > 0:
            st.success(f"当前版本: v{version}")

# ============ 主函数 ============
def main():
    render_header()
    render_sidebar()

    # 根据阶段渲染不同内容
    stage = st.session_state.get("stage", "input")

    if stage == "input":
        render_input_stage()
    elif stage == "refining":
        # 提炼中状态，显示加载
        st.spinner("🤖 AI正在处理...")
        # 实际处理在按钮点击时完成，这里只是一个过渡状态
    elif stage == "review":
        render_review_stage()
    elif stage == "saved":
        render_saved_stage()

    # 渲染提示信息
    if stage == "review":
        st.markdown("""
        <div class="tip-box">
        💡 <strong>提示</strong>：如果结果满意，输入 <strong>OK</strong> 保存到飞书；
        如果需要调整，直接输入修改意见，如"请补充更多细节"或"简化第三点"。
        </div>
        """, unsafe_allow_html=True)

# ============ 运行应用 ============
if __name__ == "__main__":
    main()
