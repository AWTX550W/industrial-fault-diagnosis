# -*- coding: utf-8 -*-
"""
Streamlit 前端应用 - 工业机械故障诊断助手
"""
import sys
import os
from pathlib import Path

# 确保项目根目录在 sys.path 中
SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import streamlit as st
from knowledge_base.loader import FaultKnowledgeBase
from rules_engine.engine import RulesEngine
from rag_module.retriever import FaultRetriever


# 页面配置
st.set_page_config(
    page_title="工业机械故障诊断助手",
    page_icon="🔧",
    layout="wide"
)

# 标题
st.title("🔧 工业机械核心部件故障诊断与维护助手")
st.markdown("---")


# 初始化（使用缓存）
@st.cache_resource
def init_knowledge_base():
    kb = FaultKnowledgeBase()
    kb.load()
    return kb


@st.cache_resource
def init_rules_engine():
    engine = RulesEngine()
    engine.load_rules()
    return engine


@st.cache_resource
def init_rag_retriever():
    retriever = FaultRetriever()
    retriever.init_rag()
    return retriever


# 侧边栏：模式选择
st.sidebar.title("诊断模式")
mode = st.sidebar.radio(
    "选择诊断方式",
    ["规则引擎诊断", "RAG 向量检索", "混合诊断"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 关于")
st.sidebar.info(
    "本工具支持轴承和电机的故障诊断。\n"
    "输入故障现象，系统将给出可能的故障原因和维护建议。"
)


# 主界面
tab1, tab2, tab3 = st.tabs(["故障诊断", "知识库查询", "关于系统"])

with tab1:
    st.header("故障诊断")
    user_input = st.text_area(
        "请输入故障现象（例如：轴承振动大，有异常噪声，温度升高）",
        height=100,
        placeholder="请描述您观察到的设备故障现象..."
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        diagnose_btn = st.button("开始诊断", type="primary")
    with col2:
        clear_btn = st.button("清空")

    if clear_btn:
        st.experimental_rerun()

    if diagnose_btn and user_input.strip():
        st.markdown("---")
        st.subheader("诊断结果")

        if mode == "规则引擎诊断":
            engine = init_rules_engine()
            results = engine.diagnose(user_input)

            if not results:
                st.warning("未匹配到已知故障规则，请尝试补充更多故障现象。")
            else:
                for i, r in enumerate(results, 1):
                    fault_id = r.fault_id
                    kb = init_knowledge_base()
                    fault = kb.get_fault_by_id(fault_id)

                    with st.expander(f"[{r.confidence:.0%}] {r.message}", expanded=(i == 1)):
                        if fault:
                            st.markdown(f"**故障名称**: {fault.name}")
                            st.markdown(f"**涉及部件**: {', '.join(fault.related_parts)}")
                            st.markdown(f"**严重程度**: {fault.severity}")
                            st.markdown("**可能原因**:")
                            for c in fault.causes:
                                st.markdown(f"- {c}")
                            st.markdown("**建议解决方案**:")
                            for s in fault.solutions:
                                st.markdown(f"- {s}")
                            st.markdown("**预防措施**:")
                            for p in fault.prevention:
                                st.markdown(f"- {p}")
                        else:
                            st.markdown(r.message)

        elif mode == "RAG 向量检索":
            retriever = init_rag_retriever()
            results = retriever.retrieve(user_input, n_results=3)

            if not results:
                st.warning("未检索到相关知识，请尝试重新描述故障现象。")
            else:
                for i, r in enumerate(results, 1):
                    fault_id = r["metadata"].get("fault_id", "")
                    doc_type = r["metadata"].get("type", "")
                    distance = r.get("distance", 0)
                    similarity = 1 - distance if distance else "N/A"

                    with st.expander(f"知识片段 {i} (相似度: {similarity if isinstance(similarity, str) else f'{similarity:.1%}'})", expanded=(i == 1)):
                        st.markdown(f"**故障ID**: {fault_id}")
                        st.markdown(f"**内容类型**: {doc_type}")
                        st.markdown(f"**知识内容**:\n{r['content']}")

        else:  # 混合诊断
            st.markdown("#### 规则引擎结果")
            engine = init_rules_engine()
            rule_results = engine.diagnose(user_input)

            if rule_results:
                for r in rule_results[:2]:
                    st.markdown(f"- [{r.confidence:.0%}] {r.message}")
            else:
                st.markdown("- 未匹配规则")

            st.markdown("#### RAG 检索结果")
            retriever = init_rag_retriever()
            rag_results = retriever.retrieve(user_input, n_results=2)

            if rag_results:
                for r in rag_results:
                    st.markdown(f"- {r['content'][:80]}...")
            else:
                st.markdown("- 未检索到相关知识")

            st.markdown("#### 综合建议")
            if rule_results:
                fault_id = rule_results[0].fault_id
                kb = init_knowledge_base()
                fault = kb.get_fault_by_id(fault_id)
                if fault:
                    st.success(f"最可能故障: **{fault.name}**\n建议优先检查: {', '.join(fault.causes[:2])}")

    elif diagnose_btn and not user_input.strip():
        st.error("请输入故障现象描述！")

with tab2:
    st.header("知识库查询")
    kb = init_knowledge_base()

    search_type = st.radio("查询方式", ["按部件浏览", "按症状搜索", "查看全部"])

    if search_type == "按部件浏览":
        component = st.selectbox("选择部件类型", ["轴承", "电机"])
        faults = kb.get_faults_by_component(component)
        if faults:
            for f in faults:
                with st.expander(f"{f.name} (严重程度: {f.severity})"):
                    st.markdown(f"**症状**: {', '.join(f.symptoms)}")
                    st.markdown(f"**原因**: {', '.join(f.causes)}")
        else:
            st.info(f"暂无 {component} 相关故障知识")

    elif search_type == "按症状搜索":
        symptom = st.text_input("输入症状关键词（如：振动、过热）")
        if symptom:
            results = kb.search_faults_by_symptom(symptom)
            if results:
                st.success(f"找到 {len(results)} 条相关故障:")
                for r in results:
                    st.markdown(f"- **{r.name}**: {r.symptoms[0]}")
            else:
                st.warning("未找到相关故障")

    else:
        st.markdown(f"**轴承故障**: {len(kb.bearing_faults)} 条")
        st.markdown(f"**电机故障**: {len(kb.motor_faults)} 条")
        if st.checkbox("显示全部详情"):
            for f in kb.all_faults:
                with st.expander(f"{f.id} - {f.name}"):
                    st.json(f.to_dict())

with tab3:
    st.header("关于系统")
    st.markdown(
        """
        ### 工业机械核心部件故障诊断与维护助手

        **功能特性**:
        - 支持轴承和电机的故障诊断
        - 基于规则引擎的快速匹配
        - 基于 RAG 的向量检索
        - 混合诊断模式

        **技术栈**:
        - Python 3.9+
        - Streamlit (Web 界面)
        - ChromaDB (向量数据库)
        - Sentence Transformers (文本向量化)
        - PyYAML (规则定义)

        **使用方式**:
        1. 在"故障诊断"页面输入故障现象
        2. 选择诊断模式
        3. 查看诊断结果和维护建议

        **项目状态**: 轻量版 (v0.1)
        """
    )
