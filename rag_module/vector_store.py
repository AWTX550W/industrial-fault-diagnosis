# -*- coding: utf-8 -*-
"""
RAG 向量检索模块 - 向量存储与检索
使用 ChromaDB 存储向量，支持持久化
"""
import os
from pathlib import Path
from typing import List, Dict, Optional


class VectorStore:
    """ChromaDB 向量存储封装"""

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or str(Path(__file__).parent / "chroma_db")
        self.client = None
        self.collection = None

    def init_chroma(self):
        """初始化 ChromaDB 客户端和集合"""
        try:
            import chromadb
            from chromadb.config import Settings
            os.makedirs(self.persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="fault_knowledge",
                metadatadata={"hnsw:space": "cosine"}
            )
            return True
        except ImportError:
            print("❌ 缺少 chromadb，请运行: pip install chromadb")
            return False
        except Exception as e:
            print(f"❌ ChromaDB 初始化失败: {e}")
            return False

    def add_documents(self, documents: List[Dict]) -> bool:
        """
        向向量库添加文档
        documents: [{"id":..., "content":..., "metadata":...}, ...]
        """
        if not self.collection:
            if not self.init_chroma():
                return False
        try:
            ids = [doc["id"] for doc in documents]
            contents = [doc["content"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            return False

    def search(self, query_text: str, n_results: int = 3) -> List[Dict]:
        """
        向量相似度搜索
        返回: [{"id":..., "content":..., "metadata":..., "distance":...}, ...]
        """
        if not self.collection:
            if not self.init_chroma():
                return []
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            output = []
            if results and results.get("ids"):
                for i, doc_id in enumerate(results["ids"][0]):
                    output.append({
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            return output
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def clear(self) -> bool:
        """清空向量库"""
        try:
            if self.client:
                self.client.delete_collection("fault_knowledge")
                self.collection = self.client.get_or_create_collection(
                    name="fault_knowledge",
                    metadata={"hnsw:space": "cosine"}
                )
            return True
        except Exception as e:
            print(f"❌ 清空失败: {e}")
            return False

    def count(self) -> int:
        """返回库中文档数量"""
        if not self.collection:
            if not self.init_chroma():
                return 0
        return self.collection.count()
