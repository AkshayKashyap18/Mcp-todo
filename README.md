# MCP Todo List Manager

A powerful, AI-driven Todo List Management system using the Model Context Protocol (MCP). This project combines a Python-based MCP server with deterministic and AI-powered task management capabilities, paired with a modern React frontend.

## 🚀 Features

- **MCP Integration**: Fully compatible with MCP clients (like Claude Desktop).
- **AI-Powered (Groq)**: Smart task parsing and fuzzy search using Large Language Models.
- **Supabase Backend**: Persistent storage using Supabase.
- **Deterministic Tools**: Precise control for adding, updating, listing, and deleting tasks.
- **Modern Dashboard**: A beautiful React + Vite frontend with Tailwind CSS and Framer Motion.

## 🛠️ Tech Stack

- **Backend**: Python 3.13+, `mcp`, `langchain`, `supabase`, `uv`.
- **AI**: Groq (Llama 3).
- **Frontend**: React 19, Vite, Tailwind CSS, Lucide icons.
- **Database**: Supabase (PostgreSQL).

## 📋 Prerequisites

- Python 3.13 or higher.
- Node.js 18 or higher (for frontend).
- `uv` (recommended for Python project management).
- A Groq API Key.
- A Supabase project and API keys.

## ⚙️ Setup

### 1. Project Configuration
Clone the repository and create a `.env` file in the root directory:

```env
GROQ_API_KEY="your_groq_api_key"
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"
```

### 2. Backend Setup (MCP Server)
Using `uv` (recommended):
```bash
uv sync
```
Or using `pip`:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## 🏃 Running the Project

### Start the MCP Server
To run the server locally on stdio:
```bash
uv run src/mcp_server/server.py
```

### Start the Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## 🛠️ MCP Tools

| Tool | Description | Input Type |
|------|-------------|------------|
| `add_task` | Create a new task (deterministic) | Title, Description, Due Date, Priority |
| `list_tasks` | List tasks with filters | Status, Priority, Limit |
| `update_task` | Update an existing task | Task ID + Updates |
| `delete_task` | Remove a task | Task ID |
| `smart_add` | AI-powered task creation | Natural language (e.g., "Buy milk tomorrow") |
| `search_tasks`| AI-powered fuzzy search | Natural language query |
| `smart_update`| AI-powered task update | Natural language command |

## 🧪 Testing

Run backend tests using `pytest`:
```bash
uv run pytest
```

---
Built with ❤️ using MCP and AI.
