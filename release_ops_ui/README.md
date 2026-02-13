# 🏦 Release Operations Platform

A modern release automation tool with **ChatBot** and **Manual UI** modes for executing software releases.

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Features](#-features)
3. [ChatBot Mode](#-chatbot-mode)
4. [Manual UI Mode](#-manual-ui-mode)
5. [AI Configuration](#-ai-configuration)
6. [Release Workflow](#-release-workflow)
7. [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git installed and configured

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd release_ops_ui

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### First Launch
1. Open http://localhost:8501 in your browser
2. Choose your mode: **ChatBot** or **Manual UI**
3. Follow the on-screen instructions

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 ChatBot Mode | Natural language release commands |
| 🖱️ Manual UI Mode | Traditional form-based workflow |
| ✅ Manager Approval | Review & approve releases via shareable links |
| 🛡️ Drift Detection | Validates files haven't changed since approval |
| 📂 Smart File Routing | Auto-routes files to correct folders |

---

## 🤖 ChatBot Mode

Use natural language to execute releases without clicking through forms.

### Step 1: Choose ChatBot Mode
When you launch the app, click **"🚀 Start with ChatBot"**.

### Step 2: Describe Your Release
Type commands like:
```
Release BANKING-123 to CIT on SSA
```

The AI will extract:
- **Jira**: BANKING-123
- **Environment**: CIT
- **Cluster**: SSA

### Step 3: Provide Missing Information
If something is missing, the AI will ask:
```
I still need: environment (CIT/BFX)
```

Simply respond with the missing info:
```
CIT environment
```

### Step 4: Confirm Execution
When everything is configured, say:
```
confirm
```
or
```
do it now
```

### Example Conversation
```
You: Release CORE-456 to BFX on LDN
AI:  ✅ Got it! Release Jira: CORE-456, Environment: BFX, Cluster: LDN
     🎯 Ready! Say 'confirm' to execute.

You: confirm
AI:  🚀 Starting Release Execution...
     ✅ SUCCESS: Release to LDN BFX completed!
```

---

## 🖱️ Manual UI Mode

Step-by-step guided workflow with traditional forms.

### Step 1: Choose Manual UI Mode
Click **"📋 Start with Manual UI"** on the launch screen.

### Step 2: Select Intent
Choose between:
- **Release Operations**: Execute releases
- **Repo Manager**: Clone/refresh repositories

### Step 3: Configure Environment (Setup Tab)
1. Select **Environment**: CIT (UAT) or BFX (Pre-Prod)
2. Select **Cluster**: SSA, LDN, WEU, etc.
3. Select **Release Type**: FULL, FIX, or ROLLBACK
4. Enter **Jira Ticket**: e.g., BANKING-123

### Step 4: Get Approval (Approval Tab)
1. Enter the **Shared Review Path** (retro folder)
2. Enter the **Search Tag** (e.g., folder name or date)
3. Click **Load Files for Review**
4. Send the approval link to your manager
5. Once approved, click **Load Approval**

### Step 5: Execute Release (Execution Tab)
1. Review the release summary
2. Check the confirmation box
3. Click **🚀 Execute Release**

---

## 🔧 AI Configuration

All AI settings are in **one file**: `config/ai_config.yaml`

### Using Mock Mode (No API Required)
```yaml
mode: MOCK
```
The built-in mock AI uses pattern matching for basic commands.

### Using Your Company's AI API
```yaml
mode: CUSTOM

api:
  url: "https://your-company-ai.example.com/v1/chat/completions"
  api_key: "your-api-key-here"
  model: "gpt-4"
  timeout: 30
  max_tokens: 1024
```

### Using Environment Variable for API Key
Leave `api_key` empty and set:
```bash
export AI_API_KEY="your-key"
```

### Customizing API Request Format
Edit `services/ai_provider.py` → `CustomAI.query()` method:
```python
# Modify payload format
payload = {
    "model": self.model,
    "messages": messages,
    "max_tokens": self.max_tokens
}

# Modify response parsing
data = response.json()
return data["choices"][0]["message"]["content"]
```

---

## 📂 Release Workflow

### How a Release Works

```
1. Configure  →  2. Approve  →  3. Execute
   ↓                 ↓              ↓
   Jira, Env,     Manager       Git commit,
   Cluster        signs off     push branch
```

### What Happens During Execution

1. **Drift Check**: Validates files haven't changed since approval
2. **Checkout Branch**: Creates release branch from base
3. **Apply Files**: Copies approved files with smart routing
4. **Commit & Push**: Commits with Jira ID as message

### File Routing Configuration

Edit `config/file_routing.yaml`:
```yaml
mappings:
  .prc: prc
  .sql: sql
  .vw: vw
  .trg: trgall
```

Files with these extensions are automatically placed in the correct folders.

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| AI not responding | Check `config/ai_config.yaml` settings |
| API quota exceeded | Wait or switch to Manual UI mode |
| Files not found | Verify the shared path exists |
| Drift detected | Files changed since approval - re-approve |
| Nothing to commit | Files already match - release skipped |

### Debug Mode

Click **"🐛 Debug Mode"** toggle in the app to see detailed error messages.

### Logs

Check the terminal running `streamlit run app.py` for backend logs.

---

## 📁 Project Structure

```
release_ops_ui/
├── app.py                    # Main application
├── config/
│   ├── ai_config.yaml        # AI settings
│   ├── clusters.yaml         # Cluster definitions
│   └── file_routing.yaml     # Extension → folder mappings
├── services/
│   ├── ai_provider.py        # AI integration
│   ├── agent_service.py      # Prompt processing
│   ├── release_service.py    # Release execution
│   └── git_service.py        # Git operations
├── ui/
│   ├── chat_interface.py     # ChatBot UI
│   ├── release_flow.py       # Release execution UI
│   └── review_approval.py    # Approval workflow
└── models/
    └── release_context.py    # State management
```

---

## 📝 License

Internal use only.
