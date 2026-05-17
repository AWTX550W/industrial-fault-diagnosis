# -*- coding: utf-8 -*-
"""
RAG 检索器 - 整合向量存储、嵌入和知识库
"""
from pathlib import Path
from typing import List, Dict, Optional
import sys

# 添加项目根目录到路径
SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from knowledge_base.loader import FaultKnowledgeBase
from rag_module.vector_store import VectorStore
from rag_module.embedding import Embedder


class FaultRetriever:
    """故障知识 RAG 检索器"""

    def __init__(self, kb_path: Optional[str] = None, persist_dir: Optional[str] = None):
        self.kb = FaultKnowledgeBase(kb_path)
        self.vector_store = VectorStore(persist_dir)
        self.embedder = Embedder()
        self.initialized = False

    def init_rag(self, force_rebuild: bool = False) -> bool:
        """
        初始化 RAG 系统：
        1. 加载知识库
        2. 初始化向量库
        3. 构建向量索引（如果为空或强制重建）
        """
        # 加载知识库
        if not self.kb.load():
            print("❌ 知识库加载失败")
            return False

        # 初始化向量库
        if not self.vector_store.init_chroma():
            print("❌ 向量库初始化失败，请检查 chromadb 安装")
            return False

        # 检查是否需要构建索引
        count = self.vector_store.count()
        if count > 0 and not force_rebuild:
            print(f"✅ RAG 索引已存在（{count} 条文档），跳过构建")
            self.initialized = True
            return True

        # 构建索引
        print("🔨 正在构建 RAG 向量索引...")
        documents = self.kb.summarize_for_rag()

        # 使用 embedding 模型（延迟加载）
        # 注意：ChromaDB 会自动使用其内置的 embedding 函数
        # 所以我们直接添加文档，让 ChromaDB 自己处理向量化
        ok = self.vector_store.add_documents(documents)
        if ok:
            print(f"✅ RAG 索引构建成功，共 {len(documents)} 条文档")
            self.initialized = True
            return True
        else:
            print("❌ RAG 索引构建失败")
            return False

    def retrieve(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        检索与查询最相关的知识片段
        返回: [{"id":..., "content":..., "metadata":..., "distance":...}, ...]
        """
        if not self.initialized:
            print("⚠️  RAG 未初始化，尝试自动初始化...")
            if not self.init_rag():
                return []

        return self.vector_store.search(query, n_results=n_results)

    def retrieve_and_format(self, query: str, n_results: int = 3) -> str:
        """
        检索并格式化为可读文本
        用于直接作为 LLM 的上下文
        """
        results = self.retrieve(query, n_results)
        if not results:
            return "未找到相关知识。"

        formatted = "以下是相关的故障诊断知识：\n\n"
        for i, r in enumerate(results, 1):
            fault_id = r["metadata"].get("fault_id", "")
            doc_type = r["metadata"].get("type", "")
            formatted += f"[知识片段 {i}] (故障ID: {fault_id}, 类型: {doc_type})\n"
            formatted += f"{r['content']}\n\n"

        return formatted

    def get_fault_detail(self, fault_id: str) -> Optional[Dict]:
        """获取完整故障知识"""
        fault = self.kb.get_fault_by_id(fault_id)
        if fault:
            return fault.to_dict()
        return None


if __name__ == "__main__":
    retriever = FaultRetriever()
    if retriever.init_rag(force_rebuild=True):
        print("\n🔍 测试检索:")
        test_queries = ["轴承振动大怎么办", "电机过热原因"]
        for q in test_queries:
            print(f"\n  查询: {q}")
            results = retriever.retrieve(q, n_results=2)
            for r in results:
                print(f"    - {r['content'][:60]}... (距离: {r.get('distance', 'N/A'):.4f})")
