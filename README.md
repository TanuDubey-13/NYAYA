# ⚖️ NYAYA — From Citizen Problem to Verified Action

> **An AI-powered civic navigator that transforms a citizen's problem into a jurisdiction-aware, evidence-verified action plan and ready-to-submit grievance.**

NYAYA helps citizens navigate municipal and civic processes without requiring them to understand complex administrative procedures or legal terminology.

Instead of functioning as a generic AI chatbot, NYAYA combines **structured AI triage, evidence-based retrieval, deterministic verification, jurisdiction mapping, dynamic action planning, and grievance drafting** into a single workflow.

---

## 🎯 The Problem

Citizens frequently encounter everyday civic problems such as:

* Garbage collection delays
* Broken streetlights
* Potholes and damaged roads
* Water and sanitation issues
* Illegal dumping
* Public infrastructure problems
* Unresolved municipal complaints

The difficulty is often not identifying the problem itself, but understanding:

* Which authority is responsible?
* Which department should handle it?
* What evidence should be collected?
* What procedure should be followed?
* What action should be taken if the complaint is ignored?
* Which information provided by an AI system can actually be trusted?

Traditional AI assistants can generate fluent answers, but they may produce **generic advice, incorrect authorities, unsupported legal claims, or fabricated references**.

NYAYA is designed around a different principle:

> **AI should understand the citizen's problem, but factual verification should be handled by deterministic systems and structured evidence.**

---

# 🚀 What NYAYA Does

NYAYA converts an unstructured citizen complaint into a structured civic case.

```text
Citizen Problem
      ↓
AI Triage
      ↓
Jurisdiction Detection
      ↓
Knowledge Retrieval
      ↓
Evidence Verification
      ↓
Action Plan
      ↓
Grievance Draft
      ↓
Case Timeline
      ↓
Persistent Dashboard
```

The goal is to move the citizen from:

> **"I have a problem. What should I do?"**

to:

> **"I know who is responsible, what evidence supports the information, what action I can take, and what I should do next."**

---

# ⭐ Core Features

## 1. 🔎 Evidence-First Verification

NYAYA does not allow the AI model to independently decide whether a legal or administrative claim is valid.

Instead, claims are evaluated against a structured knowledge corpus.

```text
Claim
  ↓
Normalize
  ↓
Knowledge Corpus Lookup
  ↓
Rule / Authority Matching
  ↓
Verification Engine
  ↓
Verification Status
```

The system produces three states:

### 🟢 Verified

The claim matches supported evidence in the knowledge corpus.

### 🟡 Needs Verification

Additional context or evidence is required before the claim can be confidently used.

### 🔴 Unverified

No reliable supporting evidence was found.

This creates an important distinction between:

> **What the AI generated**

and

> **What the system can actually verify.**

---

# 2. 🤖 Structured Gemini Triage

Citizens can describe their problems naturally.

For example:

> "The garbage hasn't been collected from our street for five days."

Gemini 2.5 Flash converts the description into structured information using schema-constrained output.

```json
{
  "category": "Waste Management",
  "subcategory": "Missed Collection",
  "urgency": "Medium",
  "location": "Kanpur",
  "jurisdiction_complete": true
}
```

The AI is responsible for:

* Problem classification
* Information extraction
* Subcategory identification
* Urgency estimation
* Location extraction
* Detecting missing information
* Generating clarification requests

The AI is **not treated as the final authority for factual or legal verification**.

---

# 3. 🏛️ Jurisdiction-Aware Guidance

Civic procedures vary by location.

NYAYA therefore treats jurisdiction as a first-class part of the case.

```text
Problem
   ↓
Location
   ↓
Jurisdiction
   ↓
Department
   ↓
Responsible Authority
   ↓
Applicable Evidence
```

If required location or jurisdiction information is missing:

```text
Incomplete Jurisdiction
        ↓
Clarification Request
        ↓
Additional Context
        ↓
Continue Verification
```

NYAYA avoids confidently guessing the responsible authority when sufficient information is unavailable.

---

# 4. 📋 Dynamic Action Plans

Instead of returning a long block of generic advice, NYAYA generates structured actions.

Example:

```text
CASE: Missed Garbage Collection

☑ Collect photographs/videos
☑ Record the affected location
☑ Document the dates of missed collection
☑ Submit a municipal complaint
☑ Attach supporting evidence
☑ Save the complaint/reference number
☑ Track the complaint
☑ Follow the appropriate escalation path if unresolved
```

Each action can be associated with:

* Responsible authority
* Supporting evidence
* Reason for the action
* Required documentation
* Verification status

---

# 5. 📄 Dynamic Grievance Drafting

NYAYA generates context-aware grievance documents based on the citizen's case.

The draft can incorporate:

* Citizen-provided information
* Problem classification
* Location
* Responsible authority
* Verified facts
* Supporting evidence
* Appropriate grievance structure

The system is designed to avoid inserting unsupported legal claims simply because they sound convincing.

---

# 6. 👤 Guest-to-User Account Mapping

Citizens can begin using NYAYA without creating an account.

### Guest Experience

```text
Describe Problem
      ↓
Explore Guidance
      ↓
Build Action Plan
      ↓
Generate Draft
```

When the citizen chooses to save their work:

```text
Guest Session
      ↓
Firebase Authentication
      ↓
User Account
      ↓
Existing Case Data
      ↓
Persistent Dashboard
```

This allows users to explore the system without unnecessary onboarding while preserving their work when they create an account.

---

# 7. 📅 Case Timeline

NYAYA represents a civic complaint as an evolving case rather than a one-time AI conversation.

```text
Problem Identified
        ↓
Information Collected
        ↓
Action Plan Created
        ↓
Grievance Drafted
        ↓
Complaint Submitted
        ↓
Under Review
        ↓
Resolved / Escalated
```

This gives citizens a structured view of what has happened and what remains to be done.

---

# 🧠 AI + Deterministic Architecture

One of NYAYA's most important design decisions is separating **AI interpretation** from **factual verification**.

```text
                    NYAYA
                      │
          ┌───────────┴───────────┐
          │                       │
       AI Layer             Deterministic Layer
          │                       │
    Gemini 2.5 Flash        Knowledge Corpus
          │                       │
    Classification          Rule Matching
    Entity Extraction       Authority Mapping
    Urgency Detection       Evidence Validation
    Clarification           Verification
          │                       │
          └───────────┬───────────┘
                      ↓
               Verified Result
                      ↓
                Action Plan
                      ↓
               Grievance Draft
                      ↓
                 Case Timeline
```

### Design Principle

> **AI understands. Evidence verifies. The application orchestrates action.**

This architecture helps reduce hallucination risks while still benefiting from the flexibility of generative AI.

---

# 🏗️ System Architecture

```mermaid
graph TD

    A[Citizen Input] --> B[Gemini Triage Agent]

    B --> C{Jurisdiction Complete?}

    C -- No --> D[Clarification Request]

    C -- Yes --> E[RAG / Knowledge Repository]

    E --> F[Deterministic Verification Engine]

    F --> G{Evidence Status}

    G -->|Verified| H[Action Plan Compiler]
    G -->|Needs Verification| I[Clarification / Source Request]
    G -->|Unverified| J[Do Not Present as Fact]

    H --> K[Document Draft Compiler]

    K --> L[Timeline State Machine]

    L --> M[User Dashboard]

    M --> N[Firestore Persistence]
```

---

# 🧑‍💻 Example User Journey

### Citizen Input

> "There is a large pothole outside my house and vehicles are struggling to pass safely."

### AI Triage

```text
Category: Roads & Infrastructure
Issue: Pothole
Urgency: High
Location: Kanpur
```

### Jurisdiction Check

```text
Location
   ↓
Municipal Jurisdiction
   ↓
Responsible Department
```

### Evidence Retrieval

NYAYA searches its structured civic knowledge corpus.

### Verification

```text
Authority Match: ✓
Service Match: ✓
Supporting Evidence: ✓

Status: 🟢 VERIFIED
```

### Action Plan

```text
1. Capture photographs
2. Record the exact location
3. Submit the complaint
4. Attach supporting evidence
5. Save the complaint/reference number
6. Track resolution
7. Follow the applicable escalation process
```

### Grievance

NYAYA generates a structured complaint using the verified case information.

### Timeline

The case can then be tracked through its lifecycle.

---




# 🛠️ Technology Stack

| Layer             | Technology                            |
| ----------------- | ------------------------------------- |
| Frontend          | React, TypeScript, Vite               |
| Backend           | Python, FastAPI                       |
| Validation        | Pydantic                              |
| AI                | Google Gemini 2.5 Flash               |
| Retrieval         | Structured Knowledge Corpus / RAG     |
| Verification      | Deterministic Verification Engine     |
| Authentication    | Firebase Authentication               |
| Database          | Cloud Firestore                       |
| API Communication | REST                                  |
| Testing           | Python Regression & Integration Tests |

---

# 📁 Project Structure

```text
NYAYA/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth/
│   │   │   └── cases/
│   │   │
│   │   ├── data/
│   │   │   ├── knowledge/
│   │   │   └── templates/
│   │   │
│   │   ├── schemas/
│   │   │   ├── triage.py
│   │   │   └── case.py
│   │   │
│   │   └── services/
│   │       ├── rag/
│   │       ├── verification/
│   │       ├── documents/
│   │       └── firestore/
│   │
│   ├── test_phase1.py
│   ├── test_gemini_triage.py
│   └── test_phase4_auth_firestore.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── RightsPanel/
│   │   │   ├── CaseDashboard/
│   │   │   ├── Editor/
│   │   │   └── Timeline/
│   │   │
│   │   ├── utils/
│   │   │   ├── api.ts
│   │   │   └── firebase.ts
│   │   │
│   │   └── App.tsx
│   │
│   └── package.json
│
├── docs/
│   └── screenshots/
│
└── README.md
```

---

# 🔐 Environment Configuration

## Backend

Create:

```text
backend/.env
```

```env
GEMINI_API_KEY=your_gemini_api_key

FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n"
```

Firebase Admin credentials can be obtained from:

**Firebase Console → Project Settings → Service Accounts → Generate New Private Key**

---

## Frontend

Create:

```text
frontend/.env
```

```env
VITE_API_URL=http://localhost:8000

VITE_FIREBASE_API_KEY=your_client_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### ⚠️ Security

Never commit credentials or secrets to Git.

Recommended `.gitignore` entries:

```gitignore
.env
.env.*
!.env.example

backend/venv/
__pycache__/
*.pyc

firebase-service-account*.json
```

Only commit `.env.example` files containing placeholder values.

---

# 🏃 Installation & Setup

## Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

Run tests:

```bash
python test_phase1.py
python test_gemini_triage.py
python test_phase4_auth_firestore.py
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

---

## Frontend

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Open:

```text
http://localhost:5173
```

---

# 🧪 Testing & Reliability

NYAYA includes tests for critical application components.

### Current Test Areas

```text
✓ RAG retrieval
✓ Knowledge corpus lookup
✓ Verification logic
✓ Gemini structured output
✓ Jurisdiction handling
✓ Authentication
✓ Firestore persistence
✓ Guest → authenticated case migration
```

The test suite is designed to help prevent regressions in the parts of the system responsible for **retrieval, verification, AI structured output, and user data persistence**.

> Add the exact number of passing tests here once the complete test suite has been executed.

---

# 🛡️ Safety & Reliability

NYAYA operates in a civic and legal-adjacent domain where incorrect information can have real-world consequences.

### Reliability Principles

* AI-generated content is not automatically considered verified.
* Claims require supporting evidence before receiving a **Verified** status.
* Missing jurisdiction information triggers clarification instead of guessing.
* Unsupported authorities are not fabricated.
* Unsupported laws, deadlines, or regulations are not presented as established facts.
* Verification status is visible to the user.
* The system distinguishes retrieved evidence from generated content.
* NYAYA does not replace a lawyer or qualified legal professional.
* Knowledge coverage depends on the jurisdictions and sources available in the system.

### Core Safety Principle

> **When NYAYA cannot verify something, it should communicate uncertainty rather than confidently invent an answer.**

---

# 🌍 Jurisdiction Coverage

NYAYA is designed to support multiple cities, departments, and civic services.

Coverage should always be explicitly tied to the available knowledge corpus.

Example:

```text
Kanpur
├── Waste Management
├── Roads / Potholes
└── Street Lighting

Bengaluru
├── Supported Department
└── Supported Department
```

> NYAYA does not assume that a rule, authority, or procedure applies outside a supported jurisdiction.

As the knowledge corpus grows, additional cities and departments can be added without changing the fundamental application architecture.

---

# 📈 Scalability

The architecture is designed to expand beyond a single municipality.

### Current Architecture

```text
Citizen
   ↓
Triage
   ↓
Jurisdiction
   ↓
Knowledge Corpus
   ↓
Verification
   ↓
Action
```

### Scaled Architecture

```text
                    NYAYA
                      │
       ┌──────────────┼──────────────┐
       ↓              ↓              ↓
    Kanpur         Bengaluru       Other Cities
       │              │              │
   Knowledge      Knowledge       Knowledge
    Corpus         Corpus          Corpus
       │              │              │
       └──────────────┼──────────────┘
                      ↓
             Shared Verification
                  Framework
```

This allows new jurisdictions to be added primarily through **knowledge and configuration**, rather than rebuilding the complete application.

---

# 🚀 Roadmap

## Phase 1 — Core Platform

* [x] AI civic triage
* [x] Structured output
* [x] Jurisdiction detection
* [x] Evidence retrieval
* [x] Deterministic verification
* [x] Action-plan generation
* [x] Grievance drafting
* [x] Firebase authentication
* [x] Firestore persistence
* [x] Case timeline

## Phase 2 — Expansion

* [ ] Expand municipal knowledge corpus
* [ ] Multi-city support
* [ ] More civic departments
* [ ] Additional official sources
* [ ] Complaint status synchronization
* [ ] Improved evidence management

## Phase 3 — Accessibility

* [ ] Hindi and additional Indian-language support
* [ ] Voice-based interaction
* [ ] Accessibility-first interface
* [ ] Mobile-first experience
* [ ] WhatsApp/SMS workflows

## Phase 4 — Civic Infrastructure

* [ ] Government API integrations
* [ ] Automated complaint tracking
* [ ] Escalation monitoring
* [ ] Analytics for recurring civic problems
* [ ] Aggregated infrastructure issue insights

---

# 🔭 Long-Term Vision

NYAYA aims to become a **trusted civic action layer** connecting citizens with public institutions.

The long-term goal is not simply to build another AI assistant.

It is to create a system where citizens can move from:

```text
"I have a civic problem."
```

to:

```text
"I know the responsible authority."
        ↓
"I know what evidence supports my case."
        ↓
"I know what action I can take."
        ↓
"I have a ready-to-submit grievance."
        ↓
"I can track what happens next."
```

---

# 👤 About the Project

**NYAYA** is an independent software project exploring how generative AI, retrieval systems, deterministic verification, and civic information can be combined to create more trustworthy citizen-facing applications.

The project focuses on one central question:

> **How can AI make civic processes easier without making factual reliability worse?**

NYAYA's architecture approaches this by keeping **AI interpretation** and **evidence verification** as separate responsibilities.

---



## NYAYA

### **From Citizen Problem to Verified Action.**
