# HealthBot Technical Architecture & Interview Guide

## System Overview

HealthBot is an AI-powered patient education platform with authentication, search capabilities, quiz generation, and grade tracking. Built using Streamlit (frontend), Flask (API), SQLite (database), Cohere (LLM), and Tavily (search).

---

## Architecture Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                     (Streamlit - app.py)                        │
│                                                                 │
│  Components:                                                    │
│  - Login/Register Forms                                         │
│  - Topic Search Interface                                       │
│  - Summary Display                                              │
│  - Quiz Interface                                               │
│  - Grade Display                                                │
│  - Admin Dashboard (for admin users)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP Requests (POST/GET)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                        API LAYER                                │
│                   (Flask - login_api.py)                        │
│                                                                 │
│  Endpoints:                                                     │
│  - POST /api/login          → User authentication              │
│  - POST /api/register       → New user creation                │
│  - POST /api/save-search    → Save search history              │
│  - GET  /api/search-history → Retrieve user history            │
│  - GET  /api/health         → Health check                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SQL Queries (Read/Write)
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      DATABASE LAYER                             │
│              (SQLite - users_database.db)                       │
│                                                                 │
│  Tables:                                                        │
│  1. Login                                                       │
│     - id (PRIMARY KEY)                                          │
│     - email_username (UNIQUE)                                   │
│     - password                                                  │
│     - name                                                      │
│     - created_at                                                │
│                                                                 │
│  2. Search_History                                              │
│     - id (PRIMARY KEY)                                          │
│     - email_username (FOREIGN KEY)                              │
│     - search_topic                                              │
│     - date                                                      │
│     - grade                                                     │
│     - created_at                                                │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      AI/ML COMPONENTS                           │
│                (healthbot_graph.py + prompts.py)                │
│                                                                 │
│  External Services:                                             │
│  ┌──────────────────────┐    ┌─────────────────────┐          │
│  │   Tavily Search API  │    │   Cohere LLM API    │          │
│  │  (Web Search)        │    │  (Text Generation)  │          │
│  └──────────────────────┘    └─────────────────────┘          │
│           │                            │                        │
│           ▼                            ▼                        │
│  ┌─────────────────────────────────────────────────┐           │
│  │         LangGraph State Machine                 │           │
│  │                                                 │           │
│  │  Nodes:                                         │           │
│  │  1. node_search      → Tavily web search       │           │
│  │  2. node_summarize   → Cohere summary          │           │
│  │  3. node_make_quiz   → Cohere quiz generation  │           │
│  │  4. node_grade_answer→ Cohere grading          │           │
│  │  5. node_reset       → Clear state             │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Roles & Technologies

### 1. Frontend Layer (Streamlit)

**File**: `app.py`

**Technology**: Streamlit 1.55.0

**Role**: User interface and session management

**Key Responsibilities**:
- Render login/register forms
- Display health topic summaries
- Present quiz questions
- Show grades and explanations
- Manage user sessions using `st.session_state`
- Admin dashboard (view users, history, add data)

**Technical Details**:
- Uses custom CSS for modern UI with gradients
- Session state variables: `logged_in`, `user_email`, `user_name`, `is_admin`, `phase`, `state`
- Phase management: `topic` → `summary` → `quiz` → `grade`
- Communicates with Flask API via HTTP requests

---

### 2. API Layer (Flask)

**File**: `login_api.py`

**Technology**: Flask 3.0.0 + Flask-CORS 4.0.0

**Role**: RESTful API for authentication and data management

**Key Responsibilities**:
- Validate user credentials
- Register new users
- Save/retrieve search history
- CORS handling for cross-origin requests

**Endpoints**:

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| POST | `/api/login` | Authenticate user | `{email, password}` | `{success, message, user}` |
| POST | `/api/register` | Create new user | `{email, password, name}` | `{success, message, user}` |
| POST | `/api/save-search` | Save search history | `{email, topic, grade}` | `{success, message}` |
| GET | `/api/search-history/<email>` | Get user history | - | `{success, email, history[]}` |
| GET | `/api/health` | Health check | - | `{status}` |

**Technical Details**:
- Runs on port 5000
- Uses SQLite with `sqlite3` module
- Row factory for dict-like access
- Error handling with try-catch blocks
- Returns JSON responses with status codes

---

### 3. Database Layer (SQLite)

**File**: `users_database.db`

**Technology**: SQLite3 (built-in Python)

**Role**: Persistent data storage

**Schema**:

**Table 1: Login**
```sql
CREATE TABLE Login (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Table 2: Search_History**
```sql
CREATE TABLE Search_History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_username TEXT NOT NULL,
    search_topic TEXT NOT NULL,
    date TEXT NOT NULL,
    grade TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_username) REFERENCES Login(email_username)
)
```

**Technical Details**:
- Lightweight file-based database
- ACID compliant
- Foreign key relationship between tables
- Timestamps for audit trail
- Unique constraint on email

---

### 4. AI/ML Layer (LangGraph + Cohere + Tavily)

**Files**: `healthbot_graph.py`, `prompts.py`

**Technologies**:
- LangGraph 0.2.19 (State machine orchestration)
- Cohere 5.0+ (LLM for text generation)
- Tavily Python 0.4.0 (Web search)
- LangChain 0.2.16 (Framework)

**Role**: AI-powered content generation and grading

#### 4a. LangGraph State Machine

**Purpose**: Orchestrate AI workflow

**State Class**: `HealthBotState` (dataclass)

**State Variables**:
```python
- topic: str                    # User's health topic
- tavily_results: List[Dict]    # Search results
- sources: str                  # Formatted citations
- summary: str                  # Generated summary
- quiz_question: str            # Quiz question
- quiz_expected_answer: str     # Expected answer
- patient_answer: str           # User's answer
- grade: str                    # A/B/C/D/F
- grade_explanation: str        # Grading explanation
- grade_citations: List[str]    # Supporting quotes
- next_action: str              # restart/exit
```

**Graph Structure**:
```
Learn Graph:
  search → summarize → make_quiz → END

Grade Graph:
  grade_answer → END

Reset Graph:
  reset → END
```

#### 4b. Cohere LLM

**Model**: `command-r7b-12-2024`

**Purpose**: Natural language generation

**Configuration**:
- `max_tokens`: 650
- `temperature`: 0.2 (deterministic)

**Use Cases**:
1. Generate patient-friendly summaries
2. Create comprehension quiz questions
3. Grade user answers with explanations

**Adapter Pattern**:
```python
class CohereAdapter:
    def invoke(self, prompt: str):
        # Calls Cohere API
        # Returns SimpleNamespace with .content
```

#### 4c. Tavily Search

**Purpose**: Web search for health information

**Configuration**:
- `k=5` (top 5 results)
- Targeted search: CDC, WHO, NIH, Mayo Clinic, NHS

**Query Format**:
```
"{topic} site:cdc.gov OR site:who.int OR site:nih.gov
  OR site:mayoclinic.org OR site:nhs.uk"
```

**Output**: List of dicts with `title`, `url`, `content`

---

### 5. Prompt Engineering

**File**: `prompts.py`

**Role**: Template prompts for LLM

**Prompts**:

1. **SUMMARY_PROMPT**:
   - Input: Sources list + web results text
   - Output: 3-4 paragraphs + key takeaways (4-6 bullets) + disclaimer
   - Citations: Inline `[SRC1]`, `[SRC2]` format

2. **QUIZ_PROMPT**:
   - Input: Summary
   - Output: JSON with `{question, expected_answer}`
   - Constraint: Must be answerable from summary alone

3. **GRADE_PROMPT**:
   - Input: Summary + question + patient answer
   - Output: JSON with `{grade, explanation, citations}`
   - Grading scale: A/B/C/D/F
   - Explanation: 3-6 patient-friendly sentences

---

## Data Flow Diagrams

### Flow 1: User Authentication

```
User enters email/password
         │
         ▼
Streamlit collects input
         │
         ▼
POST http://localhost:5000/api/login
         │
         ▼
Flask receives request
         │
         ▼
Query SQLite Login table
         │
         ▼
Compare password (plain text)
         │
    ┌────┴────┐
    │         │
  Match?   No Match?
    │         │
    ▼         ▼
Return    Return
{success:  {success:
 true,      false,
 user{}}    message}
    │         │
    └────┬────┘
         ▼
Streamlit receives response
         │
    ┌────┴────┐
    │         │
Success?   Failure?
    │         │
    ▼         ▼
Set       Show
session   error
state     message
    │
    ▼
Show HealthBot interface
```

---

### Flow 2: Health Topic Learning

```
User enters topic (e.g., "Diabetes")
         │
         ▼
Streamlit: phase = "topic"
         │
         ▼
graph.invoke(state) → Learn Graph
         │
         ▼
┌────────────────────────────────┐
│  Node 1: node_search           │
│  - Build Tavily query          │
│  - Call Tavily API             │
│  - Get 5 results               │
│  - Format sources list         │
│  - Store in state              │
└────────┬───────────────────────┘
         ▼
┌────────────────────────────────┐
│  Node 2: node_summarize        │
│  - Concat results text         │
│  - Build SUMMARY_PROMPT        │
│  - Call Cohere LLM             │
│  - Extract summary             │
│  - Store in state              │
└────────┬───────────────────────┘
         ▼
┌────────────────────────────────┐
│  Node 3: node_make_quiz        │
│  - Build QUIZ_PROMPT           │
│  - Call Cohere LLM             │
│  - Parse JSON response         │
│  - Extract question/answer     │
│  - Store in state              │
└────────┬───────────────────────┘
         ▼
Return final state to Streamlit
         │
         ▼
Save topic to Search_History
(via POST /api/save-search)
         │
         ▼
Streamlit: phase = "summary"
         │
         ▼
Display summary to user
```

---

### Flow 3: Quiz & Grading

```
User clicks "I'm ready for quiz"
         │
         ▼
Streamlit: phase = "quiz"
         │
         ▼
Display quiz_question from state
         │
         ▼
User types answer and submits
         │
         ▼
node_grade_answer(state)
         │
         ▼
┌────────────────────────────────┐
│  Node: node_grade_answer       │
│  - Build GRADE_PROMPT          │
│  - Call Cohere LLM             │
│  - Parse JSON response         │
│  - Extract grade (A-F)         │
│  - Extract explanation         │
│  - Extract citations           │
│  - Store in state              │
└────────┬───────────────────────┘
         ▼
Return graded state to Streamlit
         │
         ▼
Update Search_History with grade
(via POST /api/save-search)
         │
         ▼
Streamlit: phase = "grade"
         │
         ▼
Display grade, explanation, citations
```

---

## Key Technical Decisions

### 1. Why SQLite?
- Lightweight (no separate server)
- File-based (easy backup)
- Built into Python
- Sufficient for demo/small-scale deployment

### 2. Why Streamlit?
- Rapid prototyping
- Python-native (no HTML/CSS/JS required)
- Built-in session management
- Real-time updates

### 3. Why Flask API instead of direct database access?
- Separation of concerns
- API can be reused by other clients
- Centralized validation logic
- Better security (credentials not in frontend)

### 4. Why LangGraph?
- State machine pattern for multi-step AI workflows
- Clear node separation (search → summarize → quiz → grade)
- Built-in state management
- Easy to debug and extend

### 5. Why Cohere instead of OpenAI?
- Available model: command-r7b-12-2024
- Cost-effective
- JSON mode support
- Good for educational text generation

### 6. Why Tavily?
- Specialized for AI applications
- Returns clean, structured results
- Supports site-specific queries
- Fast response times

---

## Security Considerations

### Current Implementation:
- Plain text passwords (NOT recommended for production)
- No JWT tokens
- No HTTPS
- No input sanitization beyond basic validation

### Production Recommendations:
1. Hash passwords using `werkzeug.security.generate_password_hash`
2. Implement JWT tokens for session management
3. Use HTTPS (SSL/TLS)
4. Add SQL injection protection (parameterized queries already in use)
5. Implement rate limiting
6. Add CSRF protection
7. Validate email format
8. Add password strength requirements

---

## Performance Optimization

### Current Bottlenecks:
1. **Tavily API calls**: 2-5 seconds per search
2. **Cohere LLM calls**: 3-6 seconds per generation
3. **Sequential node execution**: Total 8-15 seconds per topic

### Optimization Strategies:
1. Cache Tavily results for common topics
2. Use faster Cohere models (if available)
3. Implement async API calls
4. Add loading indicators
5. Preload common topics

---

## Testing Strategy

### Unit Tests:
- Test individual nodes (search, summarize, quiz, grade)
- Test API endpoints (login, register, save-search)
- Test database operations (CRUD)

### Integration Tests:
- Test full workflow (topic → summary → quiz → grade)
- Test authentication flow (login → search → logout)
- Test history tracking

### Example Test Cases:
```python
# Test login
def test_login_success():
    response = requests.post("http://localhost:5000/api/login",
                            json={"email": "admin@healthbot.com",
                                  "password": "Admin@123"})
    assert response.status_code == 200
    assert response.json()["success"] == True

# Test search node
def test_search_node():
    state = HealthBotState(topic="Diabetes")
    result = node_search(state)
    assert len(result.tavily_results) > 0
    assert result.sources is not None
```

---

## Deployment Architecture

### Local Development:
```
Terminal 1: python create_database.py (one-time)
Terminal 2: python login_api.py (keep running)
Terminal 3: streamlit run app.py (keep running)
```

### Production Deployment Options:

**Option 1: Single Server**
```
Nginx (reverse proxy)
   │
   ├─→ Gunicorn (Flask API on port 5000)
   │
   └─→ Streamlit (port 8501)
```

**Option 2: Containerized (Docker)**
```yaml
services:
  api:
    build: ./api
    ports: ["5000:5000"]
    volumes: ["./db:/app/db"]

  frontend:
    build: ./frontend
    ports: ["8501:8501"]
    depends_on: ["api"]
```

**Option 3: Cloud (AWS/Azure/GCP)**
- Frontend: AWS EC2 + Streamlit
- API: AWS Lambda + API Gateway
- Database: AWS RDS (PostgreSQL) instead of SQLite
- LLM: Keep Cohere API
- Search: Keep Tavily API

---

## Environment Variables

**File**: `config.env`

```
COHERE_API_KEY="your-cohere-key"
TAVILY_API_KEY="tvly-..."
```

**Purpose**:
- Secure API key storage
- Environment-specific configuration
- Loaded via `python-dotenv`

---

## Error Handling

### API Level:
```python
try:
    # Database operation
except sqlite3.IntegrityError:
    return {"success": False, "message": "User already exists"}, 409
except Exception as e:
    return {"success": False, "message": f"Server error: {str(e)}"}, 500
```

### LLM Level:
```python
def _safe_json_loads(text: str) -> Dict[str, Any]:
    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        # Extract first JSON object block
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Model did not return JSON")
```

### Frontend Level:
```python
if result.get("success"):
    st.success("Login successful!")
else:
    st.error(f"Login failed: {result.get('message')}")
```

---

## Interview Talking Points

### 1. System Design:
"I designed a 3-tier architecture with clear separation: Streamlit for UI, Flask for API, SQLite for data. This allows independent scaling and testing of each layer."

### 2. AI Integration:
"I used LangGraph to orchestrate a multi-step AI workflow. Each node has a single responsibility: search, summarize, quiz generation, and grading. This makes the system modular and testable."

### 3. Technology Choices:
"I chose Cohere over OpenAI for cost-effectiveness and JSON mode support. Tavily provides structured search results from trusted medical sources like CDC and WHO."

### 4. State Management:
"I used Streamlit's session state for user sessions and LangGraph's state machine for AI workflow. This ensures data consistency across page reloads."

### 5. Security:
"For this demo, I used plain text passwords. In production, I'd implement bcrypt hashing, JWT tokens, HTTPS, and input validation."

### 6. Scalability:
"Current bottleneck is sequential LLM calls (8-15 seconds). I'd optimize with caching, async calls, and faster models. Database can be migrated to PostgreSQL for production."

### 7. Testing:
"I'd implement unit tests for individual nodes, integration tests for full workflows, and end-to-end tests for user journeys."

---

## System Metrics

- **Average Response Time**: 8-15 seconds (topic → summary → quiz)
- **Database Size**: ~50 KB (demo data)
- **API Latency**: <100ms (local network)
- **LLM Token Usage**: ~600 tokens per summary
- **Search Results**: 5 sources per topic
- **Supported Users**: Unlimited (SQLite limit: ~1 TB)

---

## Future Enhancements

1. Password reset via email
2. Two-factor authentication
3. User profile settings
4. Export history as PDF
5. Analytics dashboard
6. Multi-language support
7. Voice input/output
8. Mobile app version
9. Integration with EHR systems
10. Advanced search filters

---

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cannot connect to API" | Flask not running | Start `login_api.py` |
| "User not found" | Invalid credentials | Check database |
| Empty summary | Tavily API error | Check API key |
| JSON parse error | Cohere response format | Use `_safe_json_loads` |
| Port in use | Another process on 5000/8501 | Kill process or change port |

---

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | 1.55.0 | Frontend UI |
| flask | 3.0.0 | API server |
| flask-cors | 4.0.0 | CORS handling |
| cohere | 5.0+ | LLM generation |
| langchain | 0.2.16 | Framework |
| langgraph | 0.2.19 | State machine |
| tavily-python | 0.4.0 | Web search |
| requests | 2.31.0 | HTTP client |
| python-dotenv | 1.0.1 | Env variables |
| sqlite3 | Built-in | Database |

---

## Code Statistics

- **Total Lines**: ~1,500
- **Files**: 8 Python files + 5 markdown docs
- **Functions**: 25+
- **API Endpoints**: 5
- **Database Tables**: 2
- **LangGraph Nodes**: 5
- **Prompts**: 3

---

Good luck with your interview!
