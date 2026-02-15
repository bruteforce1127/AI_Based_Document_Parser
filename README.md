# ClarityVault

**AI-Powered PDF Document Analyzer & Intelligence Platform**

ClarityVault is a sophisticated Flask-based web application that leverages AI to help users understand, analyze, and compare legal and financial documents. Upload a PDF and get instant classification, translation, risk analysis, and conversational Q&A capabilities.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![GPT-4o](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)
![Supabase](https://img.shields.io/badge/Supabase-Database-orange.svg)

---

## Features

| Feature | Description |
|---------|-------------|
| **Smart Classification** | Auto-detect document types (contracts, loans, insurance, etc.) |
| **Multi-Language Translation** | Translate documents to any language |
| **Risk Analysis Dashboard** | Score risky clauses with severity ratings |
| **Benefits Analysis** | Highlight positive aspects and advantages |
| **AI Chat Assistant** | Ask questions about your documents |
| **Term Explanation** | Break down legal jargon into simple language |
| **Market Comparison** | Compare with market alternatives |
| **YouTube Integration** | Find related educational videos |
| **User Authentication** | Secure login with JWT tokens |

---

## System Architecture

### High-Level Architecture

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        Browser["Web Browser"]
        Templates["Jinja2 Templates"]
    end

    subgraph FlaskApp["Flask Application"]
        App["app.py<br/>Main Entry Point"]
        
        subgraph Routes["Route Blueprints"]
            AuthR["auth_routes.py"]
            MainR["routes.py"]
            AnalysisR["analysis_routes.py"]
            ChatR["chat_routes.py"]
            RiskR["risk_routes.py"]
            BenefitsR["benefits_routes.py"]
            CompareR["comparison_routes.py"]
            ConseqR["consequences_routes.py"]
            AuthDocR["auth_doc_routes.py"]
        end
    end

    subgraph Services["Service Layer"]
        PDFSvc["pdf_service.py<br/>PDF Extraction"]
        OpenAISvc["openai_service.py<br/>AI Operations"]
        ChatSvc["chat_service.py<br/>Q&A Engine"]
        RiskSvc["risk_service.py<br/>Risk Scoring"]
        BenefitsSvc["benefits_service.py<br/>Benefits Analysis"]
        CompareSvc["comparison_service.py<br/>Market Analysis"]
        DatabaseSvc["database_service.py<br/>Data Operations"]
        AuthSvc["auth_service.py<br/>Authentication"]
        YTSvc["youtube_service.py<br/>Video Search"]
        KeyMgr["key_manager.py<br/>API Key Rotation"]
    end

    subgraph External["External Services"]
        OpenAI["OpenAI API<br/>GPT-4o"]
        Supabase["Supabase<br/>PostgreSQL Database"]
        YouTube["YouTube Data API"]
    end

    Browser --> Templates
    Templates --> App
    App --> Routes
    Routes --> Services
    
    OpenAISvc --> KeyMgr
    KeyMgr --> OpenAI
    DatabaseSvc --> Supabase
    YTSvc --> YouTube
```

---

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Flask App
    participant P as PDF Service
    participant G as AI Service
    participant D as Supabase

    U->>B: Upload PDF Document
    B->>F: POST /classify
    F->>P: extract_text_from_pdf()
    P-->>F: Extracted Pages
    F->>G: classify_document()
    G-->>F: Document Type
    F->>D: Store Document
    D-->>F: Document ID
    F-->>B: Classification Result
    B-->>U: Show Document Viewer

    Note over U,D: User can now perform various analyses

    U->>B: Request Risk Analysis
    B->>F: GET /risk-analysis/{doc_id}
    F->>D: Fetch Document
    D-->>F: Document Content
    F->>G: analyze_document_risks()
    G-->>F: Risk Scores & Clauses
    F-->>B: Risk Dashboard
    B-->>U: Display Risk Report
```

---

### Data Model

```mermaid
erDiagram
    USERS {
        uuid id PK
        varchar name
        varchar email UK
        varchar password_hash
        timestamp created_at
    }
    
    DOCUMENTS {
        uuid id PK
        uuid user_id FK
        varchar filename
        varchar document_type
        text content
        int pages_count
        timestamp created_at
    }
    
    ANALYSES {
        uuid id PK
        uuid document_id FK
        varchar analysis_type
        jsonb result
        timestamp created_at
        timestamp updated_at
    }

    USERS ||--o{ DOCUMENTS : owns
    DOCUMENTS ||--o{ ANALYSES : has
```

---

### AI Service Integration

```mermaid
flowchart LR
    subgraph Input["Input"]
        PDF["PDF Document"]
    end

    subgraph Processing["Processing"]
        Extract["Text Extraction<br/>PyMuPDF"]
    end

    subgraph AI["AI Analysis (OpenAI)"]
        Classify["Classification"]
        Translate["Translation"]
        Terms["Term Analysis"]
        Risk["Risk Analysis"]
        Benefits["Benefits Analysis"]
        Compare["Market Comparison"]
        Chat["Q&A Chat"]
        Conseq["Consequences"]
    end

    subgraph Output["Output"]
        Dashboard["Interactive<br/>Dashboards"]
    end

    PDF --> Extract
    Extract --> Classify & Translate & Terms & Risk & Benefits & Compare & Chat & Conseq
    Classify & Translate & Terms & Risk & Benefits & Compare & Chat & Conseq --> Dashboard
```

---

## Project Structure

```
ClarityVault/
├── app.py                    # Main Flask application entry
├── config.py                 # Configuration settings
├── routes.py                 # Main document routes
├── auth_routes.py            # Authentication endpoints
├── auth_doc_routes.py        # Protected document routes
├── analysis_routes.py        # Term analysis endpoints
├── chat_routes.py            # AI chat endpoints
├── risk_routes.py            # Risk analysis endpoints
├── benefits_routes.py        # Benefits analysis endpoints
├── comparison_routes.py      # Market comparison endpoints
├── consequences_routes.py    # Consequences analysis endpoints
│
├── services/
│   ├── pdf_service.py        # PDF text extraction
│   ├── openai_service.py     # Core AI operations
│   ├── chat_service.py       # Conversational AI
│   ├── risk_service.py       # Risk scoring engine
│   ├── benefits_service.py   # Benefits analysis
│   ├── comparison_service.py # Market comparison
│   ├── database_service.py   # Supabase operations
│   ├── auth_service.py       # JWT authentication
│   ├── youtube_service.py    # YouTube integration
│   └── key_manager.py        # API key rotation
│
├── templates/
│   ├── index.html            # Landing/upload page
│   ├── login.html            # User login
│   ├── signup.html           # User registration
│   ├── dashboard.html        # User dashboard
│   ├── viewer.html           # Document viewer
│   ├── analysis.html         # Term analysis
│   ├── chat.html             # AI chat interface
│   ├── risk_dashboard.html   # Risk analysis UI
│   ├── benefits_dashboard.html # Benefits UI
│   ├── comparison.html       # Market comparison
│   └── consequences.html     # Consequences view
│
├── uploads/                  # Temporary file storage
├── requirements.txt          # Python dependencies
├── database_schema.sql       # Supabase schema
├── Procfile                  # Deployment config
└── render.yaml               # Render deployment
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API Key
- Supabase Project (URL & Key)
- YouTube Data API Key (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ClarityVault.git
cd ClarityVault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

```env
SECRET_KEY=your-secret-key
OPENAI_API_KEYS=key1,key2,key3
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key
YOUTUBE_API_KEY=your-youtube-key
JWT_SECRET=your-jwt-secret
```

### Database Setup

Run the SQL schema in your Supabase SQL Editor:

```sql
-- See database_schema.sql for full schema
CREATE TABLE users (...);
CREATE TABLE documents (...);
CREATE TABLE analyses (...);
```

### Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/classify` | Upload & classify PDF |
| `GET` | `/document/{id}` | Get document content |
| `POST` | `/translate` | Translate text |
| `POST` | `/chat/{doc_id}/ask` | Ask question |
| `GET` | `/risk-analysis/{id}` | Get risk analysis |
| `GET` | `/benefits/{id}` | Get benefits analysis |
| `GET` | `/comparison/{id}` | Get market comparison |
| `GET` | `/analyze/{id}` | Get term analysis |
| `GET` | `/consequences/{id}` | Get consequences |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 3.0, Python 3.9+ |
| **AI/LLM** | OpenAI GPT-4o |
| **Database** | Supabase (PostgreSQL) |
| **PDF Processing** | PyMuPDF (fitz) |
| **Authentication** | JWT, bcrypt |
| **Frontend** | Jinja2, HTML5, CSS3, JavaScript |
| **Deployment** | Render, Gunicorn |

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- [OpenAI](https://openai.com/) for AI inference
- [Supabase](https://supabase.com/) for database services
- [Flask](https://flask.palletsprojects.com/) for the web framework

---

