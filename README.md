# NYAYA — From Citizen Problem to Verified Action

> **Hackathon Submission:** AI for Civic & Legal Empowerment  
> *Empowering citizens to navigate municipal bureaucracies with verified facts, dynamic action plans, and automated grievance drafting.*

---

## ⚖️ The Problem We Solve
Citizens often face legalese, opaque processes, and bureaucratic bottlenecks when dealing with everyday civic problems—like garbage collection delays, broken streetlights, or pothole repairs. Existing AI solutions often act as generic chatbots that hallucinate rules, fabricate government authorities, and offer generic, unhelpful advice.

**NYAYA changes this.** It is a structured civic navigator that guides the citizen from problem description to verified administrative action.

---

## 🚀 Key Innovations
1. **Evidence-First Verification (No Hallucinations):** NYAYA does *not* allow the AI model to decide whether a legal claim or authority is valid. Verification status is determined deterministically by mapping claims against a structured knowledge corpus of municipal guidelines and bye-laws.
2. **Structured Gemini Triage:** Natural citizen descriptions are processed by **Gemini 2.5 Flash** using strict JSON schemas to extract categories, subcategories, urgency levels, and location markers without guessing or fabricating data.
3. **Guest-to-User Account Mapping:** Citizens can navigate their rights and compile full action plans anonymously as guests. Once they choose to save their data, Firebase Auth merges their anonymous session folders into secure user profiles.
4. **Action Plans & Dynamic Drafts:** NYAYA compiles specialized checklists and pre-fills standard legal/grievance formats with correct target authorities (e.g. BBMP, Kanpur Corporation) while preserving safety warnings.

---

## 🛠️ System Architecture

```mermaid
graph TD
    A[Citizen Input] --> B[Gemini Triage Agent]
    B --> C{Jurisdiction Complete?}
    C -- No --> D[Clarification Request]
    C -- Yes --> E[RAG Repository Search]
    E --> F[Deterministic Verification Engine]
    F --> G[Action Plan Compiler]
    G --> H[Document Draft Compiler]
    H --> I[Timeline State Machine]
    I --> J[User Dashboard & Persistence]
```

---

## 📁 Project Structure
```
NYAYA/
├── backend/
│   ├── app/
│   │   ├── api/          # auth & cases endpoints
│   │   ├── data/         # knowledge corpus & templates
│   │   ├── schemas/      # Pydantic models (TriageResult, CaseDocument)
│   │   └── services/     # RAG, verification, documents, firestore repo
│   ├── test_phase1.py    # RAG regression tests
│   ├── test_gemini_triage.py
│   └── test_phase4_auth_firestore.py
└── frontend/
    ├── src/
    │   ├── components/   # RightsPanel, CaseDashboard, Editor, Timeline
    │   ├── utils/        # Centralized api client & firebase auth stubs
    │   └── App.tsx       # State navigator
```

---

## ⚙️ Setting Up Environment Variables

To run the application, you need to configure the following environment files.

### 1. Backend Config (`backend/.env`)
Create a file named `.env` inside the `backend` folder:

```env
# 1. Gemini AI Credentials
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere

# 2. Firebase Admin SDK (Used for Firestore & Auth Token Verification)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
# Note: Ensure the private key is enclosed in quotes and preserves newline escape sequences
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQ...\n-----END PRIVATE KEY-----\n"
```

> 💡 **Where do I get the Firebase Private Key?**
> In the Firebase Console, go to **Project Settings** ➔ **Service Accounts** ➔ click **Generate New Private Key**. Download the JSON file and copy `project_id`, `client_email`, and `private_key` into the variables above.

---

### 2. Frontend Config (`frontend/.env`)
Create a file named `.env` inside the `frontend` folder:

```env
# 1. Backend URL
VITE_API_URL=http://localhost:8000

# 2. Firebase Client SDK (Copy from Step 2 of Web App registration)
VITE_FIREBASE_API_KEY=AIzaSyYourClientApiKey
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
VITE_FIREBASE_APP_ID=1:your_app_id
```

---

## 🏃‍♂️ Quick Start

### 1. Start Backend Server
From the `backend` directory:
```bash
# Initialize Virtual Environment
python -m venv venv
venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Run Tests
python test_phase4_auth_firestore.py

# Launch FastAPI Server
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend Server
From the `frontend` directory:
```bash
# Install Dependencies
npm install

# Run Vite Local Server
npm run dev
```
Open your browser and navigate to `http://localhost:5173`.

---

## 🌟 Hackathon Pitch Highlights
* **Deterministic Verification Badges:** Visual indicators (`🟢 Verified`, `🟡 Needs Verification`, `🔴 Unverified`) give citizens complete trust in the information provided, distinguishing NYAYA from standard wrapper chatbots.
* **Metadata-Driven Actions:** Action steps show exactly *why* they matter and which *authority* has the legal obligation to act, supported by real citations.
* **Seamless onboarding:** Users can immediately draft their document as a guest, and register later to sync their drafts permanently without losing context.
