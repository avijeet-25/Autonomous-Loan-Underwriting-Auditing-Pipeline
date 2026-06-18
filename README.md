---
title: Loan Underwriting Agent
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
========================================================================
AEGIS: AUTONOMOUS LOAN UNDERWRITING & AUDITING MULTI-AGENT PIPELINE
========================================================================

Aegis is an enterprise-grade, event-driven multi-agent orchestration 
pipeline designed to automate risk profiling, financial sanity auditing, 
and compliance monitoring for credit applications. 

Powered by LangGraph and Gemini 2.5 Flash, the system decouples complex 
underwriting criteria into specialized, sovereign AI agents that collaborate 
via an asynchronous state-machine topology to eliminate human bias and 
accelerate credit decisioning pipeline latency.

------------------------------------------------------------------------
1. ARCHITECTURAL TOPOLOGY & AGENT ROLES
------------------------------------------------------------------------

The core engine is built as an explicit directed acyclic state graph 
(DAG) where context, short-term conversational history, and structural 
payloads are seamlessly synchronized across execution boundaries:

* DATA INGESTION ENGINE: Validates incoming raw JSON profile streams, 
  seeds state vectors, and evaluates presence of compulsory documentation.
* FINANCIAL ANALYST AGENT: Evaluates balance sheets, operating vintage, 
  Debt Service Coverage Ratio (DSCR), and CIBIL bureau scores.
* COMPLIANCE AUDITOR AGENT: Audits the evaluation data against strict 
  jurisdictional guidelines, tax verified status (PAN/ITR), and legal boundaries.
* PYDANTIC SANITY GUARDRAIL: A compilation abstraction layer that intercepts 
  final structured responses to guarantee 100% data schema compliance 
  before serialization to the user interface.

------------------------------------------------------------------------
2. SYSTEM DIRECTORY TREE
------------------------------------------------------------------------

Autonomous-Loan-Underwriting-Auditing-Pipeline/
│
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI Application Server & Global Context
│   ├── graph.py           # LangGraph Topology & Specialized Nodes
│   ├── schemas.py         # Pydantic Enforcement Model Layer
│   └── agents.py          # Core Agent Prompts & LLM Tool Interfaces
│
├── frontend/
│   └── app.py             # Streamlit User Interface & Real-time Ledger Stream
│
├── .env                   # Local Environment Variables (Git-Ignored)
└── requirements.txt       # Unified Project Software Dependencies

------------------------------------------------------------------------
3. PREREQUISITES & ENVIRONMENT SETUP
------------------------------------------------------------------------

Ensure you have Python 3.11+ installed on your local workstation environment.

Step 1: Clone the Project Repository
    $ cd Autonomous-Loan-Underwriting-Auditing-Pipeline

Step 2: Install Project System Dependencies
    $ pip install -r requirements.txt

    *Note: If encountering interpreter environment compilation mismatches, run:
    $ python -m pip install -r requirements.txt

Step 3: Setup Google AI Studio API Access Key
    Create a `.env` file in the project's root directory:
    
    GOOGLE_API_KEY=AIzaSy...[Your-Actual-Gemini-API-Key]

------------------------------------------------------------------------
4. RUNNING THE NATIVE DEVELOPMENT PIPELINE
------------------------------------------------------------------------

The framework utilizes a decoupled client-server architecture. You must 
initialize the asynchronous backend process before executing the frontend UI.

Step 1: Boot the FastAPI Asynchronous Server Instance
    Open a terminal window in the project root directory and run:
    $ uvicorn app.main:app --reload --port 8000

    Ensure the console stream concludes with:
    "INFO: Application startup complete."

Step 2: Boot the Streamlit Operational Control Console
    Open a secondary distinct terminal session in the project root and run:
    $ streamlit run frontend/app.py

    The frontend web platform will automatically bind and initialize inside 
    your native default browser engine at: http://localhost:8501

------------------------------------------------------------------------
5. DOCKER CONTAINERIZATION & PRODUCTION DEPLOYMENT
------------------------------------------------------------------------

To preserve total infrastructure parity across staging, sandbox, and 
production cloud nodes, this architecture is fully Docker containerized.

To compile and execute the system container locally:
    $ docker build -t aegis-underwriting-pipeline .
    $ docker run -p 8501:8501 --env-file .env aegis-underwriting-pipeline

Production Destination (Portfolio Demonstration Hub):
* This pipeline is tailored for immediate deployment onto Hugging Face Spaces 
  using the Native Docker SDK container registry runner.
* Set your Google AI Studio Credentials safely using Hugging Face's native 
  Repository Secrets Management portal (`GOOGLE_API_KEY`) to keep deployment 
  keys private.

------------------------------------------------------------------------
6. RUNTIME CONSTRAINTS & RATE LIMIT HANDLING (429 QUOTA)
------------------------------------------------------------------------

* The Gemini 2.5 Flash Free Tier includes a strict baseline threshold 
  of 20 Requests Per Day (RPD) per Project Container.
* Because a singular autonomous profile evaluation triggers consecutive 
  agent hops (Data Ingestion -> Financial Analyst -> Compliance Auditor), 
  submitting 3-4 evaluation profiles sequentially can exhaust daily quotas.
* Solution for extended demos: If a hard quota limits testing, log into 
  Google AI Studio, instantiate a "New Project Workspace," pull a fresh 
  API string, and drop it into your local workspace.
========================================================================