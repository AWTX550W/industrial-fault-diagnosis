# Industrial Fault Diagnosis | 工业机械核心部件故障诊断助手

> 基于规则引擎 + RAG 向量检索的轴承/电机智能故障诊断系统

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

## 功能特性

- **规则引擎诊断** — 8 条专家规则，关键词匹配 + 置信度评分，毫秒级响应
- **知识库查询** — 10 条结构化故障知识（5 轴承 + 5 电机），覆盖症状/原因/方案/预防
- **RAG 向量检索** — ChromaDB + Sentence Transformers，语义级知识检索
- **混合诊断** — 规则 + 向量双路融合，兼顾精准匹配与泛化能力
- **双界面** — Streamlit Web / 零依赖终端，按环境选择

## 快速开始

### 方式一：终端交互版（零依赖，推荐先试）

```bash
git clone https://github.com/AWTX550W/industrial-fault-diagnosis.git
cd industrial-fault-diagnosis
python demo.py
```

### 方式二：Streamlit Web 界面

```bash
pip install streamlit -i https://pypi.tuna.tsinghua.edu.cn/simple
streamlit run streamlit_app/app.py
```

### 方式三：RAG 向量检索（可选）

```bash
pip install chromadb sentence-transformers -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 诊断演示

```
请输入故障现象> 轴承振动大，有异常噪声，温度升高

  匹配到 1 条规则

  [1] 可能存在轴承内圈故障
      置信度: ████████████████████ 85%  |  匹配关键词: 振动, 温度升高
      故障名称: 内圈故障 (轴承)
      严重程度: 高
      相关部件: 轴承内圈, 滚子
      可能原因:
        * 疲劳磨损
        * 润滑不良
        * 安装不当
      解决方案:
        → 检查并更换轴承
        → 改善润滑条件
        → 调整安装间隙
      预防措施:
        ◇ 定期检查润滑状态
        ◇ 避免超负荷运行
        ◇ 定期测量振动值
```

### 测试用例覆盖

| 输入描述 | 诊断结果 | 置信度 | 状态 |
|---------|---------|--------|------|
| 轴承有异响温度升高振动大 | BF001 内圈故障 | 85% | PASS |
| 电机启动困难绕组发热 | MF003 绕组故障 | 85% | PASS |
| 轴承润滑不良 | BF004 润滑不良 | 80% | PASS |
| 电机转速异常振动 | MF002 振动异常 | 70% | PASS |

## 项目结构

```
industrial-fault-diagnosis/
├── demo.py                  # 终端交互 Demo（零依赖，推荐入口）
├── run.py                   # 启动/测试脚本
├── ARCHITECTURE.md          # 架构设计文档（lite/advanced 双版本）
│
├── knowledge_base/          # 故障知识库
│   ├── fault_data.json      # 10 条故障知识（结构化 JSON）
│   └── loader.py            # 知识库加载器 + 症状搜索
│
├── rules_engine/            # 规则引擎
│   ├── rules.json           # 8 条诊断规则（关键词 + 置信度）
│   ├── rules.yaml           # YAML 格式规则（备选）
│   └── engine.py            # 规则匹配引擎（支持 JSON/YAML）
│
├── rag_module/              # RAG 向量检索模块
│   ├── vector_store.py      # ChromaDB 持久化封装
│   ├── embedding.py         # Sentence Transformers 向量化
│   └── retriever.py         # 检索器（知识库 + 向量库集成）
│
├── streamlit_app/           # Streamlit Web 界面
│   └── app.py               # 3 Tab 界面（诊断/知识库/关于）
│
├── requirements_lite.txt    # 轻量版依赖（streamlit）
└── requirements_full.txt    # 进阶版依赖（+chromadb/sentence-transformers）
```

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| 规则引擎 | Python stdlib | JSON/YAML 规则解析，关键词匹配，零外部依赖 |
| 知识库 | JSON | 结构化存储：症状/原因/方案/预防/严重程度 |
| 向量数据库 | ChromaDB | 持久化向量存储，余弦相似度检索 |
| 文本嵌入 | Sentence Transformers | paraphrase-multilingual-MiniLM-L12-v2（中英文） |
| Web 界面 | Streamlit | 3 种诊断模式 + 知识库浏览 |

## 系统架构

```
用户输入故障现象
       │
       ▼
┌──────────────────────────────────┐
│         诊断引擎（双路并行）        │
│  ┌──────────┐    ┌────────────┐  │
│  │ 规则引擎  │    │ RAG 向量检索│  │
│  │ 关键词匹配│    │ 语义相似度  │  │
│  └────┬─────┘    └─────┬──────┘  │
└───────┼────────────────┼─────────┘
        │                │
        ▼                ▼
┌──────────────────────────────────┐
│         结果融合 + 知识库查询      │
│  置信度排序 → 故障详情 → 维护建议  │
└──────────────────────────────────┘
        │
        ▼
   诊断报告输出
```

## 面试亮点

1. **完整 AI 应用链路** — 知识库构建 → 规则匹配 → 向量检索 → 结果融合 → 可视化
2. **模块化设计** — 知识库 / 规则引擎 / RAG / 前端完全解耦，可独立替换升级
3. **零依赖兜底** — 终端版不依赖任何第三方库，装不上 pip 也能跑
4. **真实工业场景** — 轴承 + 电机故障诊断，非玩具项目，有实际应用价值
5. **渐进式架构** — 轻量版（规则）→ 进阶版（+ML），展示系统设计能力

## 后续优化方向

- [ ] 接入 CWRU 轴承振动信号数据集，增加基于 ML 的信号分类
- [ ] 支持多模态输入（设备照片 / 异常声音）
- [ ] 构建故障-原因-方案知识图谱
- [ ] 对接 IoT 设备数据实现实时监测
- [ ] FastAPI 接口封装，支持系统集成调用

## License

MIT
