# ABC Technologies — AI-Powered Customer Support Automation System
### Built with LangGraph, FAISS & SQLite

---

## Overview

This project implements an **AI-Powered Customer Support Automation System** for **ABC Technologies**. The system leverages **LangGraph** for workflow orchestration, **FAISS** for Retrieval-Augmented Generation (RAG) based knowledge retrieval, and **SQLite** for persistent conversation memory. It intelligently classifies customer queries, routes them to specialized AI agents, retrieves relevant information from a knowledge base, and ensures quality responses through a supervisor agent.

---

## Architecture

```text
START
  │
  ▼
Intent Classification
  │
  ├──► Sales Agent ───────────────────────────────► Supervisor Agent ─► END
  │
  ├──► Technical Support Agent ───────────────────► Supervisor Agent ─► END
  │
  ├──► Billing Agent
  │         │
  │         ├──► High-Risk Request?
  │         │        ├── YES ─► Human Approval ─► Supervisor Agent ─► END
  │         │        └── NO  ─► Supervisor Agent ─► END
  │
  ├──► Account Management Agent ─────────────────► Supervisor Agent ─► END
  │
  └──► Memory Recall Agent ──────────────────────► Supervisor Agent ─► END
```

---

## Features (Tasks Completed)

| Task | Description | File |
|------|-------------|------|
| 1 | LangGraph Workflow Assembly | `src/graph.py` |
| 2 | Shared State Management | `src/state.py` |
| 3 | Intent Classification Node | `src/intent.py` |
| 4 | Conditional Routing Logic | `src/router.py` |
| 5 | Department-Specific AI Agents | `src/agents.py` |
| 6 | FAISS RAG Knowledge Retrieval | `src/rag.py` |
| 7 | SQLite Conversation Memory | `src/memory.py` |
| 8 | Human-in-the-Loop Approval | `src/human_loop.py` |
| 9 | Supervisor Quality Review | `src/supervisor.py` |
| 10 | End-to-End Demo with Sample Queries | `demo.py` |

---

## Project Structure

```text
customer_support_system/
├── src/
│   ├── __init__.py
│   ├── graph.py
│   ├── state.py
│   ├── intent.py
│   ├── router.py
│   ├── agents.py
│   ├── rag.py
│   ├── memory.py
│   ├── human_loop.py
│   └── supervisor.py
│
├── docs/
│   ├── company_policy.txt
│   ├── pricing_guide.txt
│   ├── technical_manual.txt
│   └── faq.txt
│
├── diagrams/
│   └── workflow.png
│
├── demo.py
├── memory.db
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Extract or Clone the Project

```bash
unzip customer_support_system.zip
cd customer_support_system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

### 3. Install Required Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python demo.py
```

---

## Demo Queries

| # | Customer Query | Workflow |
|---|----------------|----------|
| 1 | What are the pricing plans available? | Sales Agent |
| 2 | I forgot my account password. | Account Management Agent |
| 3 | My application crashes when uploading a file. | Technical Support Agent |
| 4 | I need a refund for my annual subscription. | Billing Agent → Human Approval |
| 5 | What was my previous support issue? | Memory Recall Agent |

---

## Human-in-the-Loop

The system automatically invokes **Human Approval** for sensitive customer requests such as:

- Refund requests
- Subscription cancellations
- Account closure
- Customer compensation
- Critical escalations

For demonstration purposes:

- **Demo Mode:** `AUTO_APPROVE = True`
- **Production Mode:** Set `AUTO_APPROVE = False` in `src/human_loop.py` to enable manual approval or integrate with an external ticketing system.

---

## SQLite Memory Schema

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    intent TEXT,
    department TEXT
);
```

The conversation history is stored in **memory.db**, enabling persistent memory across interactions.

---

## Knowledge Base Documents

| Document | Purpose |
|----------|---------|
| `company_policy.txt` | Company policies, refunds, cancellations, compensation and SLA information |
| `pricing_guide.txt` | Subscription plans, pricing, billing details and discounts |
| `technical_manual.txt` | Installation guides, troubleshooting steps and error codes |
| `faq.txt` | Frequently asked questions related to sales, billing, accounts and technical support |

---

## Support Departments

| Department | Responsibilities |
|------------|------------------|
| **Sales** | Product information, pricing, subscriptions and free trials |
| **Technical Support** | Software issues, crashes, installation and troubleshooting |
| **Billing** | Payments, invoices, refunds and subscription management |
| **Account Management** | Password resets, profile updates, account activation and verification |
| **Memory Recall** | Retrieves previous customer conversations using SQLite memory |

---

## Technologies Used

- Python
- LangGraph
- LangChain
- FAISS
- SQLite
- Retrieval-Augmented Generation (RAG)
- OpenAI Compatible LLM

---

## License

This project is developed for educational purposes as part of an academic assignment. **ABC Technologies** is a fictional organization used solely for demonstration and learning.
