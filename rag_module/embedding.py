# -*- coding: utf-8 -*-
"""
文本向量化 - 使用 Sentence Transformers
"""
from typing import List, Optional
import numpy as np


class Embedder:
    """文本向量化封装，支持中文"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.model = None

    def load_model(self) -> bool:
        """加载向量模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            print(f"✅ 向量模型加载成功: {self.model_name}")
            return True
        except ImportError:
            print("❌ 缺少 sentence-transformers，请运行: pip install sentence-transformers")
            return False
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return False

    def encode(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        将文本列表转为向量
        返回: ndarray, shape=(len(texts), embedding_dim)
        """
        if not self.model:
            if not self.load_model():
                return np.array([])
        try:
            embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=False)
            return embeddings
        except Exception as e:
            print(f"❌ 向量化失败: {e}")
            return np.array([])

    def encode_query(self, query: str) -> np.ndarray:
        """单条查询向量化"""
        return self.encode([query])


if __name__ == "__main__":
    emb = Embedder()
    if emb.load_model():
        vecs = emb.encode(["轴承振动大", "电机过热"])
        print(f"向量维度: {vecs.shape}")
        # 计算相似度
        from sklearn.metrics.pairwise import cosine_similarity
        sim = cosine_similarity([vecs[0]], [vecs[1]])[0][0]
        print(f"两条文本余弦相似度: {sim:.4f}")
