#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工业机械故障诊断助手 - 启动脚本

使用方式:
    python run.py              # 启动 Streamlit Web 应用
    python run.py --test      # 运行测试模式
    python run.py --init-rag  # 初始化 RAG 向量库
"""
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def init_rag():
    """初始化 RAG 向量库"""
    print("🔍 正在初始化 RAG 向量库...")
    try:
        from rag_module.retriever import FaultRetriever
        retriever = FaultRetriever()
        success = retriever.init_rag(force_rebuild=True)
        if success:
            print("✅ RAG 向量库初始化成功")
        else:
            print("❌ RAG 向量库初始化失败")
            return False
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def run_test():
    """运行测试模式"""
    print("🧪 运行测试模式...\n")

    # 测试知识库
    print("=" * 50)
    print("测试 1: 知识库加载")
    print("=" * 50)
    try:
        from knowledge_base.loader import FaultKnowledgeBase
        kb = FaultKnowledgeBase()
        if kb.load():
            print(f"✅ 知识库加载成功，共 {len(kb.all_faults)} 条故障知识")
        else:
            print("❌ 知识库加载失败")
            return False
    except Exception as e:
        print(f"❌ 知识库测试失败: {e}")
        return False

    # 测试规则引擎
    print("\n" + "=" * 50)
    print("测试 2: 规则引擎")
    print("=" * 50)
    try:
        from rules_engine.engine import RulesEngine
        engine = RulesEngine()
        if engine.load_rules():
            print(f"✅ 规则引擎加载成功，共 {len(engine.rules)} 条规则")
            test_input = "轴承振动大，有异常噪声"
            results = engine.diagnose(test_input)
            print(f"   测试输入: {test_input}")
            print(f"   匹配结果: {len(results)} 条")
            for r in results:
                print(f"     - [{r.confidence:.0%}] {r.message}")
        else:
            print("❌ 规则引擎加载失败")
            return False
    except Exception as e:
        print(f"❌ 规则引擎测试失败: {e}")
        return False

    # 测试 RAG（如果依赖已安装）
    print("\n" + "=" * 50)
    print("测试 3: RAG 向量检索")
    print("=" * 50)
    try:
        from rag_module.retriever import FaultRetriever
        retriever = FaultRetriever()
        if retriever.init_rag():
            print("✅ RAG 初始化成功")
            test_query = "轴承振动怎么办"
            results = retriever.retrieve(test_query, n_results=2)
            print(f"   测试查询: {test_query}")
            print(f"   检索结果: {len(results)} 条")
            for r in results:
                print(f"     - {r['content'][:60]}...")
        else:
            print("⚠️  RAG 初始化跳过（可能缺少依赖）")
    except Exception as e:
        print(f"⚠️  RAG 测试跳过（可能缺少依赖）: {e}")

    print("\n🎉 基础测试完成！")
    return True


def run_streamlit():
    """启动 Streamlit 应用"""
    app_path = SCRIPT_DIR / "streamlit_app" / "app.py"
    if not app_path.exists():
        print(f"❌ 找不到应用文件: {app_path}")
        return False

    print("🚀 正在启动 Streamlit 应用...")
    print(f"   应用路径: {app_path}")
    print("   在浏览器中打开 http://localhost:8501 访问应用")
    print("\n提示: 按 Ctrl+C 停止应用\n")

    try:
        os.system(f"streamlit run {app_path}")
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

    return True


if __name__ == "__main__":
    if "--test" in sys.argv:
        success = run_test()
        sys.exit(0 if success else 1)
    elif "--init-rag" in sys.argv:
        success = init_rag()
        sys.exit(0 if success else 1)
    else:
        run_streamlit()
