# 🔍 AI Log Analyzer Agent

A **production-ready AI logging agent** that acts like a senior DevOps engineer on call. It reads your application logs, correlates evidence across systems, diagnoses root causes, and takes automated actions — with human-in-the-loop approval for any infrastructure changes.

Built with **LangChain**, **Google Gemini**, and **Streamlit**, it supports multi-model LLMs, persistent memory across sessions, and a clean web UI.

---

## ✨ Features

- 🤖 **AI-Powered Log Analysis** — Uses a ReAct agent loop to reason over logs and take action through tools
- 🧠 **Persistent Memory** — Chat history and incident records are saved to disk across sessions
- 🔒 **Human-in-the-Loop Approvals** — Destructive actions (pod restarts, RDS reboots) are blocked until the user explicitly confirms
- 📣 **Slack Notifications** — Simulated (or real) incident alerts to Slack channels
- 🌐 **Multi-Model Support** — Easily switch between Gemini, OpenAI, and other LangChain-compatible providers
- 🖥️ **Streamlit Web UI** — Clean chat interface with sidebar memory management

---

## 🏗️ Architecture

The system monitors a three-tier AWS application:
- **Backend:** Java Spring Boot on EKS
- **Database:** RDS MySQL
- **Cache:** Redis ElastiCache
- **Frontend:** CloudFront + S3

```text
app.py (Streamlit UI)
│
├── src/agents/log_analyzer.py    ← ReAct orchestration loop
├── src/tools/
│   ├── log_reader.py             ← Read & list log files
│   ├── actions.py                ← Kubernetes pod restart
│   ├── aws_actions.py            ← RDS reboot
│   └── slack_notifier.py        ← Slack alerts
├── src/memory/
│   ├── chat_store.py             ← Persistent chat history
│   └── incident_store.py        ← Incident log with resolution tracking
├── src/models/
│   ├── gemini.py                 ← Google Gemini model wrapper
│   └── factory.py               ← Model provider factory
└── src/config.py                 ← Centralized configuration
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ingchrist/AI-Log-Analyzer.git
cd AI-Log-Analyzer
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.1
LOG_DIRECTORY=logs
MEMORY_DIR=.memory
```

### 5. Run the App

```bash
streamlit run app.py
```

---

## 🛠️ Tool Reference

| Tool | Type | Description |
|------|------|-------------|
| `list_log_files` | ✅ Auto | Lists all `.log` files in the logs directory |
| `read_log_file` | ✅ Auto | Reads the contents of a specific log file |
| `send_slack_notification` | ✅ Auto | Sends an incident alert to a Slack channel |
| `restart_kubernetes_pod` | 🔒 Approval Required | Restarts a pod in a given namespace |
| `reboot_rds_instance` | 🔒 Approval Required | Reboots an AWS RDS database instance |

To approve a blocked action, simply reply with **`yes`**, **`y`**, or **`confirm`** in the chat.

---

## 💬 Example Queries

```text
"List available log files"
"Analyze app.log and tell me what's wrong"
"What caused the database connection exhaustion?"
"Send a P1 alert to #on-call about the RDS connection issue"
"Restart the backend pod — yes"
```

---

## 📁 Project Structure

```text
AI-Log-Analyzer/
├── app.py                  # Main Streamlit application
├── system_prompt.txt       # Agent persona and instructions
├── examples.txt            # Incident resolution guidelines
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── logs/                   # Log files for the agent to analyze
│   ├── app.log
│   └── redis.log
└── src/
    ├── config.py
    ├── agents/
    ├── memory/
    ├── models/
    ├── tools/
    └── utils/
```

---

## 🔌 Adding a New LLM Provider

1. Create a new file in `src/models/` (e.g., `openai.py`) following the `GeminiModel` pattern
2. Register it in `src/models/factory.py`
3. Set `LLM_PROVIDER=openai` in your `.env`

---

## 📝 License

MIT License — feel free to use, modify, and distribute.

---

## 🙌 Acknowledgements

Built with [LangChain](https://www.langchain.com/), [Google Gemini](https://deepmind.google/technologies/gemini/), and [Streamlit](https://streamlit.io/).
