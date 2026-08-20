# ⚖️ NYAYA — From Citizen Problem to Verified Action

> **An AI-powered civic navigator that transforms a citizen's problem into a jurisdiction-aware, evidence-verified action plan and ready-to-submit grievance.**

**Hackathon Submission:** AI for Civic & Legal Empowerment

---

## 🎯 The Problem

Citizens frequently struggle with everyday civic problems:

* Garbage collection delays
* Broken streetlights
* Potholes and damaged roads
* Water and sanitation issues
* Illegal dumping
* Municipal service failures

The challenge isn't simply knowing **what the problem is**. Citizens often don't know:

* Which authority is responsible?
* What rules or procedures apply?
* What evidence should they collect?
* Where should they submit the complaint?
* What should they do if the complaint is ignored?
* Which information provided by an AI system can actually be trusted?

Traditional AI chatbots can generate convincing answers but may hallucinate authorities, regulations, deadlines, or legal claims.

### 💡 NYAYA's Approach

**NYAYA doesn't treat an AI-generated statement as a fact.**

It separates:

> **AI-powered understanding** from **deterministic verification.**

The AI understands the citizen's problem.
The verification engine determines what can actually be presented as verified.

---

# 🚀 What Makes NYAYA Different?

| Traditional AI Chatbot          | NYAYA                                               |
| ------------------------------- | --------------------------------------------------- |
| Generic conversational response | Structured civic case                               |
| May hallucinate rules           | Claims require evidence                             |
| Generic advice                  | Jurisdiction-specific actions                       |
| User finds authority themselves | Authority mapped from verified data                 |
| One-shot answer                 | Problem → Verification → Action → Draft → Tracking  |
| AI output treated as answer     | AI output separated from verification               |
| Generic document generation     | Context-aware grievance drafting                    |
| No clear confidence state       | 🟢 Verified / 🟡 Needs Verification / 🔴 Unverified |
| Primarily chat-focused          | Case-management focused                             |

### 🧠 Core Principle

> **AI understands the citizen. Deterministic systems decide what can be trusted.**

---

# ⭐ Key Innovations

## 1. 🔎 Evidence-First Verification

NYAYA does **not** allow Gemini to independently decide whether a legal or administrative claim is valid.

Instead:

```text
Claim
  ↓
Normalize
  ↓
Knowledge Corpus Lookup
  ↓
Authority / Rule Matching
  ↓
Evidence Found?
  ↓
Verification Engine
  ↓
🟢 Verified
🟡 Needs Verification
🔴 Unverified
```

A claim becomes **Verified only when it matches the structured knowledge corpus and satisfies the verification rules.**

This reduces the risk of fabricated authorities, regulations, and unsupported legal claims.

---

## 2. 🤖 Structured Gemini Triage

Citizens describe problems naturally.

For example:

> "Garbage hasn't been collected from our street for five days."

Gemini 2.5 Flash converts the description into structured data using strict schemas:

```json
{
  "category": "Waste Management",
  "subcategory": "Missed Collection",
  "urgency": "Medium",
  "location": "Kanpur",
  "jurisdiction_complete": true
}
```

Gemini is used for:

* Classification
* Information extraction
* Location markers
* Urgency assessment
* Clarification detection

It is **not trusted as the final source of legal truth.**

---

## 3. 🏛️ Jurisdiction-Aware Guidance

A civic solution is only useful if it identifies the correct authority.

NYAYA checks:

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

If required jurisdiction information is missing:

```text
Citizen Input
      ↓
Jurisdiction Incomplete
      ↓
❓ Clarification Request
      ↓
Continue only after sufficient context
```

NYAYA avoids guessing when the location or authority cannot be reliably determined.

---

## 4. 📋 Dynamic Action Plans

Instead of returning a wall of text, NYAYA converts verified information into actionable steps.

Example:

```text
CASE: Missed Garbage Collection

☑ Collect photographs/videos
☑ Record affected location
☑ Submit municipal complaint
☑ Attach supporting evidence
☑ Record complaint/reference number
☑ Track resolution
☑ Escalate if the issue remains unresolved
```

Each action can contain:

* Why the action matters
* Responsible authority
* Required evidence
* Supporting source
* Verification status

---

## 5. 📄 Dynamic Grievance Drafting

NYAYA generates context-aware complaint drafts using:

* Citizen's problem
* Location
* Responsible authority
* Verified facts
* Evidence collected
* Relevant complaint format

The system helps citizens produce a structured grievance without presenting unsupported legal claims as facts.

---

## 6. 👤 Guest-to-User Account Mapping

Citizens don't need to create an account before exploring the system.

### Guest Mode

```text
Describe Problem
      ↓
Explore Rights
      ↓
Build Action Plan
      ↓
Generate Draft
```

When the citizen chooses to save the case:

```text
Guest Session
      ↓
Firebase Authentication
      ↓
User Account
      ↓
Existing Case Data Migrated
      ↓
Persistent Dashboard
```

This removes unnecessary onboarding friction while preserving user-created work.

---

# 🧪 Verification States

NYAYA makes information reliability visible to the citizen.

### 🟢 VERIFIED

The claim matches supported evidence in the knowledge corpus.

### 🟡 NEEDS VERIFICATION

The available information is insufficient or additional context is required.

### 🔴 UNVERIFIED

No reliable supporting evidence was found.

> **NYAYA does not automatically convert an unsupported AI-generated claim into a legal or administrative fact.**

---

# 🧑‍💻 Example User Journey

### Citizen Problem

> "There is a large pothole outside my house and it is becoming dangerous for vehicles."

### Step 1 — AI Triage

```text
Category: Roads & Infrastructure
Issue: Pothole
Urgency: High
Location: Kanpur
```

### Step 2 — Jurisdiction Check

```text
Location
   ↓
Municipal Jurisdiction
   ↓
Responsible Department
```

### Step 3 — Evidence Search

NYAYA searches its structured civic knowledge corpus.

### Step 4 — Deterministic Verification

```text
Authority Match: ✓
Service Match: ✓
Supporting Evidence: ✓

Status: 🟢 VERIFIED
```

### Step 5 — Action Plan

```text
1. Capture photographs
2. Record exact location
3. Submit complaint
4. Attach evidence
5. Save complaint/reference number
6. Track resolution
7. Escalate when applicable
```

### Step 6 — Grievance Draft

NYAYA generates a structured complaint addressed to the appropriate authority.

### Step 7 — Case Timeline

```text
Problem Identified
       ↓
Draft Created
       ↓
Complaint Submitted
       ↓
Under Review
       ↓
Resolved
```

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

# 🧠 AI vs Deterministic Layer

One of NYAYA's core architectural decisions is separating AI reasoning from factual verification.

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
    Entity Extraction        Authority Mapping
    Urgency Detection        Evidence Validation
    Clarification            Verification Status
          │                       │
          └───────────┬───────────┘
                      ↓
               Verified Result
                      ↓
                Action Plan
                      ↓
               Grievance Draft
```

---

# 🛠️ Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Modern component-based UI

### Backend

* Python
* FastAPI
* Pydantic
* REST APIs

### AI

* Google Gemini 2.5 Flash
* Structured JSON / schema-constrained triage

### Knowledge & Retrieval

* Structured civic knowledge corpus
* RAG / retrieval layer
* Deterministic verification engine

### Authentication & Persistence

* Firebase Authentication
* Cloud Firestore

### Testing

* Python regression tests
* Gemini triage tests
* Authentication & Firestore integration tests

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
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── RightsPanel/
    │   │   ├── CaseDashboard/
    │   │   ├── Editor/
    │   │   └── Timeline/
    │   │
    │   ├── utils/
    │   │   ├── api.ts
    │   │   └── firebase.ts
    │   │
    │   └── App.tsx
    │
    └── package.json
```

---

# 🖥️ Product Preview

> Add actual screenshots here before submitting the hackathon project.

### 1. Problem Input

```text
docs/screenshots/problem-input.png
```

### 2. AI Triage

```text
docs/screenshots/triage.png
```

### 3. Evidence Verification

```text
docs/screenshots/verification.png
```

### 4. Action Plan

```text
docs/screenshots/action-plan.png
```

### 5. Generated Grievance

```text
docs/screenshots/grievance.png
```

### 6. Case Timeline

```text
docs/screenshots/timeline.png
```

---

# 🛡️ Safety & Reliability

NYAYA is designed specifically for civic and legal-adjacent use cases where incorrect information can cause real-world harm.

### Reliability Principles

* AI-generated content is not automatically considered verified.
* Claims require supporting evidence before receiving a **Verified** status.
* Missing jurisdiction information triggers clarification instead of guessing.
* Unsupported authorities are not fabricated.
* Unsupported laws, deadlines, and regulations are not presented as facts.
* Verification status is visible to the user.
* NYAYA does not replace a lawyer or qualified legal professional.
* Knowledge coverage is limited to supported jurisdictions and sources.

### Coverage Principle

> **If NYAYA cannot verify something, it should say so rather than confidently invent an answer.**

---

# 🧪 Testing & Reliability

NYAYA includes dedicated tests for critical components.

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

Run:

```bash
python test_phase1.py
python test_gemini_triage.py
python test_phase4_auth_firestore.py
```

> Add the actual test count here once verified, for example: **"XX tests passing."**

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

Never commit:

```text
.env
.env.*
Firebase service-account JSON files
API keys
Private keys
```

Use `.gitignore` and provide only `.env.example` files in the repository.

---

# 🏃 Quick Start

## 1. Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

python test_phase1.py
python test_gemini_triage.py
python test_phase4_auth_firestore.py

uvicorn app.main:app --reload --port 8000
```

---

## 2. Frontend

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

# 🎮 Demo

**Live Demo:** `ADD_YOUR_DEPLOYED_URL`

**Repository:** `ADD_YOUR_GITHUB_URL`

**Demo Video:** `ADD_YOUR_VIDEO_URL`

### Recommended Demo Flow

For the hackathon demo, demonstrate:

```text
1. Enter a real civic problem
          ↓
2. Gemini extracts structured information
          ↓
3. Jurisdiction is identified
          ↓
4. Evidence is retrieved
          ↓
5. Verification badge appears
          ↓
6. Action plan is generated
          ↓
7. Grievance is drafted
          ↓
8. Case timeline is created
          ↓
9. User saves the case
```

---

# 🌍 Jurisdiction Coverage

NYAYA is designed to be extensible across cities and municipal departments.

Current verified coverage should be explicitly listed here:

```text
Example:

✓ Kanpur
  ├── Waste Management
  ├── Roads / Potholes
  └── Street Lighting

✓ Bengaluru
  ├── [Supported Department]
  └── [Supported Department]
```

> **NYAYA does not assume that a rule or authority applies outside the jurisdictions represented in its verified knowledge corpus.**

---

# 🚀 Future Roadmap

### Phase 1 — Current

* AI civic triage
* Jurisdiction detection
* Evidence-backed verification
* Dynamic action plans
* Grievance drafting
* Firebase authentication
* Case persistence
* Timeline tracking

### Phase 2

* Expand municipal knowledge corpus
* Multi-city support
* More civic departments
* Official government API integrations
* Complaint status synchronization

### Phase 3

* Multilingual Indian-language support
* Voice-based civic assistance
* WhatsApp/SMS workflows
* Accessibility-first interfaces
* Automated escalation tracking

---

# 💡 Long-Term Vision

NYAYA aims to become a **trusted civic action layer** between citizens and public institutions.

Instead of asking:

> "What does the AI think I should do?"

Citizens should be able to ask:

> **"What can I do, which authority is responsible, what evidence supports this, and what should I do next?"**

NYAYA turns that question into a structured, evidence-aware workflow.

---

# 🏆 Hackathon Pitch

### The Problem

Citizens know their problem but often don't know the correct bureaucratic path.

### The Solution

**NYAYA converts a natural-language civic complaint into a verified, jurisdiction-aware action plan.**

### The Innovation

**AI performs understanding. Deterministic systems perform verification.**

### The Impact

Citizens receive:

**Problem → Authority → Evidence → Action → Grievance → Timeline**

instead of another generic chatbot response.

---

# 📌 Why NYAYA Matters

> **NYAYA doesn't just tell citizens what an AI thinks.**
>
> **It helps them understand what can be verified, who is responsible, what action they can take, and how to move the case forward.**

---

## 👥 Team

**Team Name:** `ADD_TEAM_NAME`

**Team Members:**

* `Member 1`
* `Member 2`
* `Member 3`
* `Member 4`

---

## 📄 License

Add your project license here.

---

**Built for AI-powered civic and legal empowerment.**

**NYAYA — From Citizen Problem to Verified Action.**
