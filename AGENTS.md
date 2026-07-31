# AGENTS.md

本文件适用于整个仓库。若子目录以后出现更具体的 `AGENTS.md`，则子目录规则优先。

这是一个经过多轮演进的老项目：同一能力可能同时存在“当前分层实现、历史单体实现、实验性实现”。工作的首要原则是先确认真实运行链路，再做最小、可验证、可回退的修改。不要仅凭文件名或 README 中的描述判断代码是否在线上路径中。

## 1. 项目目标与不可破坏的底线

“心语”是面向情感支持场景的 AI 对话应用，提供情绪与意图识别、长期记忆、RAG、Agent/Skills、附件与流式回复、反馈和自动评估。

它不是医疗诊断或心理治疗产品。任何改动都必须遵守以下底线：

- 不把模型输出包装成诊断、处方或专业治疗结论。
- 不弱化自伤、自杀、暴力、危机或高风险意图的识别、升级和兜底逻辑。
- 危机安全策略优先于“更自然”“更简短”“更像真人”等风格目标。
- 不把真实对话、用户画像、记忆、附件、模型密钥或数据库凭据放进提交、测试快照和日志。
- 记忆、会话、情绪记录和向量数据必须按 `user_id`、`session_id` 隔离。任何读取、更新、删除都要验证归属。
- 外部 URL、上传文件、Hermes 工作区和工具调用都是不可信输入，不能扩大访问范围或默认开启危险能力。

安全策略资料位于 `knowledge_base/organization_policy/crisis_intervention_protocol.md`。涉及危机处理时，先阅读该文件以及相关敏感内容实现文档。

## 2. 技术栈与实际版本边界

- 后端：Python 3.10/3.11 为主要开发目标，FastAPI、Uvicorn。
- 数据模型：Pydantic v1，项目明确限制 `<2.0.0`。
- ORM：SQLAlchemy 1.4，项目明确限制 `<2.0.0`。
- 数据库：MySQL 为主要部署方案；本地可使用 SQLite；Redis 为可选能力。
- 向量检索：ChromaDB 0.4 系列、LangChain 0.2 系列。
- 模型接入：OpenAI-compatible API，可切换智谱、通义、OpenAI 或其他兼容网关。
- 前端：React 18、Create React App 5、Axios、styled-components、react-markdown。
- 格式约定：Black 100 列，Ruff Python 3.10。

注意仓库存在版本漂移：

- `pyproject.toml` 声明 Python `>=3.10`，但现有 Dockerfile 和 GitHub Actions 仍使用 Python 3.9。
- 不要在普通功能修改中顺手统一版本。若使用 Python 3.10+ 语法，必须同时说明 Docker/CI 的兼容影响；若任务是升级运行时，则一起更新 Dockerfile、CI、文档和依赖锁定。
- `requirements.txt` 是现有安装和 Docker 路径使用的依赖来源；`pyproject.toml` 同时承担项目元数据与开发工具配置。新增或删除 Python 依赖时，两者都要核对。

## 3. 阅读顺序

开始修改前，按任务范围阅读：

1. 根目录 `README.md` 和与功能对应的 `docs/` 文档。
2. `backend/app.py`，确认路由是否真实注册。
3. 对应的 `backend/routers/*.py`，确认请求、响应和异常行为。
4. 路由实际导入的 service、model 和 database 实现。
5. `frontend/src/services/ChatAPI.js` 及调用该接口的 hook/component。
6. 对应测试和迁移。

不要跳过第 2 步。这个仓库中“有实现”不等于“当前应用已注册”。

## 4. 当前权威入口与历史入口

### 4.1 启动入口

| 文件 | 当前角色 | 修改规则 |
| --- | --- | --- |
| `main.py` | 本地开发组合入口，同时启动后端和 React 开发服务器 | 只放进程编排，不放业务逻辑 |
| `run_backend.py` | 当前独立后端入口，检查依赖并初始化 RAG 后启动 | 使用 `backend.app:app`；启动副作用要谨慎 |
| `backend/app.py` | 当前 FastAPI 应用工厂、CORS、静态目录和路由装配入口 | 新路由必须在这里或其导入的聚合模块中注册 |
| `backend/main.py` | 历史单体 FastAPI 应用，保留旧的多模态和部分旧接口 | 除非任务明确要求兼容旧入口，否则不要继续添加功能 |
| `scripts/simple_backend.py` | 旧 Python 环境兼容后端 | 不是正式实现 |
| `scripts/quick_start.py` | 旧版全量初始化入口 | 不应成为新功能依赖 |

正式后端导入目标是：

```text
backend.app:app
```

不要把 `backend.main:app` 当作当前应用，也不要因为旧单体中存在某个接口就认为前端能访问它。

### 4.2 当前应用装配

`backend/app.py` 在模块导入时执行 `app = create_app()`，因此导入应用可能同时导入并初始化聊天、RAG、意图、Agent 等服务。修改模块级初始化时要考虑：

- 测试收集阶段不能依赖真实 LLM、MySQL、Redis 或外网。
- 可选依赖失败应安全降级，不应让无关路由和 `/health` 无法导入。
- 不要在 import 阶段执行不可逆写操作、长时间网络调用或全量重建向量库。
- `run_backend.py` 已承担启动前知识库初始化；不要在多个入口重复做昂贵初始化。

当前还有一个 Windows 基线问题：`backend/database.py` 会在 import 阶段探测 MySQL；MySQL 不可用时本应回退 SQLite，但 GBK 控制台可能无法输出警告中的 Unicode 符号，进而抛出 `UnicodeEncodeError`。排查应用导入时先设置 `PYTHONUTF8=1`，并显式选择隔离的 SQLite。不要把这个编码异常误判成路由或模型故障，也不要通过删除本地数据库来规避。

## 5. 后端目录与职责

### 5.1 主要目录

| 路径 | 职责 | 注意事项 |
| --- | --- | --- |
| `backend/routers/` | HTTP、SSE、WebSocket 路由 | 参数解析、状态码、调用 service；避免堆积业务逻辑 |
| `backend/services/` | 聊天、上下文、记忆、个性化、反馈、性能等业务编排 | 当前主聊天链路在这里 |
| `backend/modules/` | RAG、LLM、Intent、多模态、模块化 Agent | 模块内部可有自己的 models/routers/services |
| `backend/agent/` | 较早期但仍被当前 `/agent` 路由使用的 Agent 核心与工具 | 与 `backend/modules/agent/` 重复，先看真实 import |
| `backend/runtime/` | 新一代 Runtime + Skills、会话、策略、预算、工具协议 | 不是所有代码都接入主聊天链路 |
| `backend/core/` | 通用配置、异常、接口、校验和工具 | 其中配置系统不是主业务唯一配置源 |
| `backend/hermes/` | 受限工作区自动化、意图与 dispatch | 默认关闭；涉及文件/网页/shell 权限 |
| `backend/plugins/` | 天气等聊天引擎插件 | 第三方 API 失败必须降级 |
| `backend/ab_testing/` | A/B 分组、事件与分析 | 当前 `backend/app.py` 未注册其 router |
| `backend/tests/` | 当前自动测试 | 测试量较少，改动功能时补回归测试 |

### 5.2 同名实现陷阱

- `backend/routers/agent.py` 与 `backend/modules/agent/routers/agent_router.py` 都声明 `/agent`。当前应用注册的是前者。
- `backend/models.py` 与 `backend/schemas/` 都有 Pydantic 模型。当前主聊天路由从 `backend.models` 导入 `ChatRequest`/`ChatResponse`，不是 `backend.schemas.chat_schemas`。
- 根 `config.py` 与 `backend/core/config.py` 是两套配置体系，变量命名不同。
- 根 `backend/main.py` 与 `backend/app.py` 都能创建 FastAPI app，但当前运行路径是后者。
- `backend/agent/` 与 `backend/modules/agent/` 并存，修改前沿当前 router/service 的 import 链追踪。
- `alembic/versions/` 与 `backend/migrations/*.sql` 并存；正式增量迁移优先 Alembic，历史 SQL 文件不能自动视为当前迁移链。

不要为了“消除重复”直接删除其中一套。先证明没有导入方、脚本、部署或文档依赖，再单独进行迁移型重构。

## 6. 当前路由地图

以下是 `backend/app.py` 当前装配的路由族：

| 前缀 | 实现 | 用途 | 装配方式 |
| --- | --- | --- | --- |
| `/chat` | `backend/routers/chat.py` | 普通聊天、附件、SSE、会话历史和删除 | 必选 |
| `/memory` | `backend/routers/memory.py` | 用户记忆查询、搜索、重要度和画像 | 必选 |
| `/feedback` | `backend/routers/feedback.py` | 用户反馈与统计 | 必选 |
| `/evaluation` | `backend/routers/evaluation.py` | 自动评估、批量评估、人工校验 | 必选 |
| `/api/emotion` | `backend/routers/emotion_analysis.py` | 情绪分析、趋势和报告 | 必选 |
| `/api/personalization` | `backend/routers/personalization.py` | 角色模板和用户个性化配置 | 必选 |
| `/api/rag` | `backend/modules/rag/routers/rag_router.py` | 知识库初始化、上传、查询和搜索 | 必选 |
| `/enhanced-chat` | `backend/routers/enhanced_chat.py` | 增强聊天和洞察 | import 成功时注册 |
| `/agent` | `backend/routers/agent.py` | Agent 聊天、状态、记忆、工具和回访 | import 成功时注册 |
| `/hermes` | `backend/routers/hermes.py` | 工作区自动化状态与 dispatch | import 成功时注册，实际能力受配置开关限制 |
| `/intent` | `backend/modules/intent/routers/intent_router.py` | 意图检测、Prompt 构建和批处理 | import 成功时注册 |
| `/performance` | `backend/routers/performance.py` | 指标、缓存和优化配置 | 与性能模块一起可选注册 |
| `/streaming` | `backend/routers/streaming_chat.py` | 另一套流式 HTTP/WebSocket API | 与性能模块一起可选注册 |
| `/`, `/health`, `/system/info` | `backend/app.py` | 根信息、健康检查、系统信息 | 必选 |

当前没有由 `backend/app.py` 注册的实现：

- `backend/routers/ab_testing.py` 中的 `/ab-testing`。
- `backend/main.py` 中的 `/multimodal/*`。
- 前端 `ChatAPI.js` 中仍保留的 `/knowledge` 和 `/emotion-examples` 调用。

若任务涉及这些接口，先决定是：

1. 将能力迁移并显式注册到当前 `backend.app`；
2. 删除或隐藏前端死入口；
3. 继续维护旧单体入口。

不要悄悄选择第 3 种。接口注册变化必须有最小 API 测试和文档说明。

## 7. 主聊天调用链

当前普通聊天大致沿以下路径运行：

```text
React useChat
  -> frontend/src/services/ChatAPI.js
  -> POST /chat/stream（multipart/form-data + SSE）
  -> backend/routers/chat.py
  -> ChatService
  -> 输入预处理 / Hermes 意图
  -> 情绪分析
  -> 意图识别与危机标记
  -> ContextService + MemoryService
  -> 可选 RAGIntegrationService
  -> 插件聊天引擎或 SimpleEmotionalChatEngine
  -> MySQL/SQLite 会话消息 + Chroma 记忆
  -> SSE token/done/error
```

非流式 `/chat/` 和 `/chat/simple` 也调用同一个 `ChatService`，但 `simple` 禁用记忆系统用于对比。

修改链路时必须注意：

- `ChatService` 在 router 模块加载时以全局实例创建，会触发多个可选组件初始化。
- 当前有效 `ChatRequest` 来自 `backend/models.py`，字段比 `backend/schemas/chat_schemas.py` 更宽松：`user_id` 可空，并带有 `deep_thinking`。
- `session_id` 为空时由服务生成 UUID；前端依赖 `done` 事件返回该 ID。
- RAG 分支和普通引擎分支的消息持久化路径不同，修改时要防止漏存或重复存储。
- 可选 RAG、Intent、插件引擎失败时应回落到基础聊天，而不是让整个请求崩溃。
- 不要用 `print` 新增可能含用户消息、上下文、密钥或完整模型响应的日志；使用项目 logger 并脱敏。
- 当前不少 router 使用宽泛 `except Exception`。新增代码不要吞掉 `HTTPException` 或把预期的 4xx 重新包装为 500。

## 8. 前后端契约

### 8.1 API 基址

前端使用：

```text
REACT_APP_API_URL
```

未设置时默认为 `http://localhost:8000`。前端配置放在 `frontend/.env.local`，不得提交。

### 8.2 流式聊天协议

前端主交互使用 `POST /chat/stream`，请求为 `FormData`：

- `message`
- `session_id`，新会话时传空字符串
- `user_id`
- `deep_thinking`，字符串 `"true"` 或 `"false"`
- `url_contents`，可选 JSON 字符串
- 一个或多个 `files`

响应是 SSE 风格的逐行 `data: <json>`。前端当前识别：

- `{"type":"token","content":"..."}`：追加文本。
- `{"type":"done","session_id":"...","emotion":"...","suggestions":[]}`：结束并保存会话。
- `{"type":"error","content":"..."}`：显示错误。
- `data: [DONE]`：会被忽略，不能代替结构化 `done` 事件。

修改事件字段、结束顺序或分隔符时，必须同步 `ChatAPI.sendMessageStreaming` 和 `useChat`，并测试跨 chunk 的半行 JSON、取消请求、服务端错误和无 token 完成。

### 8.3 会话与本地状态

前端依赖以下 localStorage key：

- `emotional_chat_user_id`
- `emotional_chat_current_session`
- `emotional_chat_theme`
- Skills 面板自己的导入技能 key

会话历史响应至少需要：

```json
{
  "session_id": "string",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "text",
      "emotion": "optional",
      "timestamp": "ISO datetime"
    }
  ]
}
```

用户会话列表响应至少需要 `sessions` 数组。空历史应返回空数组而不是 404，现有前端按此行为处理。

会话删除是不可逆操作。服务端不能只凭 `session_id` 删除跨用户数据；新增认证前，也必须把归属校验作为内部安全边界。

### 8.4 API 变更检查表

修改请求或响应时同步检查：

- 实际 router 使用的 Pydantic model；
- service 返回值；
- `frontend/src/services/ChatAPI.js`；
- `frontend/src/hooks/`；
- 使用接口的 component；
- SSE/HTTP 状态码；
- OpenAPI 示例和 `docs/API接口文档.md`；
- 兼容旧字段是否需要过渡期。

## 9. 数据与持久化

### 9.1 关系数据库

`backend/database.py` 定义 SQLAlchemy engine、session 和多数 ORM 表，包括：

- 用户、聊天会话、聊天消息；
- 情绪分析、知识、系统日志；
- 用户反馈、自动评估；
- 用户画像、个性化；
- A/B 实验、事件和分组。

数据库 URL 解析大致遵循：

1. `USE_SQLITE=1`：使用 `SQLITE_PATH`。
2. 显式 `DATABASE_URL`。
3. 由 `MYSQL_*` 组合 MySQL URL。
4. MySQL 不可用且允许 fallback 时，回退本地 SQLite。

生产环境若不允许回退，应设置 `USE_SQLITE_FALLBACK=0`。不要为了让本地测试通过而改变生产回退语义。

### 9.2 向量、上下文和运行时文件

| 路径 | 数据类型 | 默认处理 |
| --- | --- | --- |
| `knowledge_base/` | 受版本控制的内置知识资料 | 可审查修改，注意来源与安全性 |
| `chroma_db/` | Chroma 持久化向量库 | 本地生成，不提交、不手工批量编辑 |
| `data/` | SQLite、Runtime checkpoints 等 | 本地数据，不提交 |
| `context_storage/` | 上下文优化和 context-rot 存储 | 本地数据，不提交 |
| `uploads/` | 用户上传文件和生成文件 | 视为敏感数据，不提交 |
| `log/`, `logs/` | 应用、A/B 等日志 | 不提交真实内容 |
| `tmp/` | 临时 PDF、图片、导出物 | 不提交，除非任务明确要求并确认内容 |

不要删除或重建这些目录来“修测试”，除非用户明确授权。测试使用临时目录、mock 或任务专用 SQLite 文件。

### 9.3 迁移规则

- 新的正式 schema 变化创建新的 Alembic revision，不修改已发布的 `001`、`002`、`003`。
- 迁移同时考虑 MySQL 和 SQLite；现有 `003` 使用 MySQL 特定 SQL，是已知兼容风险，不要复制这种写法到新迁移。
- 升级和降级都应可解释；破坏性数据迁移先备份或设计分阶段迁移。
- ORM、Pydantic model、查询、迁移和文档要同步。
- `scripts/db_manager.py reset`/`make db-reset` 会重置数据库，未经用户明确要求不要执行。

## 10. 配置体系

### 10.1 加载入口

- `backend/app.py` 在导入路由前尝试加载根目录 `config.env`。
- 根 `config.py` 是当前 LLM、主数据库参数、Chroma、Host/Port 和 Hermes 的主要兼容配置。
- `backend/database.py` 直接从环境变量解析实际数据库连接。
- `backend/core/config.py` 是另一套 dataclass 风格配置，核心测试和部分旧代码使用它；它优先读取 `.env`，也读取 `config.env`。

### 10.2 变量命名分裂

| 领域 | 当前主路径常见变量 | `backend/core/config.py` 旧变量 |
| --- | --- | --- |
| MySQL | `MYSQL_HOST/PORT/USER/PASSWORD/DATABASE` | `DB_HOST/PORT/USERNAME/PASSWORD/DATABASE` |
| 服务 | `HOST`, `PORT` | `API_HOST`, `API_PORT` |
| LLM | `LLM_API_KEY`, `LLM_BASE_URL`, `DEFAULT_MODEL` | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` |

添加配置时：

1. 先确认消费方用哪套配置。
2. 选择一个主变量名。
3. 必要时读取旧变量作为 fallback，不要反向覆盖显式新变量。
4. 更新 `config.env.example`，只写占位值和安全默认值。
5. 添加配置解析测试，覆盖缺省、显式值和非法值。

LLM key 的当前兼容优先级为：

```text
LLM_API_KEY
-> DEEPSEEK_API_KEY
-> DASHSCOPE_API_KEY
-> OPENAI_API_KEY
```

模型和网关切换应通过配置完成，不要在业务代码中硬编码供应商 URL、模型名或 key。

## 11. 安全敏感区域

### 11.1 URL 抓取

`/chat/parse-url` 当前会由服务端请求用户提供的 URL。修改或增强时必须防 SSRF：

- 仅允许 `http`/`https`。
- 拒绝 loopback、link-local、私网、保留地址和非预期端口。
- DNS 解析后仍要校验目标地址，并考虑重定向后的地址。
- 设置连接/读取超时、响应体积、重定向次数和内容类型限制。
- 不把抓取异常、内部地址或响应体原样返回给用户。

### 11.2 文件上传

- 当前附件白名单包含图片、PDF、文本和 Office 扩展名，单文件限制为 10 MB。
- 不信任文件名、扩展名和客户端 MIME；保存名必须重新生成并限制在 `uploads/`。
- 防路径穿越、压缩炸弹、超大 PDF、恶意解析器输入和长期残留。
- 对外展示上传内容时避免脚本执行和内容嗅探。

### 11.3 Hermes 与工具

- `HERMES_TOOLS_ENABLED`、网页访问和 shell 默认关闭。
- `HERMES_WORKSPACE_ROOT` 必须解析并限制在明确目录内。
- shell、文件写入、网页抓取不能因“智能化”而绕过白名单、超时和权限开关。
- 不把用户自然语言直接拼接成 shell 命令。

### 11.4 CORS 与健康检查

- 默认只允许本地前端来源；`CORS_ALLOW_ALL=1` 仅用于调试，此时 credentials 必须关闭。
- 新增来源通过 `FRONTEND_ORIGINS` 配置，不硬编码生产域名和通配符组合。
- 当前 `/health` 实际主要验证数据库并写入一条系统日志；返回中的 `vector_db: ready` 不是完整向量库探针。不要在运维判断中夸大其覆盖范围。
- 健康检查应快速、可重复且无显著副作用；若重构，优先移除写日志式数据库探测。

## 12. 编码、风格与实现约定

- 所有文本文件保持 UTF-8。PowerShell 查看中文时显式使用 `Get-Content -Encoding utf8`。
- 终端显示乱码不代表源文件损坏，不要进行全仓库编码转换。
- Python 新代码使用类型标注，保持 Black 100 列和 Ruff 规则。
- Pydantic 使用 v1 API，例如 `validator`；不要引入只适用于 v2 的 `field_validator`、`model_dump`。
- SQLAlchemy 使用 1.4 兼容 API，不引入必须依赖 2.x 的声明或 session 行为。
- router 负责协议层，service 负责业务流程，数据库和外部集成通过清晰边界调用。
- 新 service 优先支持依赖注入，避免继续增加 import-time 全局单例。
- 异步路由中不要直接执行长时间 CPU/阻塞 I/O；必要时使用线程池、任务队列或已有异步客户端。
- 异常对外返回稳定、脱敏的信息，对内记录上下文；不要把第三方原始异常和密钥返回给前端。
- 保留已有公共字段和路由；破坏性变更应提供兼容层或明确迁移方案。
- 不修改 `frontend/src/App.js.backup` 代替正式 `App.js`。

## 13. 典型改动路径

### 13.1 新增后端 API

1. 选择现有 router 或创建 `backend/routers/<feature>.py`。
2. 在实际使用的 model 文件定义请求/响应，不要重复造第三套同名 schema。
3. 将业务逻辑放入 service/module。
4. 在 `backend/app.py` 或 `backend/routers/__init__.py` 显式注册。
5. 添加成功、校验失败、依赖失败和权限/归属测试。
6. 若前端使用，同步 `ChatAPI.js` 和对应 hook。
7. 更新 API 文档。

### 13.2 修改聊天或 Prompt

1. 跟踪 `/chat/stream` 和 `/chat/` 是否都受影响。
2. 检查输入预处理、危机意图、上下文、RAG 和普通引擎两条分支。
3. 确认消息不会漏存、重复存或跨用户召回。
4. 测试无 LLM key、LLM 超时、RAG 空库和新会话。
5. Prompt 不得绕过安全策略；更新 `backend/xinyu_prompt.py` 或实际消费的 composer，而不是仅改文档示例。

### 13.3 修改记忆

1. 保留 `user_id + session_id` 作用域。
2. 向量 metadata 必须保存 owner。
3. 删除和重要度更新前读取 metadata 并校验 owner。
4. 测试 Alice 不能读取/修改/删除 Bob 的记忆。
5. 同时检查关系库、Chroma 和内存缓存/Memory Hub 的一致性。

### 13.4 修改数据库

1. 修改 ORM。
2. 新增 Alembic revision。
3. 更新 service/query 和 Pydantic 响应。
4. 用隔离数据库测试 upgrade；有 downgrade 时也测试。
5. 同时验证 SQLite 和 MySQL 差异。

### 13.5 修改前端聊天

1. `App.js` 负责页面组合，状态逻辑优先放 hook。
2. 网络调用集中在 `ChatAPI.js`，避免组件继续散落 Axios；维护旧组件时可逐步收敛。
3. 流式状态必须覆盖发送中、取消、错误、空响应和完成。
4. 历史消息 ID、排序和去重规则不能破坏。
5. 变更样式时检查桌面和窄屏、长文本、Markdown、附件和深色主题。

### 13.6 接入新的模型供应商

1. 优先复用 `backend/modules/llm/harness.py` 的 OpenAI-compatible 设置。
2. 只新增必要配置 fallback，不在业务层判断供应商。
3. 验证普通聊天、流式行为、超时、错误映射和评估模型。
4. 更新 `config.env.example`，不要提交真实 key。

## 14. 本地安装与运行

在仓库根目录执行。Windows 推荐使用项目已有 `.venv`：

```powershell
# 首次准备本地配置；不要覆盖已有 config.env
Copy-Item config.env.example config.env

# 安装后端
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 安装前端
Set-Location frontend
npm install
Set-Location ..
```

启动前后端：

```powershell
.venv\Scripts\python.exe main.py
```

仅启动后端，并初始化本地知识库：

```powershell
.venv\Scripts\python.exe run_backend.py
```

仅快速启动当前 FastAPI app，不主动运行 `run_backend.py` 的知识库初始化：

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

仅启动前端：

```powershell
Set-Location frontend
npm start
```

默认地址：

- API：`http://localhost:8000`
- OpenAPI：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/health`
- 前端：`http://localhost:3000`

macOS/Linux 可使用 `Makefile`，但它依赖 GNU Make 和类 Unix shell。不要假设 Makefile 命令可原样在 PowerShell 工作。

## 15. 测试与验证

### 15.1 后端

优先运行最小相关测试，再扩大范围：

```powershell
# 单文件/单用例
.venv\Scripts\python.exe -m pytest backend/tests/unit/test_memory_safety.py -q
.venv\Scripts\python.exe -m pytest path/to/test_file.py::test_name -q

# 单元测试
.venv\Scripts\python.exe -m pytest backend/tests/unit -q

# 集成测试
.venv\Scripts\python.exe -m pytest backend/tests/integration -q

# 全部现有后端测试
.venv\Scripts\python.exe -m pytest backend/tests -q
```

当前测试重点只有 core utilities 和部分记忆隔离，不能把“现有测试通过”理解为聊天、RAG、SSE 和前端契约全部正确。修改未覆盖区域时主动补测试。

普通语法检查可先运行：

```powershell
.venv\Scripts\python.exe -m py_compile backend/app.py
```

不要把 `from backend.app import app` 当作无副作用的普通 smoke test。当前导入会初始化多个 ChatService、Chroma collection、插件和 RAG；当知识库状态不满足条件时，还可能使用本地 `config.env` 中的模型设置发起 embedding 请求。只有在以下条件都满足时才做应用导入或 TestClient 测试：

- 使用专门的测试进程和测试配置；
- `DATABASE_URL=sqlite:///:memory:` 或每次唯一的临时 SQLite；
- mock LLM/embedding、天气、新闻和其他外网客户端；
- Chroma 指向 pytest `tmp_path`，不能指向项目现有 `chroma_db/`；
- 禁用 telemetry 和自动知识库初始化；
- Windows 设置 `PYTHONUTF8=1`。

若当前代码无法注入这些依赖，先为初始化增加可测试边界，再做装配测试；不要用真实开发配置硬跑。

### 15.2 静态检查

```powershell
.venv\Scripts\python.exe -m ruff check backend
.venv\Scripts\python.exe -m black --check backend
.venv\Scripts\python.exe -m mypy backend --ignore-missing-imports
```

老项目可能已有与当前任务无关的存量告警。不要顺手格式化整个仓库；对修改文件运行检查，并区分“新增问题”和“历史基线问题”。

当前已知测试/运行基线包括：

- SQLAlchemy 会报告 2.0 弃用警告，依赖必须继续固定 `<2.0`，除非任务是完整升级。
- `jieba` 间接使用的 `pkg_resources` 会报告弃用警告。
- Windows 下 MySQL fallback 的 Unicode 控制台输出可能使应用导入失败，见上面的安全 smoke-test 环境变量。
- 应用 import 会创建/打开多个 Chroma collection，可能尝试自动加载示例知识并请求 embedding endpoint。
- 当前 Chroma telemetry 与已安装的 PostHog API 存在兼容错误日志；这不一定阻止启动，但不能当作健康状态正常的证据。
- 这些警告和失败应如实记录；不要用全局忽略、吞异常或放宽测试来制造“通过”。

### 15.3 前端

```powershell
Set-Location frontend
$env:CI = "true"
npm test -- --watchAll=false
npm run build
```

如果没有匹配的前端测试，`npm test` 可能因 “No tests found” 返回非零。此时至少运行生产构建，并为新增逻辑补测试。

### 15.4 API 与 SSE

路由改动按需验证：

- `/health` 状态码和响应；
- 新会话与已有会话；
- 空历史；
- 错误输入的 4xx，而不是 500；
- SSE token、done、error 和取消；
- 可选组件关闭或不可用时的降级；
- 用户 A 无法访问用户 B 的数据。

不要在自动测试中调用真实付费模型、天气 API 或用户数据库。

### 15.5 CI 不能作为唯一依据

`.github/workflows/ci.yml` 中现有单元测试命令使用 `|| echo`，集成测试还设置 `continue-on-error`；因此 CI 绿灯不代表测试真实通过。交付时报告命令的真实退出码。

## 16. Docker、Compose 与部署

- Dockerfile 当前以 Python 3.9 构建并执行 `python run_backend.py`。
- `docker-compose.yml` 包含 backend、MySQL、Redis、Nginx、Prometheus、Grafana、Elasticsearch 和 Kibana。
- Compose 不等于本地 React 开发服务器；生产前端构建和静态托管需要单独确认。
- 修改端口、健康检查、数据卷或环境变量时同步 Dockerfile、Compose、README 和生产部署文档。
- 不执行 `docker compose down -v`、删除 named volume 或重建生产数据，除非用户明确授权。
- 部署配置中的示例密码必须保持示例性质；发现真实凭据立即停止传播并报告。

## 17. 生成物与工作区保护

以下通常不属于源代码改动：

- `config.env`
- `.venv/`
- `frontend/node_modules/`
- `frontend/build/`
- `chroma_db/`
- `data/`
- `context_storage/`
- `uploads/`
- `log/`, `logs/`
- `tmp/`
- `__pycache__/`, `.pytest_cache/`

修改前运行 `git status --short`。已有未提交内容属于用户：

- 不删除、不覆盖、不格式化无关文件。
- 不使用 `git reset --hard`、`git checkout --` 或清理命令。
- 新生成的本地数据不要混入提交。
- 若任务与已有改动重叠，先检查 diff；无法安全合并时再询问用户。

## 18. 文档维护

以下变化必须同步文档：

- 启动命令、Python/Node 版本或依赖安装方式；
- 环境变量；
- API 路径、请求、响应、SSE 事件；
- 数据库迁移和部署步骤；
- 危机安全策略；
- RAG 知识库结构；
- Agent/Runtime/Skills 的实际接入关系。

优先更新：

- `README.md` / `README.en.md`
- `config.env.example`
- `docs/API接口文档.md`
- 对应专题文档
- `scripts/README.md`

不要让文档继续声称旧单体中存在、但当前 `backend.app` 未注册的接口可用。

## 19. 完成定义

交付前逐项确认：

- 已从 `backend/app.py` 证明修改位于真实运行链路。
- 只修改任务相关文件，保留用户原有工作区内容。
- 没有提交密钥、真实对话、数据库、向量库、附件、日志和生成物。
- 新旧实现的兼容影响已说明，没有无依据删除历史入口。
- API 改动已同步 model、service、前端调用和文档。
- 数据改动具备迁移，并考虑 MySQL/SQLite。
- 记忆和会话操作验证了用户归属。
- 危机、安全、SSRF、上传和工具权限没有退化。
- 已运行与改动成比例的测试/构建，并报告真实结果。
- 未执行的验证项及原因已明确写在交付说明中。
