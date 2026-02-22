# 🚀 Deployment Log Verification Automation

An automated deployment log verification system that monitors incoming deployment log archives (`.zip` and `.msg` files), validates Oracle deployment results, extracts JIRA mappings, archives audit trails, and sends email alerts — all through a premium dark-themed UI.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Core Modules](#-core-modules)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Folder Monitoring** | Polls an incoming folder for `.zip` and `.msg` files at configurable intervals |
| **MSG Email Extraction** | Automatically extracts ZIP attachments from Outlook `.msg` files |
| **Oracle Log Validation** | Detects ORA errors, compilation failures, and invalid objects from deployment logs |
| **Ignorable Error Filtering** | Configurable list of ORA errors to ignore (e.g., `ORA-00001`, `ORA-00955`) |
| **JIRA Unit Extraction** | Extracts JIRA ticket → compiled unit mappings from logs |
| **Automated Archiving** | Archives results into weekly deployment cycles with PASS/FAIL segregation |
| **Email Alerts** | Sends deployment summary emails via Outlook COM automation |
| **Dual UI** | Streamlit web UI + Tkinter desktop UI with real-time live log display |
| **Sound Alerts** | Audio notification on deployment PASS/FAIL |

---

## 🏗 Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                  UI Layer (choose one)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │  app.py     │  │  tk_app.py  │  │  service.py      │ │
│  │  (Streamlit)│  │  (Tkinter)  │  │  (CLI/headless)  │ │
│  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘ │
└─────────┼────────────────┼──────────────────┼────────────┘
          │                │                  │
          ▼                ▼                  ▼
┌──────────────────────────────────────────────────────────┐
│                     Core Pipeline                        │
│                                                          │
│  FolderMonitor → MsgProcessor → ZipProcessor             │
│                                     │                    │
│                            DeploymentValidator           │
│                                     │                    │
│                    JiraExtractor ← ──┤                   │
│                                     │                    │
│                      Archiver ← ────┤                    │
│                                     │                    │
│                    EmailSender ← ───┘                    │
└──────────────────────────────────────────────────────────┘
```

---

## 📌 Prerequisites

- **Python** 3.10+
- **Microsoft Outlook** (classic desktop version) — required for email alerts
- **Windows OS** — uses `win32com` for Outlook COM and `os.startfile` for folder opening

---

## 🔧 Installation

```bash
# 1. Clone the repository
git clone https://github.com/loges-git/PycharmProjects.git
cd PycharmProjects/deployment_monitor

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `watchdog` | File system monitoring (optional, for future real-time mode) |
| `extract-msg` | Parse Outlook `.msg` email files |
| `pywin32` | Outlook COM automation for sending emails |

---

## ⚙ Configuration

Edit `config.json` in the project root:

```json
{
  "base_audit_path": "C:\\deployment_audit_test",
  "poll_interval_seconds": 30,
  "clusters": {
    "mena": ["FSMHO1U"],
    "cee": ["FMSLO1P", "FMROM1P"],
    "ssa": ["FCCNIG", "FCCKEN"]
  },
  "ignorable_errors": ["ORA-00001", "ORA-00955"],
  "email_settings": {
    "enabled": true,
    "recipients": ["your-email@example.com"],
    "subject_templates": {
      "PASS": "[PASS] {cluster} - {instance} Deployment Validation",
      "FAIL": "[FAIL] {cluster} - {instance} Deployment Validation"
    },
    "body_template": "Cluster: {cluster}\nInstance: {instance}\nStatus: {status}\n\nDetails:\n{message}"
  }
}
```

### Key Configuration Fields

| Field | Description |
|-------|-------------|
| `base_audit_path` | Root folder where deployment cycles are archived |
| `poll_interval_seconds` | How often to scan the incoming folder (seconds) |
| `clusters` | Maps cluster names → list of Oracle instance names |
| `ignorable_errors` | ORA error codes that should NOT trigger a FAIL |
| `email_settings.enabled` | Set to `true` to enable Outlook email alerts |
| `email_settings.recipients` | List of email addresses for notifications |

---

## 🚀 Usage

### Option 1: Streamlit Web UI (Recommended)

```bash
streamlit run app.py
```

Opens a browser at `http://localhost:8501` with:
- Configuration inputs (incoming path, base audit path, poll interval)
- Start/Stop service controls
- Real-time live log display
- Deployment status with sound alerts

### Option 2: Tkinter Desktop UI

```bash
python tk_app.py
```

A native desktop window with the same features as the Streamlit version.

### Option 3: CLI / Headless Service

```bash
python service.py
```

Runs as a headless service in the terminal with console output.

---

## 📁 Project Structure

```
deployment_monitor/
├── app.py                  # Streamlit web UI entry point
├── tk_app.py               # Tkinter desktop UI entry point
├── service.py              # CLI/headless service entry point
├── main.py                 # Standalone batch processor (test_zips/)
├── shared_state.py         # Thread-safe shared state for Streamlit
├── styles.py               # Luxury dark theme CSS for Streamlit
├── config.json             # Application configuration
├── requirements.txt        # Python dependencies
│
├── core/                   # Core processing modules
│   ├── folder_monitor.py   # Polling-based folder watcher
│   ├── msg_processor.py    # Extract ZIPs from Outlook .msg files
│   ├── zip_processor.py    # Extract and parse deployment ZIPs
│   ├── validator.py        # Oracle deployment log validation
│   ├── jira_extractor.py   # JIRA ticket → unit mapping extractor
│   ├── archiver.py         # Weekly cycle archiver (PASS/FAIL)
│   ├── cycle_manager.py    # Deployment cycle naming (weekly)
│   ├── email_sender.py     # Outlook COM email sender
│   ├── notifier.py         # Windows toast notifications
│   ├── config_validator.py # Configuration schema validator
│   └── logger_config.py    # Logging configuration
│
└── tests/                  # Unit tests
```

---

## 🔧 Core Modules

### `FolderMonitor` — File Detection
Polls the incoming folder at configurable intervals. Uses file size + modification time fingerprinting for deduplication. Supports `.zip` and `.msg` files.

### `MsgProcessor` — Email Extraction
Parses Outlook `.msg` files using `extract-msg` library and extracts ZIP attachments for processing.

### `ZipProcessor` — Archive Extraction
Extracts deployment ZIP archives to a temp directory with **path traversal protection**. Locates required log files:
- `*_oracle.log_completed.log` — main deployment log
- `*_invalids_completed.log` — invalid objects log
- `oracle_error` file (optional)

Auto-detects the Oracle instance and cluster from the filename and config.

### `DeploymentValidator` — Log Validation
Runs three validation checks:
1. **Error Validation** — scans for ORA errors, filters out ignorable ones
2. **Invalid Objects Delta** — detects invalid objects created during deployment
3. **Execution Integrity** — verifies all units were compiled without unexpected failures

Returns `PASS` or `FAIL` with detailed error reports.

### `JiraExtractor` — JIRA Mapping
Parses deployment logs to extract JIRA ticket → compiled unit mappings for audit trail documentation.

### `Archiver` — Result Archiving
Organizes results into a weekly cycle folder structure:
```
base_audit_path/
└── Feb_week04_2026/
    ├── Processed/          # PASS results
    │   └── mena/FSMHO1U/
    │       ├── deployment.zip
    │       └── compiled_units.txt
    └── Failed/             # FAIL results
        └── ssa/FCCNIG/
```

### `CycleManager` — Weekly Cycle Naming
Generates deployment cycle names anchored to Fridays (e.g., `Feb_week04_2026`). Reuses the same folder for deployments within the same week.

### `EmailSender` — Outlook Email Alerts
Sends deployment summary emails via Outlook COM with configurable templates and retry logic with exponential backoff.

---

## ⚡ How It Works

1. **Start Service** — Click the Start button in the UI (or run `service.py`)
2. **Monitor** — `FolderMonitor` polls the incoming folder every N seconds
3. **Detect** — When a `.zip` or `.msg` file appears:
   - `.msg` → `MsgProcessor` extracts ZIP attachments
   - `.zip` → Sent directly to processing
4. **Extract** — `ZipProcessor` extracts the archive and locates log files
5. **Validate** — `DeploymentValidator` checks for errors, invalid objects, and compilation integrity
6. **Extract JIRA** — `JiraExtractor` maps JIRA tickets to compiled units
7. **Archive** — `Archiver` copies ZIP and generates `compiled_units.txt` into the weekly cycle folder
8. **Notify** — Email alert sent (if enabled) and status displayed in UI with sound alert

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Logs not showing in Streamlit** | Ensure `shared_state.py` exists alongside `app.py`. This module holds the shared state that persists across Streamlit reruns. |
| **Email error: "Invalid class string"** | Microsoft Outlook desktop (classic) is not installed. The email feature requires the Win32 Outlook COM class. |
| **Email error: "disabled in config"** | Set `"enabled": true` in `config.json` → `email_settings` |
| **No files detected** | Verify the incoming folder path contains `.zip` or `.msg` files. Check the poll interval setting. |
| **Instance not found in cluster** | Add the Oracle instance name to the appropriate cluster in `config.json` → `clusters` |
| **ZIP extraction error** | Ensure the ZIP contains valid Oracle deployment logs with the expected naming convention |

---

## 📄 License

Internal tool — not licensed for public distribution.
