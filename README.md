# 工业机械核心部件故障诊断与维护助手

基于规则引擎 + 知识库的轴承/电机故障智能诊断系统。

## 快速开始

```bash
# 终端交互版（零依赖，直接运行）
python demo.py

# 运行自动化测试
python run.py --test
```

## 4 种故障诊断演示

| 输入 | 匹配结果 | 置信度 |
|------|---------|--------|
| 轴承振动大，有异常噪声 | 轴承内圈故障 | 85% |
| 电机温度很高，有异味 | 电机过热 | 85% |
| 电机启动困难，电流大 | 电机启动问题 | 80% |
| 设备发出摩擦声，温度升高 | 轴承润滑不良 | 80% |

## 项目结构

```
industrial-fault-diagnosis/
├── demo.py              # 终端交互 Demo（推荐从这里开始）
├── run.py               # 启动/测试脚本
├── ARCHITECTURE.md      # 架构设计文档
│
├── knowledge_base/      # 知识库模块
│   ├── fault_data.json  # 10条故障知识（5轴承+5电机）
│   └── loader.py        # 知识库加载/查询
│
├── rules_engine/        # 规则引擎模块
│   ├── rules.json       # 8条诊断规则
│   ├── rules.yaml       # YAML格式规则（备选）
│   └── engine.py        # 规则匹配引擎
│
├── rag_module/          # RAG向量检索模块（需安装依赖）
│   ├── vector_store.py  # ChromaDB 向量存储
│   ├── embedding.py     # Sentence Transformers 向量化
│   └── retriever.py     # 检索器
│
├── streamlit_app/       # Streamlit Web 界面（需安装依赖）
│   └── app.py           # Web 应用
│
├── requirements_lite.txt   # 轻量版依赖
└── requirements_full.txt   # 进阶版依赖
```

## 安装额外依赖（可选）

```bash
# Streamlit Web界面
pip install streamlit

# RAG向量检索
pip install chromadb sentence-transformers

# 进阶版：信号处理+机器学习
pip install scikit-learn scipy matplotlib
```

## 两种版本

- **轻量版**（当前）：规则引擎 + 知识库，零依赖运行
- **进阶版**（规划中）：增加 CWRU 轴承振动信号分析 + ML 故障分类

## 面试亮点

1. 完整的诊断链路：输入现象 → 规则匹配 → 知识检索 → 维护建议
2. 模块化设计：知识库/规则引擎/RAG/前端独立解耦
3. 真实工业场景：轴承+电机故障诊断，实用性强
4. 可扩展：轻量→进阶，规则→ML，终端→Web
