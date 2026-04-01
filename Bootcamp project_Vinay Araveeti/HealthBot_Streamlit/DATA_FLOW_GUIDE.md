# HealthBot: Data Flow from UI to LLM and Back

Complete technical guide showing how data moves through the system at each stage.

---

## Overview: The Complete Journey

```
USER INPUT
    ↓
STREAMLIT (Frontend)
    ↓
FLASK API (API Layer)
    ↓
LANGGRAPH NODES (Orchestration)
    ├→ TAVILY (Search)
    ├→ COHERE LLM (Generate)
    └→ SQLITE (Persist)
    ↓
RESPONSE BACK TO STREAMLIT
    ↓
USER OUTPUT (Display)
```

---

## Stage 1: User Input in Streamlit

### 1a. User Enters Topic

**File**: `app.py` (lines ~200-250)

**User Action**:
```
User types: "Diabetes"
User clicks: "Learn about this topic"
```

**Code Flow**:
```python
# app.py
if st.session_state.phase == "topic":
    topic = st.text_input("What health topic would you like to learn about?")

    if st.button("Learn about this topic"):
        st.session_state.topic = topic  # Store in session state
        st.session_state.phase = "summary"
        st.rerun()
```

**Data Structure at This Point**:
```python
st.session_state = {
    "logged_in": True,
    "user_email": "user@example.com",
    "user_name": "John Doe",
    "phase": "summary",
    "topic": "Diabetes",  # ← New data
    "state": None  # LangGraph state (empty initially)
}
```

**Type**: `str` (plain text)

---

### 1b. Preparing LLM State

**File**: `app.py` (lines ~250-280)

**Code Flow**:
```python
# Create LangGraph state from user input
from healthbot_graph import learn_graph, HealthBotState

if st.session_state.phase == "summary" and st.session_state.state is None:
    # Initialize state machine
    st.session_state.state = HealthBotState(
        topic=st.session_state.topic,
        tavily_results=[],
        sources="",
        summary="",
        quiz_question="",
        quiz_expected_answer="",
        patient_answer="",
        grade="",
        grade_explanation="",
        grade_citations=[],
        next_action=""
    )
```

**Data Structure**:
```python
class HealthBotState:
    topic: str = "Diabetes"
    tavily_results: List[Dict] = []
    sources: str = ""
    summary: str = ""
    quiz_question: str = ""
    quiz_expected_answer: str = ""
    patient_answer: str = ""
    grade: str = ""
    grade_explanation: str = ""
    grade_citations: List[str] = []
    next_action: str = ""
```

**Memory Used**: ~1 KB

---

## Stage 2: Invoking LangGraph

### 2a. Trigger the Learn Graph

**File**: `app.py` (lines ~280-310)

**Code Flow**:
```python
# Invoke the LangGraph state machine
from healthbot_graph import learn_graph

if st.session_state.state and st.session_state.phase == "summary":
    try:
        # ← THIS IS WHERE DATA LEAVES THE FRONTEND
        result_state = learn_graph.invoke(
            st.session_state.state,
            {"recursion_limit": 100}
        )
        # ← DATA COMES BACK HERE

        st.session_state.state = result_state
        st.session_state.phase = "quiz"
        st.rerun()

    except Exception as e:
        st.error(f"Error: {str(e)}")
```

**Data Leaving Streamlit**:
```python
# HealthBotState object passed to learn_graph.invoke()
{
    "topic": "Diabetes",
    "tavily_results": [],
    "sources": "",
    "summary": "",
    # ... other empty fields
}
```

**Serialization**: LangGraph internally converts to dict for state management

**Network**: No network call at this point (local execution)

---

## Stage 3: LangGraph Executes Nodes

### 3a. Search Node

**File**: `healthbot_graph.py` → `node_search()` function

**3a.1 Input to node_search**:

```python
def node_search(state: HealthBotState) -> dict:
    """
    Node 1: Search for health information
    Input: HealthBotState with topic
    Output: Updated state with tavily_results and sources
    """

    # RECEIVE DATA FROM PREVIOUS NODE (or initial state)
    topic = state.topic  # "Diabetes" ← from Streamlit
    print(f"[node_search] Searching for: {topic}")

    # ... processing ...
```

**Data Received**:
```python
Input State:
{
    "topic": "Diabetes",
    "tavily_results": [],
    "sources": "",
    # ... rest empty
}
```

**3a.2 Build Tavily Query**:

```python
    # Format search query for trusted medical sources
    query = f"""{topic}
              site:cdc.gov OR site:who.int OR site:nih.gov
              OR site:mayoclinic.org OR site:nhs.uk"""

    # Example formatted query:
    # "Diabetes site:cdc.gov OR site:who.int OR site:nih.gov
    #  OR site:mayoclinic.org OR site:nhs.uk"
```

**3a.3 Call Tavily API**:

```python
    from tavily import TavilyClient

    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    # ← OUTGOING NETWORK REQUEST TO TAVILY
    response = tavily_client.search(
        query=query,
        max_results=5,
        search_depth="advanced"
    )
    # ← INCOMING NETWORK RESPONSE FROM TAVILY
```

**Network Request (Outgoing)**:
```json
{
  "query": "Diabetes site:cdc.gov OR site:who.int ...",
  "max_results": 5,
  "search_depth": "advanced"
}
```

**Network Response (Incoming from Tavily)**:
```json
{
  "results": [
    {
      "title": "Diabetes: Overview - CDC",
      "url": "https://www.cdc.gov/diabetes/",
      "content": "Diabetes is a chronic condition that affects how..."
    },
    {
      "title": "About Diabetes - WHO",
      "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
      "content": "Diabetes is a serious chronic disease that..."
    },
    // ... 3 more results
  ]
}
```

**Response Size**: ~15 KB

**3a.4 Format Results for State**:

```python
    # Store search results
    results = response.get("results", [])

    # Format source citations
    sources = ""
    for idx, result in enumerate(results, 1):
        source_text = f"[SRC{idx}] {result['title']} - {result['url']}\n"
        sources += source_text

    # Build text of all results for LLM context
    results_text = "\n".join([
        f"[SRC{i}]\nTitle: {r['title']}\nContent: {r['content']}"
        for i, r in enumerate(results, 1)
    ])
```

**3a.5 Return Updated State**:

```python
    # SEND DATA TO NEXT NODE (or back to state)
    return {
        "tavily_results": results,           # Raw API response
        "sources": sources,                  # Formatted citations
        # Note: Other fields remain unchanged
    }
```

**Data Returned from node_search**:
```python
Updated State:
{
    "topic": "Diabetes",
    "tavily_results": [
        {
            "title": "Diabetes: Overview - CDC",
            "url": "https://www.cdc.gov/diabetes/",
            "content": "Diabetes is a chronic condition..."
        },
        // ... 4 more results
    ],
    "sources": "[SRC1] Diabetes: Overview - CDC - https://...\n[SRC2] About Diabetes - WHO - https://...",
    "summary": "",  # Still empty
    # ... rest unchanged
}
```

**Data Size**: ~20 KB (Tavily results stored)

---

### 3b. Summarize Node

**File**: `healthbot_graph.py` → `node_summarize()` function

**3b.1 Input to node_summarize**:

```python
def node_summarize(state: HealthBotState) -> dict:
    """
    Node 2: Generate patient-friendly summary using Cohere LLM
    Input: State with tavily_results and sources
    Output: Updated state with summary
    """

    # RECEIVE DATA FROM PREVIOUS NODE
    topic = state.topic  # "Diabetes"
    tavily_results = state.tavily_results  # List of 5 search results
    results_text = "\n".join([
        f"[SRC{i}]\n{r['content']}"
        for i, r in enumerate(tavily_results, 1)
    ])
    # results_text is now ~10 KB of search content
```

**3b.2 Build Prompt for LLM**:

```python
    from prompts import SUMMARY_PROMPT

    # Get prompt template from prompts.py
    prompt = SUMMARY_PROMPT.format(
        topic=topic,  # "Diabetes"
        search_results=results_text  # ~10 KB of search content
    )

    # Example formatted prompt:
    prompt = f"""
    Based on these search results about '{topic}':

    {results_text}

    Write a 3-4 paragraph patient-friendly summary...
    Include key takeaways as bullet points...
    Cite sources as [SRC1], [SRC2], etc...
    """
```

**Prompt Size**: ~12 KB (topic + search results + template)

**3b.3 Call Cohere LLM API**:

```python
    from langchain_cohere import ChatCohere

    llm = ChatCohere(
        model="command-r7b-12-2024",
        temperature=0.2,
        max_tokens=650,
        api_key=os.getenv("COHERE_API_KEY")
    )

    # ← OUTGOING REQUEST TO COHERE API
    response = llm.invoke(prompt)
    # ← INCOMING RESPONSE FROM COHERE API

    summary_text = response.content  # Extract generated text
```

**Network Request (Outgoing to Cohere)**:
```
POST https://api.cohere.com/v2/chat
Headers:
  Authorization: Bearer <COHERE_API_KEY>
  Content-Type: application/json

Body:
{
  "model": "command-r7b-12-2024",
  "messages": [
    {
      "role": "user",
      "content": "Based on these search results about 'Diabetes':\n\n[SRC1]..."
    }
  ],
  "temperature": 0.2,
  "max_tokens": 650
}
```

**Request Size**: ~12 KB

**Network Response (Incoming from Cohere)**:
```json
{
  "id": "uuid",
  "generation_id": "uuid",
  "text": "Diabetes is a chronic metabolic disorder that affects millions globally. The condition occurs when the body either cannot produce enough insulin or cannot use it effectively...\n\nKey Takeaways:\n- Type 1 and Type 2 diabetes differ in cause\n- [SRC1] Regular monitoring is important\n- [SRC2] Lifestyle changes can help manage symptoms",
  "finish_reason": "end_turn",
  "usage": {
    "input_tokens": 1200,
    "output_tokens": 450
  }
}
```

**Response Size**: ~3-5 KB

**Tokens Used**:
- Input: ~1200 tokens (~4.8 KB)
- Output: ~450 tokens (~1.8 KB)
- Total: ~1650 tokens (~6.6 KB equivalent)

**3b.4 Return Updated State**:

```python
    return {
        "summary": summary_text,  # Generated summary (~1.5 KB)
        # tavily_results and sources preserved in state
    }
```

**Data Returned from node_summarize**:
```python
Updated State:
{
    "topic": "Diabetes",
    "tavily_results": [...],  # Still there
    "sources": "[SRC1]...[SRC2]...",
    "summary": "Diabetes is a chronic metabolic disorder...\n\nKey Takeaways:\n- Type 1 and Type 2...",
    "quiz_question": "",  # Still empty
    # ... rest unchanged
}
```

**Cumulative State Size**: ~25 KB

---

### 3c. Make Quiz Node

**File**: `healthbot_graph.py` → `node_make_quiz()` function

**3c.1 Input to node_make_quiz**:

```python
def node_make_quiz(state: HealthBotState) -> dict:
    """
    Node 3: Generate quiz question using Cohere LLM
    Input: State with summary
    Output: Updated state with quiz_question and quiz_expected_answer
    """

    # RECEIVE DATA FROM PREVIOUS NODE
    summary = state.summary  # The generated summary (~1.5 KB)
```

**3c.2 Build Quiz Prompt**:

```python
    from prompts import QUIZ_PROMPT

    prompt = QUIZ_PROMPT.format(
        summary=summary  # ~1.5 KB
    )

    # Example formatted prompt:
    prompt = f"""
    Based on this summary:

    {summary}

    Create a comprehension quiz question that:
    - Can be answered from the summary
    - Tests key concepts
    - Returns JSON with "question" and "expected_answer" fields
    """
```

**Prompt Size**: ~2 KB

**3c.3 Call Cohere LLM API** (again):

```python
    # ← OUTGOING REQUEST TO COHERE API
    response = llm.invoke(prompt)
    # ← INCOMING RESPONSE FROM COHERE API

    quiz_text = response.content

    # Parse JSON response
    import json
    import re

    # Extract JSON from response
    match = re.search(r"\{.*\}", quiz_text, flags=re.DOTALL)
    if match:
        quiz_json = json.loads(match.group(0))
        question = quiz_json.get("question", "")
        expected_answer = quiz_json.get("expected_answer", "")
```

**Network Request (Outgoing to Cohere)**:
```
POST https://api.cohere.com/v2/chat
Body:
{
  "model": "command-r7b-12-2024",
  "messages": [
    {
      "role": "user",
      "content": "Based on this summary:\n\nDiabetes is a chronic metabolic disorder...\n\nCreate a comprehension quiz question..."
    }
  ],
  "max_tokens": 650
}
```

**Request Size**: ~2 KB

**Network Response (Incoming from Cohere)**:
```json
{
  "text": "{\"question\": \"What are the two main types of diabetes mentioned in the summary?\", \"expected_answer\": \"Type 1 and Type 2. Type 1 occurs when the body cannot produce enough insulin, while Type 2 occurs when the body cannot use insulin effectively.\"}",
  "finish_reason": "end_turn",
  "usage": {
    "input_tokens": 300,
    "output_tokens": 150
  }
}
```

**Response Size**: ~500 bytes

**3c.4 Return Updated State**:

```python
    return {
        "quiz_question": question,
        "quiz_expected_answer": expected_answer
    }
```

**Data Returned from node_make_quiz**:
```python
Updated State:
{
    "topic": "Diabetes",
    "tavily_results": [...],
    "sources": "[SRC1]...",
    "summary": "Diabetes is a chronic metabolic disorder...",
    "quiz_question": "What are the two main types of diabetes?",
    "quiz_expected_answer": "Type 1 and Type 2. Type 1 occurs when...",
    "patient_answer": "",  # Still empty - waiting for user
    # ... rest unchanged
}
```

**Cumulative State Size**: ~26 KB

---

## Stage 4: Back to Streamlit (First Display)

**File**: `app.py` (lines ~300-350)

**Code Flow**:
```python
# After learn_graph.invoke() completes
result_state = learn_graph.invoke(st.session_state.state)

# Store returned state
st.session_state.state = result_state

# Now display summary
st.write("## Summary")
st.write(result_state.summary)

# Show sources
st.write("### Sources")
st.write(result_state.sources)

st.write("---")

# When user is ready, show quiz
if st.button("I'm ready for the quiz"):
    st.session_state.phase = "quiz"
    st.rerun()
```

**Data Received Back in Streamlit**:
```python
HealthBotState:
{
    "topic": "Diabetes",
    "tavily_results": [5 search results],
    "sources": "[SRC1] Diabetes: Overview - CDC\n[SRC2] About Diabetes - WHO\n...",
    "summary": "Diabetes is a chronic metabolic disorder...",
    "quiz_question": "What are the two main types of diabetes?",
    "quiz_expected_answer": "Type 1 and Type 2...",
    "patient_answer": "",
    "grade": "",
    "grade_explanation": "",
    "grade_citations": [],
    "next_action": ""
}
```

**Display on Screen**:
```
┌─────────────────────────────────────────┐
│ Welcome, John Doe                       │
├─────────────────────────────────────────┤
│ ## Summary                              │
│                                         │
│ Diabetes is a chronic metabolic        │
│ disorder that affects millions         │
│ globally... [SRC1]                     │
│                                         │
│ Key Takeaways:                         │
│ - Type 1 and Type 2 diabetes differ    │
│ - [SRC1] Regular monitoring is         │
│   important                            │
│ - [SRC2] Lifestyle changes help        │
│                                         │
│ ### Sources                            │
│ [SRC1] Diabetes: Overview - CDC -      │
│        https://www.cdc.gov/diabetes/   │
│ [SRC2] About Diabetes - WHO -          │
│        https://www.who.int/...         │
│                                         │
│ [I'm ready for the quiz] Button        │
└─────────────────────────────────────────┘
```

---

## Stage 5: User Takes Quiz

### 5a. User Enters Answer

**File**: `app.py` (lines ~350-400)

**User Action**:
```
Streamlit displays:
"What are the two main types of diabetes?"

User types: "Type 1 and Type 2"
User clicks: "Submit Answer"
```

**Code Flow**:
```python
if st.session_state.phase == "quiz":
    st.write(f"### {st.session_state.state.quiz_question}")

    patient_answer = st.text_area("Your answer:")

    if st.button("Submit Answer"):
        st.session_state.state.patient_answer = patient_answer  # ← Store answer
        st.session_state.phase = "grade"
        st.rerun()
```

**Data Updated in Session State**:
```python
st.session_state.state.patient_answer = "Type 1 and Type 2"
```

**Data Size**: ~50 bytes

---

### 5b. Invoke Grade Node

**File**: `app.py` (lines ~400-420)

**Code Flow**:
```python
# Invoke grade_graph with updated state
grade_result = grade_graph.invoke(
    st.session_state.state,
    {"recursion_limit": 100}
)

st.session_state.state = grade_result
```

**Data Sent to Grade Graph**:
```python
HealthBotState:
{
    "topic": "Diabetes",
    "summary": "Diabetes is a chronic metabolic disorder...",
    "quiz_question": "What are the two main types of diabetes?",
    "quiz_expected_answer": "Type 1 and Type 2. Type 1 occurs when...",
    "patient_answer": "Type 1 and Type 2",  # ← New data
    "grade": "",  # Empty - about to be filled
    # ... rest unchanged
}
```

---

## Stage 6: Grading Node

**File**: `healthbot_graph.py` → `node_grade_answer()` function

**6a. Input to Grading Node**:

```python
def node_grade_answer(state: HealthBotState) -> dict:
    """
    Node 4: Grade user answer and provide explanation
    Input: State with patient_answer
    Output: Updated state with grade, explanation, citations
    """

    # RECEIVE DATA FROM STREAMLIT
    summary = state.summary
    question = state.quiz_question
    expected_answer = state.quiz_expected_answer
    patient_answer = state.patient_answer

    print(f"Grading: {patient_answer} against {expected_answer}")
```

**6b. Build Grading Prompt**:

```python
    from prompts import GRADE_PROMPT

    prompt = GRADE_PROMPT.format(
        summary=summary,
        question=question,
        expected_answer=expected_answer,
        patient_answer=patient_answer
    )

    # Example formatted prompt:
    prompt = f"""
    Summary: Diabetes is a chronic metabolic disorder...

    Question: What are the two main types of diabetes?

    Expected Answer: Type 1 and Type 2. Type 1 occurs when the body cannot produce enough insulin, while Type 2 occurs when the body cannot use insulin effectively.

    User's Answer: Type 1 and Type 2

    Grade this answer on a scale A-F and provide:
    1. Grade (A/B/C/D/F)
    2. Explanation (3-6 sentences)
    3. Supporting quotes from the summary

    Return as JSON:
    {{
        "grade": "A",
        "explanation": "...",
        "citations": ["quote1", "quote2"]
    }}
    """
```

**Prompt Size**: ~2 KB

**6c. Call Cohere LLM API** (third call):

```python
    # ← OUTGOING REQUEST TO COHERE API
    response = llm.invoke(prompt)
    # ← INCOMING RESPONSE FROM COHERE API

    grade_text = response.content

    # Parse JSON response
    grade_json = json.loads(extract_json_from_response(grade_text))

    grade = grade_json.get("grade", "C")
    explanation = grade_json.get("explanation", "")
    citations = grade_json.get("citations", [])
```

**Network Request (Outgoing to Cohere)**:
```
POST https://api.cohere.com/v2/chat
Body (similar structure):
{
  "model": "command-r7b-12-2024",
  "messages": [{
    "role": "user",
    "content": "Summary: Diabetes is a chronic metabolic disorder...\n\nQuestion: What are the two main types...\n\nUser's Answer: Type 1 and Type 2\n\nGrade this answer..."
  }],
  "max_tokens": 650
}
```

**Request Size**: ~2 KB

**Network Response (Incoming from Cohere)**:
```json
{
  "text": "{\"grade\": \"A\", \"explanation\": \"Excellent! You correctly identified the two main types of diabetes mentioned in the summary. Your answer directly matches the expected answer and demonstrates a clear understanding of the fundamental distinction between Type 1 and Type 2 diabetes. [SRC1] Type 1 occurs when the body cannot produce enough insulin, while [SRC1] Type 2 occurs when the body cannot use insulin effectively.\", \"citations\": [\"Type 1 occurs when the body cannot produce enough insulin\", \"Type 2 occurs when the body cannot use insulin effectively\"]}",
  "finish_reason": "end_turn",
  "usage": {
    "input_tokens": 400,
    "output_tokens": 200
  }
}
```

**Response Size**: ~800 bytes

**6d. Return Updated State**:

```python
    return {
        "grade": grade,                    # "A"
        "grade_explanation": explanation,  # Full explanation
        "grade_citations": citations       # List of quotes
    }
```

**Data Returned from node_grade_answer**:
```python
Updated State:
{
    "topic": "Diabetes",
    "summary": "Diabetes is a chronic metabolic disorder...",
    "quiz_question": "What are the two main types of diabetes?",
    "quiz_expected_answer": "Type 1 and Type 2...",
    "patient_answer": "Type 1 and Type 2",
    "grade": "A",  # ← New data
    "grade_explanation": "Excellent! You correctly identified...",  # ← New data
    "grade_citations": ["Type 1 occurs when...", "Type 2 occurs when..."],  # ← New data
    "next_action": ""
}
```

**Cumulative State Size**: ~27 KB

---

## Stage 7: Back to Streamlit (Final Display)

**File**: `app.py` (lines ~420-480)

**Code Flow**:
```python
# After grade_graph.invoke() completes
grade_result = grade_graph.invoke(st.session_state.state)
st.session_state.state = grade_result

# Now display grade
st.write("## Your Grade")

grade = st.session_state.state.grade
if grade == "A":
    st.success(f"Grade: {grade} - Excellent!")
elif grade == "B":
    st.info(f"Grade: {grade} - Good job!")
# ... etc

st.write("### Explanation")
st.write(st.session_state.state.grade_explanation)

st.write("### Supporting Information")
for citation in st.session_state.state.grade_citations:
    st.write(f"- {citation}")
```

**Display on Screen**:
```
┌─────────────────────────────────────────┐
│ ## Your Grade                           │
│                                         │
│ ✓ Grade: A - Excellent!                │
│                                         │
│ ### Explanation                         │
│ Excellent! You correctly identified    │
│ the two main types of diabetes. Your   │
│ answer directly matches the expected   │
│ answer and demonstrates a clear        │
│ understanding of the fundamental       │
│ distinction between Type 1 and Type 2  │
│ diabetes...                            │
│                                         │
│ ### Supporting Information             │
│ - Type 1 occurs when the body cannot   │
│   produce enough insulin               │
│ - Type 2 occurs when the body cannot   │
│   use insulin effectively              │
│                                         │
│ [Learn Another Topic] Button           │
└─────────────────────────────────────────┘
```

---

## Stage 8: Save to Database

**File**: `app.py` (lines ~480-520)

**Code Flow**:
```python
# After displaying grade, save to database
import requests

save_data = {
    "email": st.session_state.user_email,
    "topic": st.session_state.state.topic,
    "grade": st.session_state.state.grade
}

# ← OUTGOING HTTP REQUEST TO FLASK API
response = requests.post(
    "http://localhost:5000/api/save-search",
    json=save_data,
    headers={"Content-Type": "application/json"}
)
# ← INCOMING HTTP RESPONSE FROM FLASK API

if response.json().get("success"):
    st.success("Learning session saved!")
```

**Network Request (Outgoing to Flask API)**:
```
POST http://localhost:5000/api/save-search
Headers:
  Content-Type: application/json

Body:
{
  "email": "user@example.com",
  "topic": "Diabetes",
  "grade": "A"
}
```

**Request Size**: ~100 bytes

---

## Stage 9: Flask API Saves to Database

**File**: `login_api.py` → `/api/save-search` endpoint

**Code Flow**:
```python
@app.route("/api/save-search", methods=["POST"])
def save_search():
    """Save search history to database"""

    data = request.json
    email = data.get("email")
    topic = data.get("topic")
    grade = data.get("grade")

    # ← WRITE TO SQLITE DATABASE
    try:
        conn = sqlite3.connect("users_database.db")
        cursor = conn.cursor()

        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """INSERT INTO Search_History
               (email_username, search_topic, date, grade)
               VALUES (?, ?, ?, ?)""",
            (email, topic, date_str, grade)
        )

        conn.commit()
        conn.close()

        return {"success": True, "message": "Search saved"}, 200

    except Exception as e:
        return {"success": False, "message": str(e)}, 500
```

**SQL Query Executed**:
```sql
INSERT INTO Search_History
(email_username, search_topic, date, grade)
VALUES ('user@example.com', 'Diabetes', '2024-12-15 14:30:45', 'A');
```

**Data Written to SQLite**:
```
Table: Search_History
Row:
- id: 1
- email_username: "user@example.com"
- search_topic: "Diabetes"
- date: "2024-12-15 14:30:45"
- grade: "A"
- created_at: "2024-12-15 14:30:45"
```

**Database Size**: +~200 bytes

**Network Response (Back to Streamlit)**:
```json
{
  "success": true,
  "message": "Search saved"
}
```

**Response Size**: ~50 bytes

---

## Complete Data Journey Summary

### Data Transformations:

```
1. USER INPUT (Streamlit)
   Type: String ("Diabetes")
   Size: ~10 bytes

   ↓

2. STREAMLIT SESSION STATE
   Type: HealthBotState dataclass
   Size: ~1 KB (empty fields)

   ↓

3. LANGGRAPH NODE: SEARCH
   ├─ Input: HealthBotState (1 KB)
   ├─ Out: Tavily API Request (500 bytes)
   ├─ In: Tavily API Response (15 KB)
   └─ Output: HealthBotState (20 KB, with results)

   ↓

4. LANGGRAPH NODE: SUMMARIZE
   ├─ Input: HealthBotState (20 KB)
   ├─ Out: Cohere API Request (12 KB)
   ├─ In: Cohere API Response (3-5 KB)
   └─ Output: HealthBotState (25 KB, with summary)

   ↓

5. LANGGRAPH NODE: MAKE QUIZ
   ├─ Input: HealthBotState (25 KB)
   ├─ Out: Cohere API Request (2 KB)
   ├─ In: Cohere API Response (500 bytes)
   └─ Output: HealthBotState (26 KB, with quiz)

   ↓

6. STREAMLIT DISPLAYS SUMMARY & QUIZ
   Type: HTML/Markdown
   Size: Rendered on screen

   ↓

7. USER ENTERS QUIZ ANSWER (Streamlit)
   Type: String ("Type 1 and Type 2")
   Size: ~50 bytes

   ↓

8. LANGGRAPH NODE: GRADE
   ├─ Input: HealthBotState (26 KB)
   ├─ Out: Cohere API Request (2 KB)
   ├─ In: Cohere API Response (800 bytes)
   └─ Output: HealthBotState (27 KB, with grade)

   ↓

9. STREAMLIT DISPLAYS GRADE
   Type: HTML/Markdown
   Size: Rendered on screen

   ↓

10. FLASK API SAVES TO DATABASE
    Type: HTTP POST Request (100 bytes)
    Destination: SQLite users_database.db

    ↓

11. DATABASE STORES RECORD
    Type: SQL INSERT
    Size: ~200 bytes added to DB
```

---

## Network Communication Summary

### API Calls Made:

1. **Tavily Search API** (1 call per topic)
   - Request: ~500 bytes
   - Response: ~15 KB
   - Total: ~15.5 KB
   - Latency: 2-5 seconds

2. **Cohere LLM API** (3 calls per topic)
   - Request 1 (Summarize): ~12 KB
   - Response 1: ~3-5 KB
   - Request 2 (Quiz): ~2 KB
   - Response 2: ~500 bytes
   - Request 3 (Grade): ~2 KB
   - Response 3: ~800 bytes
   - Total: ~20 KB
   - Latency: 3-6 seconds per call (9-18 seconds total)

3. **Flask API** (2 calls)
   - Login: ~100 bytes request
   - Save Search: ~100 bytes request
   - Latency: <100ms each

### Total Network Usage Per Topic Learning:
- **Data Transfer**: ~35.6 KB
- **Time**: ~12-24 seconds
- **API Calls**: 5 total

---

## Memory Usage in Streamlit Session

```
st.session_state memory:

- logged_in: 5 bytes
- user_email: 20 bytes
- user_name: 15 bytes
- is_admin: 1 byte
- phase: 20 bytes
- state (HealthBotState):
  ├─ topic: 10 bytes
  ├─ tavily_results: 15 KB (5 search results)
  ├─ sources: 500 bytes
  ├─ summary: 1.5 KB
  ├─ quiz_question: 200 bytes
  ├─ quiz_expected_answer: 300 bytes
  ├─ patient_answer: 50 bytes
  ├─ grade: 2 bytes
  ├─ grade_explanation: 500 bytes
  └─ grade_citations: 300 bytes

Total per session: ~18-20 KB

For 100 concurrent users: 1.8-2 MB
For 1000 concurrent users: 18-20 MB
```

---

## Error Handling & Data Integrity

### Error Points & Recovery:

1. **Tavily API Fails**
   ```python
   try:
       results = tavily_client.search(query)
   except Exception as e:
       st.error(f"Search failed: {e}")
       return state  # Return with empty tavily_results
   ```
   - Data Lost: None (fallback to empty results)

2. **Cohere LLM Returns Invalid JSON**
   ```python
   def _safe_json_loads(text):
       try:
           return json.loads(text)
       except:
           match = re.search(r"\{.*\}", text, re.DOTALL)
           if match:
               return json.loads(match.group(0))
           raise ValueError("Invalid JSON")
   ```
   - Data Lost: None (extracted from response text)

3. **Database Connection Fails**
   ```python
   try:
       cursor.execute(INSERT_QUERY, data)
       conn.commit()
   except sqlite3.IntegrityError:
       return {"success": False, "message": "User already exists"}
   except Exception as e:
       return {"success": False, "message": str(e)}
   ```
   - Data Lost: None (returned to user for retry)

---

## Data Flow Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  STREAMLIT                                  │
│                                                                             │
│  User Input: "Diabetes" ──→ Session State (1 KB)                           │
│                                    │                                        │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
                                     │ learn_graph.invoke()
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 LANGGRAPH                                   │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    │
│  │  node_search     │───→│ node_summarize   │───→│ node_make_quiz   │    │
│  │  (20 KB)         │    │ (25 KB)          │    │ (26 KB)          │    │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘    │
│        │                         │                        │               │
│  ┌─────▼─────┐           ┌──────▼──────┐          ┌───────▼────────┐    │
│  │   Tavily  │           │   Cohere    │          │    Cohere      │    │
│  │   API     │           │   LLM       │          │    LLM         │    │
│  │  15 KB    │           │   3-5 KB    │          │  500 bytes     │    │
│  └───────────┘           └─────────────┘          └────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Return state (26 KB)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  STREAMLIT                                  │
│                                                                             │
│  Display Summary → Display Quiz Question → User Enters Answer              │
│                                                    │                        │
└────────────────────────────────────────────────────┼────────────────────────┘
                                                     │
                                                     │ grade_graph.invoke()
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 LANGGRAPH                                   │
│                                                                             │
│  ┌──────────────────────────┐                                             │
│  │  node_grade_answer       │ (27 KB)                                     │
│  └────────────┬─────────────┘                                             │
│               │                                                            │
│         ┌─────▼─────┐                                                     │
│         │   Cohere  │                                                     │
│         │   LLM     │                                                     │
│         │ 800 bytes │                                                     │
│         └───────────┘                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Return state (27 KB)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  STREAMLIT                                  │
│                                                                             │
│  Display Grade, Explanation, Citations → Save to Database                  │
│                                                │                            │
└────────────────────────────────────────────────┼────────────────────────────┘
                                                 │
                                    POST /api/save-search
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  FLASK API                                  │
│                                                                             │
│  Receive JSON Request (100 bytes) → Validate → INSERT SQL Query            │
│                                                │                            │
└────────────────────────────────────────────────┼────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  SQLITE DB                                  │
│                                                                             │
│  Search_History Table:                                                     │
│  [id | email | topic | grade | date | created_at]                         │
│  [1  | user@example.com | Diabetes | A | 2024-12-15... | 2024-12-15...]  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways

1. **Data Flows Through Multiple Layers**:
   - Streamlit (UI) → LangGraph (Orchestration) → External APIs (Cohere, Tavily) → Flask API → SQLite

2. **State Object is Central**:
   - HealthBotState carries all data through the workflow
   - Each node reads inputs and writes outputs to the state
   - State is preserved between nodes automatically by LangGraph

3. **External APIs Handle Heavy Lifting**:
   - Tavily returns ranked search results
   - Cohere generates all text content (summaries, quizzes, grades)
   - Both APIs return data in structured formats (JSON)

4. **Network Communication is Optimized**:
   - Requests are minimal (~2-12 KB each)
   - Responses are compact (~500 bytes - 15 KB each)
   - Total per topic: ~35 KB over ~12-24 seconds

5. **Database Persistence is Simple**:
   - Only grade + topic + timestamp stored
   - ~200 bytes per learning session
   - Accessed later for user's learning history

6. **Error Handling Preserves Data**:
   - Failures return partial state
   - User can retry operations
   - Nothing is permanently lost until explicitly deleted

---

Good luck with your interview!
