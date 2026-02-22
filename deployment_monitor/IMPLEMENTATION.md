# Implementation Guide — Deployment Log Verification Automation

This document provides a detailed technical breakdown of each module, data flow, and design decisions. It is intended for developers who need to understand, maintain, or extend the system.

---

## Table of Contents

- [System Overview](#system-overview)
- [Data Flow Pipeline](#data-flow-pipeline)
- [Module Deep Dive](#module-deep-dive)
  - [Entry Points](#1-entry-points)
  - [Shared State](#2-shared-state-shared_statepy)
  - [Folder Monitor](#3-folder-monitor)
  - [MSG Processor](#4-msg-processor)
  - [ZIP Processor](#5-zip-processor)
  - [Deployment Validator](#6-deployment-validator)
  - [JIRA Extractor](#7-jira-extractor)
  - [Archiver](#8-archiver)
  - [Cycle Manager](#9-cycle-manager)
  - [Email Sender](#10-email-sender)
  - [Styles](#11-styles)
- [Threading Model](#threading-model)
- [Configuration Schema](#configuration-schema)
- [Deployment Cycle Structure](#deployment-cycle-structure)
- [Extending the System](#extending-the-system)

---

## System Overview

The application automates the verification of Oracle database deployments. Deployment teams run scripts that produce log files packaged as ZIP archives. These logs are either dropped manually into a monitored folder or received as email attachments (`.msg` files). The system automatically:

1. Detects new files in the incoming folder
2. Extracts and parses Oracle deployment logs
3. Validates for errors, invalid objects, and compilation integrity
4. Archives results into a structured weekly cycle hierarchy
5. Sends email notifications with deployment status

---

## Data Flow Pipeline

```
              ┌─────────────────┐
              │  Incoming Folder │
              │  (.zip / .msg)   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  FolderMonitor   │  Polls every N seconds
              │  (Deduplication) │  Fingerprint: size + mtime
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │                 │
        .msg file          .zip file
              │                 │
              ▼                 │
      ┌───────────────┐        │
      │ MsgProcessor  │        │
      │ (extract-msg) │        │
      └───────┬───────┘        │
              │                │
              ▼                ▼
         ZIP file(s) ──────────┤
                               │
                               ▼
                    ┌─────────────────┐
                    │  ZipProcessor    │  Extract to temp dir
                    │  Path traversal  │  Find log files
                    │  protection      │  Detect instance/cluster
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐     Returns:
                    │ DeploymentValid. │  ─► status: PASS/FAIL
                    │                 │     message: details
                    │ 3 validations:  │     error_details: [...]
                    │ • ORA errors    │     invalid_objects: [...]
                    │ • Invalid objs  │
                    │ • Exec integrity│
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
          ┌───────────────┐  ┌───────────────┐
          │ JiraExtractor │  │   Archiver     │
          │               │  │ PASS → Processed│
          │ JIRA → units  │  │ FAIL → Failed  │
          │ mapping       │  │ compiled_units │
          └───────────────┘  └───────────────┘
                                     │
                                     ▼
                            ┌───────────────┐
                            │  EmailSender   │
                            │  Outlook COM   │
                            │  with retry    │
                            └───────────────┘
```

---

## Module Deep Dive

### 1. Entry Points

The system provides three ways to run:

#### `app.py` — Streamlit Web UI
- Runs on `http://localhost:8501`
- Background thread handles file processing
- `shared_state.py` module provides thread-safe communication
- Auto-refreshes every 0.3–2 seconds to display live logs
- Uses `styles.py` for a luxury dark glassmorphic theme

#### `tk_app.py` — Tkinter Desktop UI
- Native Windows application
- Uses `after()` for UI updates from background thread
- Same processing pipeline as Streamlit version

#### `service.py` — CLI Headless Service
- Console-based output
- Reads configuration from `config.json`
- Suitable for running as a background service or scheduled task

#### `main.py` — Batch Processor
- Processes ZIP files from a `test_zips/` folder
- Useful for testing and one-off validation runs

---

### 2. Shared State (`shared_state.py`)

**Purpose**: Solves Streamlit's re-execution problem for background thread communication.

**Why it exists**: Streamlit re-executes `app.py` via `exec()` on every user interaction and `st.rerun()` call. This recreates all module-level variables, breaking communication between the background thread and UI. By moving shared state to a **separate imported module**, Python's `sys.modules` cache ensures the variables persist.

**Shared variables**:

| Variable | Type | Purpose |
|----------|------|---------|
| `log_queue` | `queue.Queue` | Log messages from background → UI |
| `state_queue` | `queue.Queue` | Status updates from background → UI |
| `log_buffer` | `deque(maxlen=500)` | Circular buffer — authoritative log store |
| `buffer_lock` | `threading.Lock` | Thread-safe access to `log_buffer` |
| `stop_event` | `threading.Event` | Signal background thread to stop |

**Key functions**:
- `add_log(message)` — Thread-safe, callable from any thread
- `set_status(status)` — Queues status update for UI
- `get_all_logs()` — Returns buffer snapshot for UI
- `drain_queue()` — Prevents unbounded queue growth
- `drain_state_queue()` — Returns and clears pending state updates

---

### 3. Folder Monitor

**File**: `core/folder_monitor.py`  
**Class**: `FolderMonitor`

**Polling mechanism**:
- Scans for `.zip` and `.msg` files at configurable intervals
- Uses **file fingerprinting** (size + modification time) for deduplication
- Prevents re-processing of files that haven't changed
- `mark_as_processed()` records the fingerprint after successful processing

**Deduplication logic**:
```
1. Scan folder for .zip/.msg files
2. For each file, compute fingerprint = (file_size, mtime)
3. If filename exists in processed set AND fingerprint matches → skip
4. If filename exists BUT fingerprint differs → treat as new version
5. If filename is new → yield for processing
```

**Also includes**: `RealTimeFolderMonitor` (watchdog-based) retained for future use.

---

### 4. MSG Processor

**File**: `core/msg_processor.py`  
**Class**: `MsgProcessor`

- Uses `extract-msg` library to parse Outlook `.msg` files
- Iterates through email attachments
- Extracts files with `.zip` extension
- Saves extracted ZIPs to the incoming folder for processing

---

### 5. ZIP Processor

**File**: `core/zip_processor.py`  
**Class**: `ZipProcessor`

**Security**: Includes **path traversal protection** — validates all extracted paths stay within the target directory (prevents `../../etc/passwd` style attacks).

**Log file detection**: Searches the extracted directory for:
- `*_oracle.log_completed.log` — main deployment log (required)
- `*_invalids_completed.log` — invalid objects log (required)
- `oracle_error` file (optional)

**Instance detection**: Extracts the instance name from the main log filename:
```
FSMHO1U_oracle.log_completed.log → instance = "FSMHO1U"
```

**Cluster detection**: Maps instance to cluster using `config.json`:
```json
"clusters": { "mena": ["FSMHO1U"] }
```
→ `FSMHO1U` → cluster = `mena`

**Returns metadata dict**:
```python
{
    "instance": "FSMHO1U",
    "cluster": "mena",
    "main_log_path": Path("..."),
    "invalid_log_path": Path("..."),
    "error_log_path": Path("...") or None
}
```

Supports context manager (`with ZipProcessor(...) as zp:`) for automatic cleanup.

---

### 6. Deployment Validator

**File**: `core/validator.py`  
**Class**: `DeploymentValidator`

Performs **three validation checks** in sequence:

#### Check 1: Error Validation (`validate_errors`)
- Extracts ORA error codes and messages from the error log
- Filters against `ignorable_errors` list from config
- If non-ignorable errors remain → **FAIL**

#### Check 2: Invalid Objects Delta (`validate_invalid_delta`)
- Parses the invalids log for objects created with compilation warnings
- Detects objects like packages, triggers, views with invalid status
- If invalid objects found → **FAIL**

#### Check 3: Execution Integrity (`validate_execution_integrity`)
- Verifies all units listed in the log were actually executed
- Detects dropped or skipped compilation units
- If integrity check fails → **FAIL**

**Return format**:
```python
{
    "status": "PASS" | "FAIL",
    "message": "Human-readable summary",
    "error_details": [{"unit": "...", "code": "ORA-00942", "message": "..."}],
    "invalid_objects": [{"object": "...", "type": "PACKAGE BODY"}]
}
```

---

### 7. JIRA Extractor

**File**: `core/jira_extractor.py`  
**Class**: `JiraExtractor`

- Parses the main deployment log
- Extracts JIRA ticket references (e.g., `PROJ-1234`)
- Maps each JIRA ticket to its list of compiled units
- Returns: `{"PROJ-1234": ["unit1.sql", "unit2.sql"], ...}`

---

### 8. Archiver

**File**: `core/archiver.py`  
**Class**: `Archiver`

**Archives deployment results** into a hierarchical folder structure:

```
base_audit_path/
└── Feb_week04_2026/           ← Deployment cycle
    ├── Processed/             ← PASS results
    │   └── mena/FSMHO1U/
    │       ├── logs.zip       ← Original ZIP
    │       └── compiled_units.txt
    └── Failed/                ← FAIL results
        └── ssa/FCCNIG/
            ├── logs.zip
            └── compiled_units.txt
```

**`compiled_units.txt`** contains:
- Deployment cycle name
- Cluster and instance info
- JIRA → unit mappings in a formatted report

Handles duplicate filenames with auto-incrementing suffixes.

---

### 9. Cycle Manager

**File**: `core/cycle_manager.py`  
**Class**: `CycleManager`

**Naming convention**: `{Month}_week{NN}_{Year}` (e.g., `Feb_week04_2026`)

**Week anchoring logic**: Anchored to Fridays for weekend deployment cycles:
- Friday → use this Friday as anchor
- Saturday → anchor to previous Friday
- Sunday → anchor to previous Friday
- Mon–Thu → use current date

All deployments within the same week share the same cycle folder.

---

### 10. Email Sender

**File**: `core/email_sender.py`  
**Class**: `EmailSender`

- Uses **Outlook COM automation** (`win32com.client.Dispatch("Outlook.Application")`)
- Requires classic Outlook desktop installed and running
- Configurable subject and body templates with `{cluster}`, `{instance}`, `{status}`, `{message}` placeholders
- **Retry logic**: 3 retries with exponential backoff (1s, 2s, 4s) for transient COM errors
- Template validation on initialization

---

### 11. Styles

**File**: `styles.py`  
**Function**: `load_css()`

Injects a luxury dark glassmorphic theme into the Streamlit UI:
- Custom fonts (Playfair Display + Inter)
- Gradient backgrounds and buttons
- Glass-effect cards with backdrop blur
- Custom scrollbar and high-contrast inputs

---

## Threading Model

### Streamlit (`app.py`)

```
Main Thread (Streamlit)          Background Thread
─────────────────────────        ─────────────────────
                                 
st.rerun() loop                  run_service()
    │                                │
    ├─ import shared_state ──────────┤ import shared_state
    │  (same module object)          │ (same module object)
    │                                │
    ├─ drain_queue()                 ├─ add_log("...")
    ├─ get_all_logs() ◄──────────── ├─ set_status("PASS")
    ├─ drain_state_queue()           │
    ├─ update st.session_state       │
    ├─ render UI                     │
    ├─ sleep(0.3-2.0s)               │
    └─ st.rerun()                    └─ loop...
```

**Critical rule**: The background thread must **never** call any Streamlit API (`st.*`). All communication goes through `shared_state.py`.

---

## Configuration Schema

```json
{
  "base_audit_path": "string (absolute path)",
  "poll_interval_seconds": "integer (5-300)",
  "clusters": {
    "<cluster_name>": ["<instance1>", "<instance2>"]
  },
  "ignorable_errors": ["ORA-XXXXX"],
  "email_settings": {
    "enabled": "boolean",
    "recipients": ["email@example.com"],
    "subject_templates": {
      "PASS": "string with {cluster}, {instance}",
      "FAIL": "string with {cluster}, {instance}"
    },
    "body_template": "string with {status}, {cluster}, {instance}, {message}"
  }
}
```

---

## Deployment Cycle Structure

The archiver creates the following directory structure:

```
C:\deployment_audit_test\              ← base_audit_path
├── Feb_week03_2026\                   ← Weekly cycle
│   ├── Processed\                     ← PASS
│   │   ├── mena\
│   │   │   └── FSMHO1U\
│   │   │       ├── logs.gatherer.sh.2026-02-21.zip
│   │   │       └── compiled_units.txt
│   │   └── cee\
│   │       └── FMSLO1P\
│   │           └── ...
│   └── Failed\                        ← FAIL
│       └── ssa\
│           └── FCCNIG\
│               ├── logs.gatherer.sh.2026-02-21.zip
│               └── compiled_units.txt
└── Feb_week04_2026\
    └── ...
```

---

## Extending the System

### Adding a New Cluster/Instance
Add the instance name to the appropriate cluster in `config.json`:
```json
"clusters": {
    "mena": ["FSMHO1U", "NEW_INSTANCE"]
}
```

### Adding New Ignorable Error Codes
Append to the `ignorable_errors` list:
```json
"ignorable_errors": ["ORA-00001", "ORA-00955", "ORA-XXXXX"]
```

### Switching to SMTP Email
Replace the Outlook COM logic in `email_sender.py` with Python's `smtplib`:
```python
import smtplib
from email.mime.text import MIMEText

# Use smtp.gmail.com:587 with app password
```

### Adding New Validation Rules
Add a new method to `DeploymentValidator` and call it from `validate_all()`:
```python
def validate_custom_rule(self):
    # Your validation logic
    pass

def validate_all(self):
    # ... existing checks ...
    custom_result = self.validate_custom_rule()
    if custom_result["status"] == "FAIL":
        return custom_result
```
