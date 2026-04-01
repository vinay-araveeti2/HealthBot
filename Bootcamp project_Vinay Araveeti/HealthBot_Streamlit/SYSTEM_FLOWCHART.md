# HealthBot System Flowchart & Architecture

Complete visual flowcharts showing all system flows and interactions.

---

## 1. HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌────────────────────────────────────────────────────────────────────┐
│                                                                    │
│                         END USER                                  │
│                    (Web Browser/Client)                           │
│                                                                    │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              │ HTTP/HTTPS
                              │
        ┌─────────────────────┴──────────────────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────┐                      ┌──────────────────┐
│     STREAMLIT    │                      │   FLASK API      │
│   (Frontend UI)  │◄────────────────────►│  (API Gateway)   │
│   Port: 8501     │    JSON/HTTP Req     │  Port: 5000      │
└──────────────────┘    JSON Responses    └──────────────────┘
        │                                            │
        │                                            │
        │                    ┌───────────────────────┘
        │                    │
        └────────┬───────────┘
                 │
                 │ (State Management)
                 │
        ┌────────▼──────────┐
        │   LangGraph       │
        │  State Machine    │
        │   (Orchestrator)  │
        └────────┬──────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌──────────┐
│ Tavily  │ │ Cohere  │ │ SQLite   │
│ Search  │ │  LLM    │ │Database  │
│  API    │ │  API    │ │ (Local)  │
└─────────┘ └─────────┘ └──────────┘
```

---

## 2. USER AUTHENTICATION FLOW

```
START
  │
  ▼
┌─────────────────────────────────────┐
│  User Opens HealthBot Application   │
│  (Streamlit runs on :8501)          │
└─────────────┬───────────────────────┘
              │
              ▼
         ┌────────────────┐
         │  Check if user │
         │  is logged in? │
         └────┬───────┬───┘
              │       │
         YES  │       │ NO
              │       │
              ▼       ▼
        ┌──────┐  ┌────────────────────┐
        │Show  │  │ Display Login Form  │
        │Home  │  │                    │
        │Page  │  │ ┌────────────────┐ │
        └──────┘  │ │Email/Username  │ │
              ▲    │ └────────────────┘ │
              │    │ ┌────────────────┐ │
              │    │ │Password        │ │
              │    │ └────────────────┘ │
              │    │ ┌────────────────┐ │
              │    │ │[Login] Button  │ │
              │    │ │[Register] Link │ │
              │    │ └────────────────┘ │
              │    └────────┬───────────┘
              │             │
              │             ▼
              │      ┌──────────────────┐
              │      │ User selects:    │
              │      │ 1. Login         │
              │      │ 2. Register      │
              │      └──────┬───────┬───┘
              │             │       │
              │        ┌────┘       └────┐
              │        │                 │
              │        ▼                 ▼
              │   ┌─────────┐      ┌──────────────┐
              │   │ LOGIN   │      │ REGISTER     │
              │   │ FLOW    │      │ FLOW         │
              │   └────┬────┘      └──────┬───────┘
              │        │                 │
              ▼        │                 │
         ┌────────┐    │                 │
         │ Validate  │  │
         │Credentials│  │
         │in Database│  │
         └────┬────┘    │
              │         │
         ┌────┴────┐    │
         │          │   │
      YES│          │NO │
        │          │   │
        ▼          ▼   ▼
     ┌──────┐  ┌────────────────┐    ┌──────────────┐
     │Set   │  │Show Error      │    │Create User   │
     │Session│  │"Invalid        │    │in Database   │
     │State │  │Credentials"    │    └──────┬───────┘
     └──┬───┘  │               │           │
        │      └──────┬────────┘           │
        │             │                   │
        │             │                   ▼
        │             │          ┌────────────────┐
        │             │          │Set Session     │
        │             │          │State + Login   │
        │             │          └────────┬───────┘
        │             │                   │
        └─────────────┼───────────────────┘
                      │
                      ▼
              ┌─────────────────┐
              │Show Home Page   │
              │- Search Topic   │
              │- View History   │
              │- Admin Controls │
              └─────────────────┘

END
```

---

## 3. TOPIC LEARNING FLOW

```
START (User enters topic)
  │
  ▼
┌─────────────────────────────────────┐
│ User Types Health Topic             │
│ Example: "Diabetes"                 │
│ Clicks: "Learn about this topic"    │
└─────────────┬───────────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Create HealthBotState   │
    │ with topic              │
    └─────────────┬───────────┘
                  │
                  ▼
    ┌─────────────────────────┐
    │ Invoke learn_graph      │
    │ .invoke(state)          │
    └──────────────┬──────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
         ▼                   ▼
    ┌─────────────┐    ┌──────────────┐
    │  NODE 1:    │    │ STATE        │
    │ SEARCH      │───→│ Updated:     │
    │             │    │ - tavily_    │
    │ Action:     │    │   results    │
    │ 1. Format   │    │ - sources    │
    │    query    │    │              │
    │ 2. Call     │    │ Size: 20 KB  │
    │    Tavily   │    │              │
    │ 3. Get 5    │    │              │
    │    results  │    │              │
    │             │    │              │
    │ API Call:   │    │              │
    │ GET         │    │              │
    │ tavily.     │    │              │
    │ search()    │    │              │
    └─────────────┘    └──────────────┘
         │
         ▼
    ┌─────────────────────────┐
    │  NODE 2:                │
    │ SUMMARIZE               │
    │                         │
    │ Action:                 │
    │ 1. Extract search       │
    │    results text         │
    │ 2. Build prompt         │
    │ 3. Call Cohere LLM      │
    │ 4. Generate summary     │
    │ 5. Format with          │
    │    citations            │
    │                         │
    │ API Call:               │
    │ POST Cohere             │
    │ /v2/chat                │
    └──────────┬──────────────┘
               │
               ▼
    ┌──────────────────────┐
    │ STATE Updated:       │
    │ - summary (1.5 KB)   │
    │                      │
    │ Size: 25 KB          │
    └──────────┬───────────┘
               │
               ▼
    ┌─────────────────────────┐
    │  NODE 3:                │
    │ MAKE_QUIZ               │
    │                         │
    │ Action:                 │
    │ 1. Extract summary      │
    │ 2. Build quiz prompt    │
    │ 3. Call Cohere LLM      │
    │ 4. Parse JSON response  │
    │ 5. Extract question     │
    │    & expected answer    │
    │                         │
    │ API Call:               │
    │ POST Cohere             │
    │ /v2/chat                │
    └──────────┬──────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ STATE Updated:           │
    │ - quiz_question (200 B)  │
    │ - quiz_expected_answer   │
    │   (300 B)                │
    │                          │
    │ Size: 26 KB              │
    └──────────┬───────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Return state to         │
    │ Streamlit               │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Display:                │
    │ - Summary               │
    │ - Sources/Citations     │
    │ - [Ready for Quiz] Btn  │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Save topic to database  │
    │ POST /api/save-search   │
    │                         │
    │ → Flask API saves to    │
    │   Search_History table  │
    └──────────┬──────────────┘
               │
               ▼
              END
```

---

## 4. QUIZ & GRADING FLOW

```
START (User ready for quiz)
  │
  ▼
┌─────────────────────────────────────┐
│ Display Quiz Question to User       │
│                                     │
│ Q: {quiz_question}                  │
│                                     │
│ Answer: [Text Input Box]            │
│ [Submit Answer] Button              │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ User Types Answer                   │
│ Clicks: "Submit Answer"             │
└─────────────┬───────────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ Update state with       │
    │ patient_answer          │
    └──────────┬──────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Invoke grade_graph       │
    │ .invoke(state)           │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │  NODE 4:                 │
    │ GRADE_ANSWER             │
    │                          │
    │ Input:                   │
    │ - summary                │
    │ - question               │
    │ - expected_answer        │
    │ - patient_answer ← NEW   │
    │                          │
    │ Action:                  │
    │ 1. Build grading prompt  │
    │ 2. Call Cohere LLM       │
    │ 3. Generate:             │
    │    - grade (A/B/C/D/F)   │
    │    - explanation         │
    │    - citations           │
    │ 4. Parse JSON response   │
    │                          │
    │ API Call:                │
    │ POST Cohere              │
    │ /v2/chat                 │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ STATE Updated:           │
    │ - grade                  │
    │ - grade_explanation      │
    │ - grade_citations        │
    │                          │
    │ Size: 27 KB              │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Return state to          │
    │ Streamlit                │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Display Grade Screen:    │
    │                          │
    │ Grade: A                 │
    │ ✓ Excellent!             │
    │                          │
    │ Explanation:             │
    │ {grade_explanation}      │
    │                          │
    │ Supporting Info:         │
    │ • {citation_1}           │
    │ • {citation_2}           │
    │                          │
    │ [Learn Another Topic]    │
    └──────────┬───────────────┘
               │
               ▼
    ┌──────────────────────────┐
    │ Save result to database  │
    │ POST /api/save-search    │
    │                          │
    │ Payload:                 │
    │ {                        │
    │   email: user@ex.com,    │
    │   topic: "Diabetes",     │
    │   grade: "A"             │
    │ }                        │
    │                          │
    │ → Flask API INSERT into  │
    │   Search_History table   │
    └──────────┬───────────────┘
               │
               ▼
              END
```

---

## 5. COMPLETE END-TO-END FLOW

```
╔════════════════════════════════════════════════════════════════════╗
║                    HEALTHBOT COMPLETE FLOW                        ║
╚════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: APPLICATION START                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Terminal 1: $ python create_database.py                         │
│              (Creates users_database.db if not exists)           │
│                                                                  │
│  Terminal 2: $ python login_api.py                               │
│              (Flask API running on :5000)                        │
│                                                                  │
│  Terminal 3: $ streamlit run app.py                              │
│              (Streamlit UI running on :8501)                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: USER AUTHENTICATION                                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User enters credentials:                                        │
│  Email: user@example.com                                         │
│  Password: password123                                           │
│                                                                  │
│  Streamlit sends:                                                │
│  POST http://localhost:5000/api/login                            │
│  {email: "user@example.com", password: "password123"}            │
│                                                                  │
│  Flask validates against users_database.db (Login table)         │
│  ✓ Credentials match                                             │
│                                                                  │
│  Response: {success: true, user: {...}}                          │
│                                                                  │
│  ✓ User logged in, session state set                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: TOPIC SELECTION & LEARNING                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User enters topic: "Diabetes"                                   │
│  Clicks: "Learn about this topic"                                │
│                                                                  │
│  Streamlit initiates learn_graph.invoke() with:                  │
│  HealthBotState(topic="Diabetes", ...)                           │
│                                                                  │
│  ┌─ LANGGRAPH EXECUTION ──────────────────────────────────────┐ │
│  │                                                            │ │
│  │ NODE 1: node_search                                        │ │
│  │ ├─ Query: "Diabetes site:cdc.gov OR site:who.int ..."    │ │
│  │ ├─ Call: Tavily API search()                              │ │
│  │ └─ Result: 5 web results (~15 KB)                         │ │
│  │                                                            │ │
│  │ NODE 2: node_summarize                                    │ │
│  │ ├─ Input: Search results text                             │ │
│  │ ├─ Prompt: "Write patient-friendly summary..."            │ │
│  │ ├─ Call: Cohere LLM (~1200 input tokens)                  │ │
│  │ └─ Output: Summary with citations (~450 tokens)           │ │
│  │                                                            │ │
│  │ NODE 3: node_make_quiz                                    │ │
│  │ ├─ Input: Summary                                         │ │
│  │ ├─ Prompt: "Create quiz question from summary..."         │ │
│  │ ├─ Call: Cohere LLM (~300 input tokens)                   │ │
│  │ └─ Output: JSON {question, expected_answer}               │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Return: State with summary & quiz (~26 KB total)                │
│                                                                  │
│  Streamlit displays summary to user                              │
│  ✓ Learning session saved to database                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: QUIZ PRESENTATION                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Streamlit displays:                                             │
│                                                                  │
│  ┌────────────────────────────────────────┐                     │
│  │ Quiz Time!                             │                     │
│  │                                        │                     │
│  │ Question:                              │                     │
│  │ "What are the two main types of      │                     │
│  │  diabetes mentioned in the summary?"  │                     │
│  │                                        │                     │
│  │ Your Answer:                           │                     │
│  │ [________________________]              │                     │
│  │                                        │                     │
│  │ [Submit Answer] Button                 │                     │
│  └────────────────────────────────────────┘                     │
│                                                                  │
│  User types answer: "Type 1 and Type 2"                          │
│  Clicks: [Submit Answer]                                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: ANSWER GRADING                                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Streamlit invokes grade_graph.invoke() with:                    │
│  state.patient_answer = "Type 1 and Type 2"                      │
│                                                                  │
│  ┌─ LANGGRAPH EXECUTION ──────────────────────────────────────┐ │
│  │                                                            │ │
│  │ NODE 4: node_grade_answer                                 │ │
│  │ ├─ Input:                                                │ │
│  │ │  ├─ Summary                                             │ │
│  │ │  ├─ Question                                            │ │
│  │ │  ├─ Expected Answer                                     │ │
│  │ │  └─ Patient Answer                                      │ │
│  │ │                                                         │ │
│  │ ├─ Prompt: "Grade this answer based on summary..."        │ │
│  │ ├─ Call: Cohere LLM (~400 input tokens)                   │ │
│  │ └─ Output: JSON {grade, explanation, citations}           │ │
│  │    - grade: "A"                                           │ │
│  │    - explanation: "Excellent! You correctly..."           │ │
│  │    - citations: ["quote1", "quote2"]                      │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Return: State with grade (~27 KB total)                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: RESULTS DISPLAY & PERSISTENCE                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Streamlit displays grade screen:                                │
│                                                                  │
│  ┌────────────────────────────────────────┐                     │
│  │ ✓ Your Grade: A                        │                     │
│  │                                        │                     │
│  │ Excellent work!                        │                     │
│  │                                        │                     │
│  │ Explanation:                           │                     │
│  │ You correctly identified Type 1 and    │                     │
│  │ Type 2 diabetes. Your answer matches   │                     │
│  │ the expected answer perfectly.         │                     │
│  │                                        │                     │
│  │ Supporting Information:                │                     │
│  │ • Type 1 occurs when body cannot      │                     │
│  │   produce insulin                     │                     │
│  │ • Type 2 occurs when body cannot      │                     │
│  │   use insulin effectively             │                     │
│  │                                        │                     │
│  │ [Learn Another Topic]                  │                     │
│  └────────────────────────────────────────┘                     │
│                                                                  │
│  Streamlit saves result via:                                     │
│  POST http://localhost:5000/api/save-search                      │
│  Payload:                                                        │
│  {                                                               │
│    email: "user@example.com",                                    │
│    topic: "Diabetes",                                            │
│    grade: "A"                                                    │
│  }                                                               │
│                                                                  │
│  Flask API inserts into Search_History table:                    │
│  INSERT INTO Search_History                                      │
│  (email_username, search_topic, date, grade)                     │
│  VALUES ('user@example.com', 'Diabetes', now(), 'A')             │
│                                                                  │
│  ✓ Result persisted to database                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: LEARNING HISTORY                                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User clicks: "View Learning History"                            │
│                                                                  │
│  Streamlit requests:                                             │
│  GET http://localhost:5000/api/search-history/user@example.com   │
│                                                                  │
│  Flask API queries Search_History table:                         │
│  SELECT * FROM Search_History                                    │
│  WHERE email_username = 'user@example.com'                       │
│  ORDER BY created_at DESC                                        │
│                                                                  │
│  Response: Array of previous searches                            │
│  [                                                               │
│    {topic: "Diabetes", grade: "A", date: "2024-12-15..."},      │
│    {topic: "Hypertension", grade: "B", date: "2024-12-14..."},  │
│    {topic: "Asthma", grade: "A+", date: "2024-12-13..."}        │
│  ]                                                               │
│                                                                  │
│  Streamlit displays history table                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. DATABASE SCHEMA FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│                     SQLITE DATABASE                             │
│                  (users_database.db)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌──────────────── TABLE: Login ─────────────────┐              │
│ │                                               │              │
│ │  CREATE TABLE Login (                         │              │
│ │    id INTEGER PRIMARY KEY AUTOINCREMENT,      │              │
│ │    email_username TEXT UNIQUE NOT NULL,       │              │
│ │    password TEXT NOT NULL,                    │              │
│ │    name TEXT NOT NULL,                        │              │
│ │    created_at TIMESTAMP DEFAULT now()         │              │
│ │  )                                            │              │
│ │                                               │              │
│ │  Sample Data:                                 │              │
│ │  ┌─────┬──────────────────┬──────────┬──────┐ │              │
│ │  │ id  │ email_username   │ name     │ pass │ │              │
│ │  ├─────┼──────────────────┼──────────┼──────┤ │              │
│ │  │ 1   │ user@example.com │ John Doe │ ●●●● │ │              │
│ │  │ 2   │ admin@health...  │ Admin    │ ●●●● │ │              │
│ │  │ 3   │ doctor@health... │ Dr.Smith │ ●●●● │ │              │
│ │  └─────┴──────────────────┴──────────┴──────┘ │              │
│ │                                               │              │
│ └───────────────────────────────────────────────┘              │
│                         │                                      │
│                         │ FOREIGN KEY                          │
│                         ▼                                      │
│ ┌───── TABLE: Search_History ──────────────────┐              │
│ │                                              │              │
│ │  CREATE TABLE Search_History (               │              │
│ │    id INTEGER PRIMARY KEY AUTOINCREMENT,     │              │
│ │    email_username TEXT NOT NULL,             │              │
│ │    search_topic TEXT NOT NULL,               │              │
│ │    date TEXT NOT NULL,                       │              │
│ │    grade TEXT NOT NULL,                      │              │
│ │    created_at TIMESTAMP DEFAULT now(),       │              │
│ │    FOREIGN KEY(email_username)               │              │
│ │      REFERENCES Login(email_username)        │              │
│ │  )                                           │              │
│ │                                              │              │
│ │  Sample Data:                                │              │
│ │  ┌────┬──────────────────┬──────────┬───┐   │              │
│ │  │ id │ email            │ topic    │gr │   │              │
│ │  ├────┼──────────────────┼──────────┼───┤   │              │
│ │  │ 1  │ user@example.com │ Diabetes │ A │   │              │
│ │  │ 2  │ user@example.com │ Asthma   │ B │   │              │
│ │  │ 3  │ admin@health...  │ Covid-19 │ A │   │              │
│ │  └────┴──────────────────┴──────────┴───┘   │              │
│ │                                              │              │
│ └──────────────────────────────────────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. API ENDPOINTS FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                    FLASK API (localhost:5000)                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ENDPOINT 1: POST /api/login                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Request:  {email: "user@ex.com", password: "pass"}        │ │
│  │ Process:  Query Login table, verify credentials           │ │
│  │ Response: {success: true, user: {id, email, name}}        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ENDPOINT 2: POST /api/register                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Request:  {email: "new@ex.com", password: "pass",         │ │
│  │            name: "New User"}                              │ │
│  │ Process:  Check if email exists, INSERT into Login table  │ │
│  │ Response: {success: true, user: {id, email, name}}        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ENDPOINT 3: POST /api/save-search                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Request:  {email: "user@ex.com", topic: "Diabetes",       │ │
│  │            grade: "A"}                                    │ │
│  │ Process:  INSERT into Search_History table                │ │
│  │ Response: {success: true, message: "Search saved"}        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ENDPOINT 4: GET /api/search-history/<email>                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Request:  GET /api/search-history/user@ex.com             │ │
│  │ Process:  SELECT * FROM Search_History WHERE email_...    │ │
│  │ Response: {success: true, email: "...", history: []}      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ENDPOINT 5: GET /api/health                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Request:  GET /api/health                                 │ │
│  │ Process:  Return server status                            │ │
│  │ Response: {status: "healthy", timestamp: "..."}           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 8. LANGGRAPH STATE MACHINE FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH STATE MACHINE                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LEARN GRAPH WORKFLOW:                                           │
│  ═══════════════════════                                         │
│                                                                  │
│            ┌─────────────┐                                       │
│            │   START     │                                       │
│            │             │                                       │
│            │ Input State:│                                       │
│            │ - topic     │                                       │
│            └──────┬──────┘                                       │
│                   │                                              │
│                   ▼                                              │
│       ┌─────────────────────────┐                               │
│       │ Node: node_search       │                               │
│       │                         │                               │
│       │ Updates:                │                               │
│       │ ✓ tavily_results        │                               │
│       │ ✓ sources              │                               │
│       └──────────┬──────────────┘                               │
│                  │                                              │
│                  ▼                                              │
│       ┌─────────────────────────┐                               │
│       │ Node: node_summarize    │                               │
│       │                         │                               │
│       │ Updates:                │                               │
│       │ ✓ summary              │                               │
│       └──────────┬──────────────┘                               │
│                  │                                              │
│                  ▼                                              │
│       ┌─────────────────────────┐                               │
│       │ Node: node_make_quiz    │                               │
│       │                         │                               │
│       │ Updates:                │                               │
│       │ ✓ quiz_question        │                               │
│       │ ✓ quiz_expected_answer │                               │
│       └──────────┬──────────────┘                               │
│                  │                                              │
│                  ▼                                              │
│            ┌──────────┐                                         │
│            │   END    │                                         │
│            │          │                                         │
│            │ Return   │                                         │
│            │ Complete │                                         │
│            │ State    │                                         │
│            └──────────┘                                         │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  GRADE GRAPH WORKFLOW:                                           │
│  ═════════════════════                                           │
│                                                                  │
│            ┌─────────────┐                                       │
│            │   START     │                                       │
│            │             │                                       │
│            │ Input State:│                                       │
│            │ - patient_  │                                       │
│            │   answer    │                                       │
│            └──────┬──────┘                                       │
│                   │                                              │
│                   ▼                                              │
│       ┌─────────────────────────┐                               │
│       │ Node: node_grade_answer │                               │
│       │                         │                               │
│       │ Updates:                │                               │
│       │ ✓ grade                │                               │
│       │ ✓ grade_explanation    │                               │
│       │ ✓ grade_citations      │                               │
│       └──────────┬──────────────┘                               │
│                  │                                              │
│                  ▼                                              │
│            ┌──────────┐                                         │
│            │   END    │                                         │
│            │          │                                         │
│            │ Return   │                                         │
│            │ Graded   │                                         │
│            │ State    │                                         │
│            └──────────┘                                         │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  RESET GRAPH WORKFLOW:                                           │
│  ══════════════════════                                          │
│                                                                  │
│            ┌─────────────┐                                       │
│            │   START     │                                       │
│            └──────┬──────┘                                       │
│                   │                                              │
│                   ▼                                              │
│       ┌──────────────────────┐                                  │
│       │ Node: node_reset     │                                  │
│       │                      │                                  │
│       │ Action: Clear all    │                                  │
│       │ fields except topic  │                                  │
│       │                      │                                  │
│       │ Updates:             │                                  │
│       │ ✓ tavily_results = []│                                  │
│       │ ✓ summary = ""       │                                  │
│       │ ✓ quiz_question = "" │                                  │
│       │ ✓ grade = ""         │                                  │
│       └──────────┬───────────┘                                  │
│                  │                                              │
│                  ▼                                              │
│            ┌──────────┐                                         │
│            │   END    │                                         │
│            └──────────┘                                         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 9. DATA FLOW BETWEEN SYSTEMS

```
┌────────────────────────────────────────────────────────────────────┐
│                      SYSTEM INTERACTIONS                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  STREAMLIT ←──→ LANGGRAPH                                          │
│  ├─ Invoke: learn_graph.invoke(state)                             │
│  ├─ Receive: Updated state with results                           │
│  └─ Process: Format and display to user                           │
│                                                                    │
│  LANGGRAPH ←──→ TAVILY API                                         │
│  ├─ Request: POST /search                                         │
│  │  Payload: {query, max_results, search_depth}                   │
│  ├─ Response: {results: [{title, url, content}, ...]}             │
│  └─ Storage: Save in state.tavily_results                         │
│                                                                    │
│  LANGGRAPH ←──→ COHERE LLM API                                     │
│  ├─ Request 1 (Summarize): POST /v2/chat                          │
│  │  Payload: {model, messages, temperature, max_tokens}           │
│  │  Response: {text: "summary...", usage: {input, output tokens}} │
│  ├─ Request 2 (Quiz): POST /v2/chat                               │
│  │  Payload: {model, messages, ...}                               │
│  │  Response: {text: "{\"question\": \"...\", ...}", ...}         │
│  ├─ Request 3 (Grade): POST /v2/chat                              │
│  │  Payload: {model, messages, ...}                               │
│  │  Response: {text: "{\"grade\": \"A\", ...}", ...}              │
│  └─ Storage: Save results in respective state fields              │
│                                                                    │
│  STREAMLIT ←──→ FLASK API                                          │
│  ├─ Authentication:                                               │
│  │  Request:  POST /api/login or /api/register                    │
│  │  Response: {success, user, message}                            │
│  ├─ Save Search:                                                  │
│  │  Request:  POST /api/save-search                               │
│  │  Response: {success, message}                                  │
│  ├─ Get History:                                                  │
│  │  Request:  GET /api/search-history/<email>                     │
│  │  Response: {success, email, history: []}                       │
│  └─ Health Check:                                                 │
│     Request:  GET /api/health                                     │
│     Response: {status}                                            │
│                                                                    │
│  FLASK API ←──→ SQLITE DATABASE                                    │
│  ├─ Query Login:                                                  │
│  │  SELECT * FROM Login WHERE email_username = ?                  │
│  ├─ Insert User:                                                  │
│  │  INSERT INTO Login (email, password, name) VALUES (...)        │
│  ├─ Insert Search:                                                │
│  │  INSERT INTO Search_History (...) VALUES (...)                 │
│  ├─ Query History:                                                │
│  │  SELECT * FROM Search_History WHERE email_username = ?         │
│  └─ Response: Rows converted to JSON                              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 10. ADMIN FLOW

```
START
  │
  ▼
┌─────────────────────────────────┐
│ Admin Logs In                   │
│                                 │
│ Email: admin@healthbot.com      │
│ Password: Admin@123             │
│                                 │
│ Database check:                 │
│ is_admin flag = true            │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ Admin Dashboard Displayed       │
│                                 │
│ Options:                        │
│ [1] View All Users              │
│ [2] View Search History         │
│ [3] Add Health Data             │
│ [4] Generate Reports            │
│ [5] Manage Users                │
└─────────────┬───────────────────┘
              │
    ┌─────────┼─────────┬───────────┐
    │         │         │           │
    ▼         ▼         ▼           ▼
  [1]       [2]       [3]         [4]
   │         │         │           │
   ▼         ▼         ▼           ▼
Query     Query   Add New     Generate
All       All     Health      Report
Users     Search  Topics
          History
   │         │         │           │
   ▼         ▼         ▼           ▼
Display   Display   Store      Display
Users     History   in DB      Analytics
Table     Table

              │
              ▼
         END
```

---

## 11. ERROR HANDLING FLOW

```
┌──────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING FLOWS                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AUTHENTICATION ERROR:                                           │
│  ════════════════════                                            │
│                                                                  │
│    User enters credentials                                       │
│             │                                                    │
│             ▼                                                    │
│    Send to Flask /api/login                                      │
│             │                                                    │
│             ▼                                                    │
│    ┌──────────────────┐                                         │
│    │ Query database   │                                         │
│    │ for credentials  │                                         │
│    └────┬─────────┬───┘                                         │
│         │         │                                             │
│      FOUND      NOT FOUND                                        │
│         │         │                                             │
│         ▼         ▼                                             │
│    ┌─────────┐  ┌──────────────────┐                           │
│    │Verify   │  │Return error:     │                           │
│    │password │  │"Invalid          │                           │
│    └────┬────┘  │credentials"      │                           │
│         │       └────────┬─────────┘                            │
│      MATCH               │                                       │
│         │                │                                       │
│         ├────────────────┤                                       │
│         │                │                                       │
│         ▼                ▼                                       │
│      SUCCESS          FAILURE                                    │
│         │                │                                       │
│         ▼                ▼                                       │
│    Set session    Show error message                             │
│    Login user     Ask to retry                                   │
│         │                                                        │
│         └────────────────┘                                       │
│                │                                                 │
│                ▼                                                 │
│            Continue                                              │
│            or Retry                                              │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  API CALL ERROR:                                                 │
│  ════════════════                                                │
│                                                                  │
│    API Request (Tavily/Cohere)                                   │
│             │                                                    │
│             ▼                                                    │
│    ┌──────────────────┐                                         │
│    │Wait for response │                                         │
│    └────┬──────────┬───┘                                         │
│         │          │                                             │
│      SUCCESS    TIMEOUT/ERROR                                    │
│         │          │                                             │
│         ▼          ▼                                             │
│    ┌─────────┐  ┌──────────────────┐                           │
│    │Process  │  │Log error         │                           │
│    │response │  │Show user message │                           │
│    └────┬────┘  │"Service unavail" │                           │
│         │       └────────┬─────────┘                            │
│         │                │                                       │
│         ▼                ▼                                       │
│      Display       Offer retry                                   │
│      Results      or skip                                        │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  DATABASE ERROR:                                                 │
│  ════════════════                                                │
│                                                                  │
│    DB Operation (INSERT/SELECT)                                  │
│             │                                                    │
│             ▼                                                    │
│    ┌──────────────────┐                                         │
│    │Execute query     │                                         │
│    └────┬──────────┬───┘                                         │
│         │          │                                             │
│      SUCCESS    FAILURE                                          │
│         │          │                                             │
│         ▼          ▼                                             │
│    ┌─────────┐  ┌──────────────────┐                           │
│    │Commit   │  │Rollback trans    │                           │
│    │Save data│  │Log error         │                           │
│    │         │  │Show user message │                           │
│    │Return   │  │"DB error"        │                           │
│    │success  │  │                  │                           │
│    └────┬────┘  └────────┬─────────┘                            │
│         │                │                                       │
│         ▼                ▼                                       │
│    Continue          Retry available                             │
│    operations                                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 12. DEPLOYMENT ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────────┐
│                   LOCAL DEVELOPMENT SETUP                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Machine:                                                        │
│  ├─ Localhost (127.0.0.1)                                        │
│  │                                                               │
│  ├─ Terminal 1: python create_database.py                        │
│  │  └─ Creates: users_database.db                                │
│  │             ├─ Login table                                    │
│  │             └─ Search_History table                           │
│  │                                                               │
│  ├─ Terminal 2: python login_api.py                              │
│  │  └─ Runs: Flask API on http://localhost:5000                 │
│  │           ├─ /api/login                                       │
│  │           ├─ /api/register                                    │
│  │           ├─ /api/save-search                                 │
│  │           ├─ /api/search-history/<email>                      │
│  │           └─ /api/health                                      │
│  │                                                               │
│  └─ Terminal 3: streamlit run app.py                             │
│     └─ Runs: Streamlit UI on http://localhost:8501              │
│              ├─ Login page                                       │
│              ├─ Learning page                                    │
│              ├─ Quiz page                                        │
│              └─ Results page                                     │
│                                                                  │
│  External APIs:                                                  │
│  ├─ Tavily Search (requires API key)                             │
│  └─ Cohere LLM (requires API key)                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              PRODUCTION DEPLOYMENT OPTIONS                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Option 1: Single Server with Nginx                              │
│  ═══════════════════════════════════════                          │
│                                                                  │
│  Internet                                                        │
│     │                                                            │
│     ▼                                                            │
│  ┌──────────────────────────────────────┐                       │
│  │  Nginx (Reverse Proxy)               │                       │
│  │  :80  → /api/*  → :5000              │                       │
│  │  :80  → /*      → :8501              │                       │
│  └──────────────────────────────────────┘                       │
│     │              │                                             │
│     ▼              ▼                                             │
│  ┌─────────┐   ┌──────────┐                                     │
│  │Streamlit│   │Flask API │                                     │
│  │:8501    │   │:5000     │                                     │
│  └────┬────┘   └────┬─────┘                                     │
│       │             │                                           │
│       │             ▼                                           │
│       │         ┌────────────┐                                  │
│       │         │PostgreSQL  │                                  │
│       │         │DB (RDS)    │                                  │
│       │         └────────────┘                                  │
│       │                                                         │
│       └─────────────────┘                                       │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  Option 2: Containerized (Docker Compose)                        │
│  ════════════════════════════════════════                        │
│                                                                  │
│  docker-compose.yml:                                             │
│  ├─ frontend service                                             │
│  │  └─ Streamlit image, port 8501                               │
│  ├─ api service                                                  │
│  │  └─ Flask image, port 5000                                   │
│  └─ db service                                                   │
│     └─ PostgreSQL image, port 5432                              │
│                                                                  │
│  ┌─────────────┐  ┌──────────┐  ┌────────┐                    │
│  │ Streamlit   │  │Flask API │  │Postgres│                    │
│  │ Container   │  │Container │  │ DB     │                    │
│  │             │  │          │  │        │                    │
│  │ :8501       │  │ :5000    │  │ :5432  │                    │
│  └──────┬──────┘  └────┬─────┘  └────┬───┘                    │
│         │              │             │                         │
│         └──────────────┼─────────────┘                         │
│                        │                                       │
│                   Docker Network                               │
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                  │
│  Option 3: Cloud Deployment (AWS)                                │
│  ═════════════════════════════════                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐          │
│  │ AWS Architecture                                 │          │
│  │                                                  │          │
│  │ Route 53 (DNS) ──→ healthbot.example.com         │          │
│  │      │                                           │          │
│  │      ▼                                           │          │
│  │ CloudFront (CDN)                                 │          │
│  │      │                                           │          │
│  │      ▼                                           │          │
│  │ ALB (Load Balancer)                              │          │
│  │      │                                           │          │
│  │  ┌───┴───────┐                                   │          │
│  │  │           │                                   │          │
│  │  ▼           ▼                                   │          │
│  │ EC2          EC2                                 │          │
│  │ (Streamlit)  (Flask API)                         │          │
│  │              x2 (auto-scale)                     │          │
│  │                                                  │          │
│  │      ▼                                           │          │
│  │ RDS PostgreSQL                                   │          │
│  │ (Multi-AZ)                                       │          │
│  │                                                  │          │
│  │      ▼                                           │          │
│  │ S3 (Static files, backups)                       │          │
│  │                                                  │          │
│  └──────────────────────────────────────────────────┘          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 13. PERFORMANCE METRICS FLOW

```
┌────────────────────────────────────────────────────────────────┐
│               PERFORMANCE & TIMING DIAGRAM                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  USER ACTION: "Learn about Diabetes"                           │
│  ═══════════════════════════════════════                        │
│                                                                │
│  T=0ms:       User clicks button                               │
│               │                                                │
│               ▼                                                │
│  T=50ms:      Streamlit sends request to LangGraph            │
│               │                                                │
│               ▼                                                │
│  T=100ms:     LangGraph node_search starts                     │
│               │                                                │
│               ▼  (Building query)                              │
│               │                                                │
│  T=200ms:     Request sent to Tavily API                       │
│               │                                                │
│               ↓ (Network latency ~1-2 seconds)                 │
│               │                                                │
│  T=2500ms:    Tavily API response received                     │
│               │                                                │
│               ▼  (Parsing results)                             │
│               │                                                │
│  T=2600ms:    node_summarize starts                            │
│               │ (Building prompt with search results)          │
│               │                                                │
│  T=2800ms:    Request sent to Cohere LLM API                  │
│               │                                                │
│               ↓ (Network latency ~2-3 seconds)                 │
│               │                                                │
│  T=5500ms:    Cohere LLM response received                     │
│               │                                                │
│               ▼  (Parsing response)                            │
│               │                                                │
│  T=5600ms:    node_make_quiz starts                            │
│               │ (Building prompt with summary)                 │
│               │                                                │
│  T=5700ms:    Request sent to Cohere LLM API                  │
│               │                                                │
│               ↓ (Network latency ~1-2 seconds)                 │
│               │                                                │
│  T=7200ms:    Cohere LLM response received                     │
│               │                                                │
│               ▼  (Parsing JSON)                                │
│               │                                                │
│  T=7300ms:    LangGraph returns state to Streamlit            │
│               │                                                │
│               ▼                                                │
│  T=7350ms:    Streamlit displays summary & quiz               │
│               │                                                │
│               ▼                                                │
│  T=7400ms:    User sees results                                │
│                                                                │
│  TOTAL TIME: 7.4 seconds                                       │
│                                                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                │
│  TIME BREAKDOWN:                                               │
│  ═══════════════                                               │
│  - Tavily Search:        2500ms (34%)                          │
│  - Cohere Summary:       2700ms (36%)                          │
│  - Cohere Quiz:          1500ms (20%)                          │
│  - Overhead & Network:   700ms  (9%)                           │
│  ───────────────────────────────                               │
│    TOTAL:                7400ms (100%)                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

Perfect! I've created a comprehensive **SYSTEM_FLOWCHART.md** document with 13 detailed flowchart sections:

1. **High-Level System Architecture** - All components and connections
2. **User Authentication Flow** - Login/Register process
3. **Topic Learning Flow** - Search → Summarize → Quiz generation
4. **Quiz & Grading Flow** - Answer submission and grading
5. **Complete End-to-End Flow** - Full workflow with all 7 steps
6. **Database Schema Flow** - Table structure and relationships
7. **API Endpoints Flow** - All 5 REST endpoints
8. **LangGraph State Machine Flow** - Workflow nodes and state updates
9. **Data Flow Between Systems** - System interactions
10. **Admin Flow** - Admin dashboard operations
11. **Error Handling Flow** - Error scenarios and recovery
12. **Deployment Architecture** - Local, production, and cloud options
13. **Performance Metrics Flow** - Timing breakdown of operations

You now have visual flowcharts for every aspect of your HealthBot system for the interview!