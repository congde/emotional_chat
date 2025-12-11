# 心语机器人 - RAG系统实施步骤

## 概述

本文档详细说明了心语（HeartTalk）情感陪伴机器人的RAG（检索增强生成）系统实施过程，展示如何将专业心理健康知识库集成到AI对话系统中。

---

## 3.1 技术架构

```
RAG知识库系统
├── 知识库核心层 (knowledge_base.py)
│   ├── KnowledgeBaseManager - 知识库管理器
│   └── PsychologyKnowledgeLoader - 心理知识加载器
│
├── RAG服务层 (rag_service.py)
│   ├── RAGService - 检索增强生成服务
│   └── RAGIntegrationService - RAG集成服务
│
├── 路由层 (rag_router.py)
│   └── 提供RESTful API接口
│
└── Chat服务集成 (chat_service.py)
    └── 自动识别并使用RAG增强回复
```

**核心组件：**
- **向量存储**: ChromaDB
- **嵌入模型**: OpenAI text-embedding-ada-002
- **LLM模型**: GPT-4
- **文档处理**: LangChain + PyPDF

---

## 3.2 实施步骤

### 步骤1：加载并处理文档

```python
# backend/modules/rag/core/knowledge_base.py

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class KnowledgeBaseManager:
    """心理健康知识库管理器"""
    
    def __init__(self, persist_directory: str = "./chroma_db/psychology_kb"):
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None
        
        # 配置文档分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,          # 每块500字符
            chunk_overlap=50,        # 块间重叠50字符
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]
        )
    
    def load_pdf_documents(self, pdf_path: str) -> List[Document]:
        """加载PDF文档"""
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        logger.info(f"成功加载PDF文档，共 {len(docs)} 页")
        return docs
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档为小块"""
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"文档分割完成，共 {len(chunks)} 个文档块")
        return chunks
```

**实际使用示例：**

```python
# init_rag_knowledge.py

from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager

# 初始化知识库管理器
kb_manager = KnowledgeBaseManager()

# 加载PDF（如果有）
# docs = kb_manager.load_pdf_documents("psychology_guide.pdf")

# 或加载内置示例知识
loader = PsychologyKnowledgeLoader(kb_manager)
loader.load_sample_knowledge()  # 加载内置的6大类心理健康知识
```

**内置知识主题：**
1. 认知行为疗法（CBT）基础知识
2. 正念减压技术（MBSR）
3. 积极心理学实践技巧
4. 应对焦虑的具体策略
5. 改善睡眠的科学方法
6. 建立心理韧性的方法

---

### 步骤2：生成向量并存储

```python
# backend/modules/rag/core/knowledge_base.py

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from datetime import datetime

class KnowledgeBaseManager:
    
    def create_vectorstore(self, chunks: List[Document]) -> Chroma:
        """创建向量存储"""
        logger.info(f"开始创建向量存储，共 {len(chunks)} 个文档块")
        
        # 为每个文档块添加元数据
        for i, chunk in enumerate(chunks):
            if 'chunk_id' not in chunk.metadata:
                chunk.metadata['chunk_id'] = i
            if 'timestamp' not in chunk.metadata:
                chunk.metadata['timestamp'] = datetime.now().isoformat()
        
        # 创建向量存储并持久化
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        vectorstore.persist()
        
        self.vectorstore = vectorstore
        logger.info("向量存储创建完成并持久化")
        return vectorstore
    
    def load_vectorstore(self) -> Chroma:
        """加载已存在的向量存储"""
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        logger.info("向量存储加载成功")
        return self.vectorstore
    
    def search_similar(self, query: str, k: int = 3) -> List[Document]:
        """相似度搜索"""
        if self.vectorstore is None:
            self.load_vectorstore()
        
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"搜索完成，返回 {len(results)} 个结果")
        return results
```

**初始化知识库：**

```bash
# 方法1: 使用命令行脚本
python init_rag_knowledge.py

# 方法2: 通过API
curl -X POST http://localhost:8000/api/rag/init/sample
```

**输出示例：**
```
======================================================================
 心语机器人 - RAG知识库初始化
======================================================================

→ 步骤 1/3: 初始化知识库管理器...
✓ 知识库管理器初始化成功

→ 步骤 2/3: 加载心理健康知识...
✓ 心理健康知识加载成功

→ 步骤 3/3: 验证知识库...
✓ 知识库验证成功

----------------------------------------------------------------------
知识库统计信息:
  状态: 就绪
  文档数量: 150
  存储位置: ./chroma_db/psychology_kb
  嵌入模型: OpenAI Ada-002
----------------------------------------------------------------------
```

---

### 步骤3：实现检索与生成链路

```python
# backend/modules/rag/services/rag_service.py

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

class RAGService:
    """RAG检索增强生成服务"""
    
    def __init__(self, kb_manager: Optional[KnowledgeBaseManager] = None):
        if kb_manager is None:
            kb_manager = KnowledgeBaseManager()
            kb_manager.load_vectorstore()
        
        self.kb_manager = kb_manager
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        
        # 心理健康专用prompt模板
        self.prompt_template = PromptTemplate(
            template="""你是"心语"，一个专业的心理健康陪伴机器人。

参考知识：
{context}

用户问题：{question}

请基于上述专业知识，用温暖、共情和专业的语气回答用户。注意：
1. 优先使用知识库中的科学方法和技巧
2. 用通俗易懂的语言解释专业概念
3. 提供具体可操作的建议
4. 表达共情和支持
5. 如果知识库中有相关练习或技巧，详细说明步骤
6. 询问用户是否需要进一步的指导或陪伴

回答：""",
            input_variables=["context", "question"]
        )
    
    def create_qa_chain(self, search_k: int = 3) -> RetrievalQA:
        """创建QA链"""
        retriever = self.kb_manager.get_retriever(search_kwargs={"k": search_k})
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
        return qa_chain
    
    def ask(self, question: str, search_k: int = 3) -> Dict[str, Any]:
        """向知识库提问"""
        # 创建QA链
        qa_chain = self.create_qa_chain(search_k)
        
        # 执行查询
        result = qa_chain({"query": question})
        
        # 提取答案和来源
        answer = result["result"]
        source_documents = result.get("source_documents", [])
        
        # 整理来源信息
        sources = []
        for doc in source_documents:
            source_info = {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question,
            "knowledge_count": len(sources)
        }
    
    def ask_with_context(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_emotion: Optional[str] = None,
        search_k: int = 3
    ) -> Dict[str, Any]:
        """结合对话上下文和用户情绪的知识问答"""
        # 检索相关知识
        knowledge_docs = self.kb_manager.search_similar(question, k=search_k)
        
        # 构建知识上下文
        knowledge_context = "\n\n".join([
            f"【知识{i+1}】{doc.page_content}"
            for i, doc in enumerate(knowledge_docs)
        ])
        
        # 构建对话历史上下文
        history_context = ""
        if conversation_history:
            recent_history = conversation_history[-3:]
            history_lines = [
                f"{'用户' if msg['role']=='user' else '心语'}: {msg['content']}"
                for msg in recent_history
            ]
            history_context = "\n".join(history_lines)
        
        # 构建情绪上下文
        emotion_context = f"用户当前情绪: {user_emotion}" if user_emotion else ""
        
        # 构建完整prompt
        enhanced_prompt = f"""你是"心语"，一个专业的心理健康陪伴机器人。

{emotion_context}

最近对话：
{history_context}

参考的专业知识：
{knowledge_context}

用户当前问题：{question}

请基于上述专业知识和对话上下文，用温暖、共情和专业的语气回答用户。"""
        
        # 使用LLM生成回答
        response = self.llm.predict(enhanced_prompt)
        
        # 整理来源信息
        sources = [
            {
                "content": doc.page_content[:200] + "...",
                "metadata": doc.metadata
            }
            for doc in knowledge_docs
        ]
        
        return {
            "answer": response,
            "sources": sources,
            "question": question,
            "knowledge_count": len(sources),
            "used_emotion_context": user_emotion is not None,
            "used_history_context": conversation_history is not None
        }


class RAGIntegrationService:
    """RAG集成服务 - 智能判断何时使用RAG"""
    
    def __init__(self, rag_service: Optional[RAGService] = None):
        self.rag_service = rag_service or RAGService()
    
    def should_use_rag(self, message: str, emotion: Optional[str] = None) -> bool:
        """判断是否应该使用RAG"""
        # 触发RAG的关键词
        rag_triggers = [
            "怎么办", "如何", "方法", "建议", "技巧", "练习",
            "失眠", "焦虑", "抑郁", "压力", "紧张", "担心",
            "正念", "冥想", "放松", "呼吸", "认知", "行为"
        ]
        
        # 需要专业建议的情绪
        professional_emotions = [
            "焦虑", "抑郁", "压力大", "紧张", "恐惧", "悲伤"
        ]
        
        # 检查是否触发
        has_trigger = any(trigger in message.lower() for trigger in rag_triggers)
        needs_professional = emotion and any(prof in emotion for prof in professional_emotions)
        rag_available = self.rag_service.is_knowledge_available()
        
        return (has_trigger or needs_professional) and rag_available
    
    def enhance_response(
        self,
        message: str,
        emotion: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """增强回复"""
        if not self.should_use_rag(message, emotion):
            return {
                "use_rag": False,
                "reason": "当前对话不需要专业知识库支持"
            }
        
        # 使用RAG生成回答
        result = self.rag_service.ask_with_context(
            question=message,
            conversation_history=conversation_history,
            user_emotion=emotion,
            search_k=3
        )
        
        result["use_rag"] = True
        return result
```

**API使用示例：**

```python
import requests

# 方法1: 直接向知识库提问
response = requests.post(
    "http://localhost:8000/api/rag/ask",
    json={
        "question": "我最近总是失眠，怎么办？",
        "search_k": 3
    }
)

# 方法2: 带上下文的问答
response = requests.post(
    "http://localhost:8000/api/rag/ask/context",
    json={
        "question": "有什么具体的方法可以帮助我入睡吗？",
        "user_emotion": "焦虑",
        "conversation_history": [
            {"role": "user", "content": "我最近压力很大"},
            {"role": "assistant", "content": "我理解你现在的压力..."}
        ],
        "search_k": 3
    }
)

# 方法3: 通过Chat API自动使用RAG（推荐）
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "我经常失眠，有什么科学的方法吗？",
        "user_id": "user123",
        "session_id": "session456"
    }
)
# Chat API会自动判断是否需要使用RAG
```

---

### 步骤4：测试效果

#### 4.1 运行测试脚本

```bash
# 完整系统测试
python test_rag_system.py

# RAG效果对比演示
python demo_rag_comparison.py
```

#### 4.2 测试结果对比

**测试案例：失眠问题**

**用户：** "我最近总是失眠，怎么办？"

**❌ 无RAG版本（通用回复）：**
```
你可以试试听听轻音乐、喝杯热牛奶，或者睡前不要玩手机。
保持规律作息也很重要。
```

**✅ RAG增强版本（专业建议）：**
```
我理解失眠的困扰，这确实会影响白天的状态和情绪。失眠常常与过度思考和
身体紧张有关。我想分享一个经过科学验证的方法——正念身体扫描练习：

具体步骤：
1. 平躺在床上，保持舒适的姿势
2. 闭上眼睛，开始深呼吸几次
3. 将注意力依次集中在身体各个部位：
   • 从脚趾开始，感受脚趾的感觉
   • 逐步向上：脚掌 → 小腿 → 大腿 → 腹部 → 胸部 → 手臂 → 头部
4. 观察每个部位的感觉，不做任何评判
5. 如果感到紧张，想象呼吸流经该部位，带来放松
6. 如果思绪飘走，温柔地将注意力带回身体

临床研究表明，持续8周的正念身体扫描练习可以显著改善失眠问题，特别是
入睡困难和睡眠质量。

除此之外，睡眠卫生也很重要：
• 每天同一时间起床和睡觉（包括周末）
• 睡前1小时避免电子屏幕（蓝光会影响褪黑素分泌）
• 保持卧室凉爽（18-20°C最佳）、黑暗和安静
• 如果20分钟内睡不着，起床做些安静的活动，直到感到困倦再回床上

需要我现在陪你做一遍身体扫描练习吗？或者你想了解更多关于改善睡眠的
方法？

💡 [此回复基于 3 个专业知识源]
来源：
  [1] 正念减压技术（MBSR）- 内置知识库
  [2] 改善睡眠的科学方法 - 内置知识库
  [3] 认知行为疗法（CBT）基础知识 - 内置知识库
```

#### 4.3 效果对比分析

| 维度 | 无RAG版本 | RAG增强版本 |
|------|----------|------------|
| **专业性** | ⭐⭐ 通用建议 | ⭐⭐⭐⭐⭐ 专业心理学知识 |
| **可操作性** | ⭐⭐ 模糊建议 | ⭐⭐⭐⭐⭐ 详细步骤说明 |
| **可信度** | ⭐⭐ 无来源引用 | ⭐⭐⭐⭐⭐ 标注知识来源 |
| **科学性** | ⭐⭐ 常识性建议 | ⭐⭐⭐⭐⭐ 临床研究支持 |
| **个性化** | ⭐⭐ 通用回复 | ⭐⭐⭐⭐⭐ 结合情绪和历史 |

#### 4.4 完整测试输出

```
======================================================================
| 心语机器人 - RAG知识库系统测试
| 测试时间: 2025-10-16 14:30:00
======================================================================

======================================================================
| 1. 测试知识库管理器
======================================================================

→ 初始化知识库管理器...
✓ 知识库管理器初始化成功

→ 加载示例心理健康知识...
✓ 示例知识加载成功

→ 获取知识库统计信息...
✓ 统计信息:
  • status: 就绪
  • document_count: 150
  • persist_directory: ./chroma_db/psychology_kb
  • embedding_model: OpenAI Ada-002

======================================================================
| 2. 测试相似度搜索
======================================================================

------------------------------------------------------------
| 查询: 我最近总是失眠，怎么办？
------------------------------------------------------------

找到 3 个相关文档:

【结果 1】相似度: 0.2345
主题: 改善睡眠的科学方法
来源: 内置知识库
内容预览: 良好的睡眠对心理健康至关重要。睡眠卫生建议...

【结果 2】相似度: 0.2567
主题: 正念减压技术（MBSR）
来源: 内置知识库
内容预览: 身体扫描练习是一种有效的放松技术...

【结果 3】相似度: 0.2891
主题: 应对焦虑的具体策略
来源: 内置知识库
内容预览: 深呼吸技术可以快速激活副交感神经系统...

======================================================================
| 测试摘要
======================================================================

总测试数: 6
通过: 6 ✓
失败: 0 ✗
成功率: 100.0%

详细结果:
  ✓ 知识库管理器: 通过
  ✓ 相似度搜索: 通过
  ✓ RAG问答: 通过
  ✓ 带上下文RAG问答: 通过
  ✓ RAG集成服务: 通过
  ✓ 完整工作流程: 通过

======================================================================

🎉 所有测试通过！RAG系统运行正常。
```

---

## 3.3 RAG增强的优势总结

### ✓ 专业性提升
- **无RAG**: 通用的安慰和建议，如"试试听音乐、喝热牛奶"
- **有RAG**: 基于认知行为疗法、正念减压等权威心理学知识

### ✓ 可操作性增强
- **无RAG**: 模糊的建议，缺乏具体步骤
- **有RAG**: 详细的分步指导，用户可以立即实践

### ✓ 可信度提升
- **无RAG**: 无知识来源，用户难以信任
- **有RAG**: 引用专业知识源，增强可信度和专业性

### ✓ 科学性保障
- **无RAG**: 基于常识的建议
- **有RAG**: 包含临床研究支持的方法，如"8周正念练习显著改善失眠"

### ✓ 个性化回复
- **无RAG**: 千篇一律的通用回复
- **有RAG**: 结合用户情绪、对话历史，生成定制化专业建议

---

## 3.4 系统配置与部署

### 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 主要新增依赖：
# - pypdf==3.17.4          # PDF文档处理
# - langchain==0.0.350     # RAG框架
# - chromadb==0.4.18       # 向量数据库
# - openai==1.3.7          # OpenAI API
# - python-multipart       # 文件上传
```

### 初始化流程

```bash
# 1. 初始化知识库
python init_rag_knowledge.py

# 2. 验证系统
python test_rag_system.py

# 3. 查看对比演示
python demo_rag_comparison.py

# 4. 启动服务
python run_backend.py
```

### API接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/rag/status` | GET | 获取知识库状态 |
| `/api/rag/init/sample` | POST | 初始化示例知识 |
| `/api/rag/upload/pdf` | POST | 上传PDF文档 |
| `/api/rag/ask` | POST | 知识问答 |
| `/api/rag/ask/context` | POST | 带上下文问答 |
| `/api/rag/search` | POST | 搜索知识 |
| `/api/rag/examples` | GET | 获取示例问题 |

---

## 3.5 核心代码文件

| 文件路径 | 功能说明 |
|---------|----------|
| `backend/modules/rag/core/knowledge_base.py` | 知识库管理核心，负责文档加载、分块、向量化、检索 |
| `backend/modules/rag/services/rag_service.py` | RAG服务层，实现检索增强生成、智能触发判断 |
| `backend/modules/rag/routers/rag_router.py` | RAG API路由，提供RESTful接口 |
| `init_rag_knowledge.py` | 知识库初始化脚本 |
| `test_rag_system.py` | 完整系统测试脚本 |
| `demo_rag_comparison.py` | RAG效果对比演示脚本 |

---

## 3.6 技术参数说明

| 参数 | 值 | 说明 |
|------|---|------|
| **chunk_size** | 500 | 文档分块大小（字符数） |
| **chunk_overlap** | 50 | 文档块间重叠（字符数） |
| **embedding_model** | text-embedding-ada-002 | OpenAI嵌入模型 |
| **embedding_dimension** | 1536 | 向量维度 |
| **llm_model** | gpt-4 | 生成模型 |
| **temperature** | 0.7 | 生成温度（平衡创造性和准确性） |
| **search_k** | 3 | 默认检索文档数量 |
| **persist_directory** | ./chroma_db/psychology_kb | 向量数据库存储路径 |

---

## 3.7 分块策略详解

RAG系统的性能很大程度上取决于文档分块的质量。不当的分块会破坏语义边界，导致检索到的片段信息残缺、上下文缺失。本系统实现了多种分块策略，可根据文档类型自动选择最佳策略。

### 3.7.1 基础分块策略

#### 固定长度分块（Character）

**策略说明**: 按预设字符数直接切分，不考虑文本结构。

**优点**: 实现简单、速度快、对任意文本通用。

**缺点**: 容易破坏语义边界；块过大容易引入噪声，过小则上下文不足。

**适用场景**: 结构性弱的纯文本，或数据预处理初期的基线方案。

**参数建议（中文语料）**:
- `chunk_size`: 300-800 字符
- `chunk_overlap`: 10%-20%

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import CharacterTextSplitter

splitter = CharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=90
)
chunks = splitter.split_documents(documents)
```

#### 基于句子的分块（Sentence）

**策略说明**: 先按句子切分，再将若干句子聚合成满足chunk_size的块。

**优点**: 句子级完整性最好，对问句/答句映射友好，便于高质量引用。

**缺点**: 中文分句需特别处理；仅句子级切分可能导致块过短。

**适用场景**: 法律法规、新闻、公告、FAQ等以句子为主的文本。

**中文分句**: 系统使用正则表达式识别中文标点（。！？；）进行分句。

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import SentenceTextSplitter

splitter = SentenceTextSplitter(
    chunk_size=600,
    chunk_overlap=80
)
chunks = splitter.split_documents(documents)
```

#### 递归字符分块（Recursive）

**策略说明**: 给定一组由"粗到细"的分隔符（段落→换行→空格→字符），自上而下递归切分，在不超出chunk_size的前提下尽量保留自然语义边界。

**优点**: 在"保持语义边界"和"控制块大小"之间取得稳健平衡，对大多数文本即插即用。

**缺点**: 分隔符配置不当会导致块粒度失衡；极度格式化文本（表格/代码）效果一般。

**适用场景**: 综合性语料、说明文档、报告、知识库条目。

**分隔符优先级**:
1. 段落: `\n\n`
2. 换行: `\n`
3. 中文标点: `。！？；`
4. 英文标点: `. ! ? ;`
5. 空格: ` `
6. 字符级: `""`（兜底）

**使用示例**:
```python
from backend.modules.rag.core.langchain_compat import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]
)
chunks = splitter.split_documents(documents)
```

### 3.7.2 结构感知分块策略

#### Markdown结构化分块（Structure）

**策略说明**: 利用文档固有结构（标题层级、列表、代码块、表格）作为分块边界，逻辑清晰、可追溯性强。

**优点**: 保证上下文完整性，提升检索信噪比，保留标题路径便于溯源。

**缺点**: 仅适用于结构化文档；需要文档有清晰的标题层级。

**适用场景**: Markdown文档、技术手册、API文档、结构化知识库。

**实施步骤**:
1. 解析Markdown结构（识别标题、代码块、表格）
2. 生成章节（以标题为父节点）
3. 二次切分（章节超出chunk_size时按段落切分）
4. 合并短块（低于min_chunk的块与相邻块合并）
5. 添加标题路径前缀

**参数建议**:
- `chunk_size`: 600-1000 字符
- `min_chunk`: 200-300 字符
- `chunk_overlap`: 10%-15%

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import MarkdownStructureSplitter

splitter = MarkdownStructureSplitter(
    chunk_size=900,
    min_chunk=250,
    overlap_ratio=0.1
)
chunks = splitter.split_documents(documents)
```

**元数据增强**: 每个块包含：
- `section_title`: 章节标题
- `breadcrumbs`: 标题路径（如 ["指南", "安装", "步骤1"]）
- `section_level`: 标题层级（1-6）

#### 对话式分块（Dialogue）

**策略说明**: 以"轮次/说话人"为边界，优先按对话邻接对和小段话题窗口聚合。

**优点**: 保持对话上下文完整，便于理解问答对关系。

**缺点**: 仅适用于对话格式文档。

**适用场景**: 客服对话、访谈、会议纪要、技术支持工单等多轮交流。

**参数建议**:
- `max_turns`: 6-12 轮
- `max_chars`: 600-1000 字符
- `overlap_turns`: 1-2 轮

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import DialogueSplitter

splitter = DialogueSplitter(
    max_turns=10,
    max_chars=900,
    overlap_turns=2
)
chunks = splitter.split_documents(documents)
```

### 3.7.3 高级分块策略

#### 小-大分块（Small-Big）

**策略说明**: 用"小粒度块"（句子/短句）做高精度召回，定位到最相关的微片段；再将其"所在的大粒度块"（段落/小节）作为上下文送入LLM。

**优点**: 兼顾精确性与上下文完整性，检索精度高且答案连贯。

**缺点**: 索引体积增大，检索时需要额外的聚合步骤。

**适用场景**: 需要高精度检索和完整上下文的场景。

**工作流程**:
1. **离线构建索引**:
   - 创建小块索引（句子级，用于召回）
   - 创建大块存储（段落级，用于上下文）
   - 建立小块到大块的映射关系

2. **在线检索**:
   - 用小块索引召回top_k个小块
   - 按parent_id分组，选出top_m个大块候选
   - 在父块中高亮或保留命中小句附近的上下文

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import SmallBigChunking

splitter = SmallBigChunking(
    small_chunk_size=200,  # 小块用于召回
    big_chunk_size=900,    # 大块用于上下文
    small_overlap=50,
    big_overlap=90
)
chunks = splitter.split_documents(documents)
```

#### 父子段分块（Parent-Child）

**策略说明**: 将文档按结构单元（父块）切分，再在每个父块内切出子块（句子/短段）。为子块建向量索引以做高精度召回，检索时先召回子块，再扩展到父块或父块中的局部窗口。

**优点**: 句级证据准确 + 段/小节级上下文完整，可追溯性强。

**缺点**: 索引结构复杂，需要维护父子映射关系。

**适用场景**: 结构清晰的说明文、手册、白皮书、法规、FAQ聚合页。

**工作流程**:
1. **结构粗切（父块）**: 按标题层级/段落切出父块
2. **精细切分（子块）**: 在父块内部以句子/子句为单位切分
3. **建索引**: 子块向量索引（用于召回），父块存储（用于上下文）
4. **检索组装**: 召回子块 → 按parent_id聚合 → 在父块中抽取命中句邻域

**使用示例**:
```python
from backend.modules.rag.core.chunking_strategies import ParentChildChunking

splitter = ParentChildChunking(
    parent_chunk_size=1000,  # 父块大小
    child_chunk_size=300,   # 子块大小
    parent_overlap=100,
    child_overlap=50
)
chunks = splitter.split_documents(documents)
```

### 3.7.4 自动策略选择

系统实现了智能策略选择器，可根据文档类型自动选择最佳分块策略。

**检测逻辑**:
1. **对话检测**: 识别对话格式（User:、Assistant:等），使用`dialogue`策略
2. **Markdown检测**: 识别Markdown结构（标题、代码块等），使用`structure`策略
3. **长文档检测**: 段落数>10且有结构，使用`parent_child`策略
4. **长句子检测**: 平均句子长度>100，使用`sentence`策略
5. **默认**: 使用`recursive`策略

**使用示例**:
```python
from backend.modules.rag.core.knowledge_base import KnowledgeBaseManager

# 自动选择策略
kb_manager = KnowledgeBaseManager(
    chunking_strategy="auto",  # 自动选择
    chunk_size=500,
    chunk_overlap=50
)

# 手动指定策略
kb_manager = KnowledgeBaseManager(
    chunking_strategy="structure",  # 强制使用结构感知分块
    chunk_size=900,
    chunk_overlap=90
)

# 在分块时指定策略
chunks = kb_manager.split_documents(documents, strategy="small_big")
```

**策略对比表**:

| 策略 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **character** | 纯文本、基线方案 | 简单快速 | 破坏语义边界 |
| **sentence** | 句子为主文本 | 句子完整性好 | 块可能过短 |
| **recursive** | 综合语料 | 平衡性好 | 格式化文本效果一般 |
| **structure** | Markdown文档 | 结构清晰、可追溯 | 仅适用结构化文档 |
| **dialogue** | 对话文本 | 保持对话上下文 | 仅适用对话格式 |
| **small_big** | 高精度检索 | 精确+完整 | 索引体积大 |
| **parent_child** | 结构化长文档 | 句级准确+段级完整 | 结构复杂 |

---

## 3.8 策略选择指南

### 3.8.1 如何选择分块策略

**决策流程**:

1. **文档类型识别**
   - 对话格式 → `dialogue`
   - Markdown文档 → `structure`
   - 长文档（>10段落）且有结构 → `parent_child`
   - 长句子（平均>100字符） → `sentence`
   - 其他 → `recursive`

2. **性能要求**
   - 需要高精度召回 → `small_big` 或 `parent_child`
   - 需要快速处理 → `character` 或 `recursive`
   - 需要可追溯性 → `structure` 或 `parent_child`

3. **文档特征**
   - 有清晰标题层级 → `structure`
   - 句子为主 → `sentence`
   - 无特殊结构 → `recursive`

### 3.8.2 参数调优建议

**chunk_size调优**:
- 中文语料: 300-800 字符起步
- 技术文档: 可适当增大到 900-1200 字符
- 对话文本: 600-1000 字符

**chunk_overlap调优**:
- 一般场景: 10%-20%
- 需要强上下文连续性: 15%-25%
- 注意: 超过30%通常导致索引体积显著上升，收益有限

**调优流程**:
1. 固定检索与重排，只动分块参数
2. 用验证集计算 Recall@k、nDCG、MRR
3. 观察块长分布：长尾太长则收紧chunk_size，过短则放宽
4. 评估答案事实性（faithfulness）和可追溯性

### 3.8.3 实际应用示例

**示例1: 心理健康知识库（Markdown格式）**
```python
kb_manager = KnowledgeBaseManager(
    chunking_strategy="structure",  # 使用结构感知分块
    chunk_size=900,
    chunk_overlap=90
)
```

**示例2: 客服对话记录**
```python
kb_manager = KnowledgeBaseManager(
    chunking_strategy="dialogue",  # 使用对话分块
    chunk_size=800,
    chunk_overlap=80
)
```

**示例3: 技术文档（需要高精度）**
```python
kb_manager = KnowledgeBaseManager(
    chunking_strategy="parent_child",  # 使用父子段分块
    chunk_size=1000,
    chunk_overlap=100
)
```

**示例4: 自动选择（推荐）**
```python
kb_manager = KnowledgeBaseManager(
    chunking_strategy="auto",  # 自动选择最佳策略
    chunk_size=500,
    chunk_overlap=50
)
```

---

## 3.9 结论

通过RAG技术，"心语"情感陪伴机器人实现了从**"情感倾听者"到"专业心理助手"**的升级：

1. **知识驱动**: 基于权威心理学知识库，而非仅依赖LLM的训练数据
2. **专业可信**: 引用知识来源，提供科学依据，增强用户信任
3. **实用可操作**: 提供详细的步骤指导，用户可以立即实践
4. **智能触发**: 自动识别需要专业知识的场景，无缝集成到对话流程
5. **持续扩展**: 支持上传PDF文档，不断丰富知识库内容

RAG系统让AI不仅能共情用户情绪，更能提供科学、专业、可操作的心理健康建议，真正成为用户的专业心理陪伴助手。

---

**文档版本**: v2.0  
**创建日期**: 2025-10-16  
**更新日期**: 2025-01-XX  
**项目**: 心语（HeartTalk）情感陪伴机器人  
**开发团队**: 心语机器人项目组

---

## 更新日志

### v2.0 (2025-01-XX)
- ✨ 新增多种分块策略支持（基础分块、结构感知、高级分块）
- ✨ 实现自动策略选择机制
- ✨ 添加Markdown结构化分块
- ✨ 添加对话式分块
- ✨ 添加小-大分块和父子段分块策略
- 📝 更新文档，补充分块策略详解和选择指南

### v1.0 (2025-10-16)
- 初始版本，基础RAG功能实现

