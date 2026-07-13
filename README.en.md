# Xinyu · Emotional Support Chatbot

[简体中文](README.md) | [English](README.en.md)

An open-source AI conversation application for emotional-support scenarios. It combines a FastAPI backend and a React frontend with emotion and intent recognition, long-term memory, RAG, agent skills, streaming responses, and automated evaluation. It works with OpenAI-compatible model providers, including Zhipu GLM, Alibaba Cloud Qwen, and OpenAI.

> [!IMPORTANT]
> This project is intended for technical research and emotional support. It does not provide medical diagnoses or professional therapy. If someone is in immediate danger or at risk of self-harm, contact local emergency services, a crisis hotline, or a trusted person immediately.

![Home screen](image/首页界面.png)

## Highlights

- Emotion and intent understanding, including safety policies for crisis-related language.
- Contextual conversations based on the current turn, conversation history, semantic memory, and user profiles.
- A ChromaDB-powered RAG knowledge base for mental-health resources, self-help exercises, and organizational policies.
- Task planning, tool use, reflection, plugins, and a Runtime + Skills agent architecture.
- File and image attachments, audio processing, and streaming chat.
- User feedback, automated evaluation, A/B tests, performance metrics, and emotion trends.
- A React 18 interface with Markdown, themes, typewriter effects, and avatar customization.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | React 18, Axios, styled-components, react-markdown |
| API | Python 3.10+, FastAPI, Uvicorn, Pydantic v1 |
| AI | OpenAI-compatible APIs, LangChain, Runtime + Skills |
| Data | MySQL / SQLite, ChromaDB, optional Redis |
| Operations | Docker Compose, Nginx, Prometheus, Grafana |

## Quick start

### 1. Prerequisites

- Python 3.10 or 3.11 for the best compatibility
- Node.js 18+ and npm
- An API key for an OpenAI-compatible model provider
- MySQL 8 (optional; SQLite can be used locally)

```bash
git clone https://github.com/congde/emotional_chat.git
cd emotional_chat
```

### 2. Configure the backend

Copy the example configuration:

```bash
# macOS / Linux
cp config.env.example config.env

# Windows PowerShell
Copy-Item config.env.example config.env
```

Set at least these values:

```dotenv
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
DEFAULT_MODEL=glm-5.1
```

For example, to use Qwen through DashScope:

```dotenv
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DEFAULT_MODEL=qwen-plus
```

To use SQLite instead of a local MySQL server:

```dotenv
USE_SQLITE=1
SQLITE_PATH=./emotional_chat_local.db
```

See [`config.env.example`](config.env.example) for every option. Never commit a `config.env` file containing real credentials.

### 3. Start the backend

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python run_backend.py
```

The launcher checks dependencies, initializes the local knowledge base, and serves the API at `http://localhost:8000`.

- OpenAPI UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

### 4. Start the frontend

In another terminal:

```bash
cd frontend
npm install
npm start
```

Open <http://localhost:3000>. If the backend is not available on local port `8000`, create `frontend/.env.local`:

```dotenv
REACT_APP_API_URL=http://your-backend-host:8000
```

## Common commands

On systems with GNU Make installed:

```bash
make help          # List available commands
make install       # Install Python dependencies
make run           # Start the backend and initialize the knowledge base
make rag-init      # Initialize the RAG knowledge base
make db-upgrade    # Apply database migrations
make db-check      # Check the database connection
```

Run the test suites with:

```bash
pytest
cd frontend && npm test
```

## Docker deployment

The repository includes a Compose stack for the backend, MySQL, Redis, Nginx, and observability services:

```bash
cp config.env.example config.env
docker compose up -d --build
docker compose ps
```

The Compose file does not build the React development server. For production, run `npm run build` and serve the generated static files through Nginx or another static host. Replace all example passwords, restrict CORS, configure HTTPS, and enable observability services according to the host's capacity. See the [production deployment guide](docs/生产部署指南.md) for details (currently in Chinese).

## Architecture

```text
React Web
   │ HTTP / SSE
   ▼
FastAPI routers
   ▼
Chat / Emotion / Intent / Memory / Agent services
   ├── OpenAI-compatible LLM
   ├── ChromaDB knowledge & semantic memory
   ├── MySQL or SQLite persistence
   └── Redis cache (optional)
```

Key directories:

```text
backend/          FastAPI app, routers, services, and core modules
  agent/          Agent core and tool calling
  runtime/        Runtime + Skills conversation runtime
  modules/        Intent, RAG, LLM, and multimodal modules
  routers/        HTTP and SSE APIs
  services/       Chat, memory, context, and personalization services
frontend/         React web client
knowledge_base/   Built-in knowledge resources
docs/             Architecture, deployment, and feature documentation
test_*.py         Backend test and evaluation scripts
```

## Further reading

- [API reference](docs/API接口文档.md)
- [Agent architecture](docs/Agent技术架构完整指南.md)
- [Memory architecture](docs/记忆系统架构.md)
- [RAG implementation](docs/RAG实施步骤.md)
- [Windows setup](docs/Windows运行指南.md)
- [macOS setup](docs/MACBOOK_SETUP.md)
- [Release history](docs/版本迭代记录.md)

Most detailed documentation is currently written in Chinese.

## Contributing

Issues and pull requests are welcome. Keep changes focused, run the relevant tests, and update affected documentation. Python code follows the repository's Black and Ruff configuration.

## Contact

Questions and suggestions are welcome through any of the following channels:

- Submit a [GitHub Issue](https://github.com/congde/emotional_chat/issues)
- Email the maintainer at [congdeyuan@gmail.com](mailto:congdeyuan@gmail.com)
- WeChat: `jx-yuancongde`

## License

Licensed under the [MIT License](LICENSE).
