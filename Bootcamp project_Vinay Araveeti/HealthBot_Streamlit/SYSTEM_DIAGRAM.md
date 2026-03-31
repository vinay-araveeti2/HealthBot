# 🎯 HealthBot Login System - Visual Setup Guide

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│                   (Streamlit App)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Login Page (Email/Password)                       │   │
│  │  • Registration Form                                 │   │
│  │  • Health Bot Interface                              │   │
│  │  • User Session Management                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↕️ HTTP Requests                     │
└─────────────────────────────────────────────────────────────┘
                              ⬇️
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER                               │
│                  (Flask Server)                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • POST /api/login           (User authentication)  │   │
│  │  • POST /api/register        (New user creation)    │   │
│  │  • POST /api/save-search     (History tracking)     │   │
│  │  • GET  /api/search-history  (History retrieval)    │   │
│  └─────────────────────────────────────────────────────┘   │
│                         ↕️ Read/Write                        │
└─────────────────────────────────────────────────────────────┘
                              ⬇️
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                          │
│              (Excel Database - users_database.xlsx)         │
│  ┌──────────────────────┐  ┌──────────────────────────┐    │
│  │   Login Sheet        │  │  Search_History Sheet    │    │
│  │  ─────────────────   │  │  ──────────────────────  │    │
│  │  • Email/Username    │  │  • Email                 │    │
│  │  • Password          │  │  • Search Topic          │    │
│  │  • Name              │  │  • Date/Time             │    │
│  │  • [User Records]    │  │  • Grade                 │    │
│  └──────────────────────┘  │  • [History Records]     │    │
│                            └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### **Login Flow**
```
User Input (Email/Password)
         ↓
Streamlit App (app.py)
         ↓
HTTP POST → http://localhost:5000/api/login
         ↓
Flask API Server (login_api.py)
         ↓
Load Users from Excel (users_database.xlsx)
         ↓
Compare Credentials
    ├─ ✅ Match? → Return Success + User Data
    └─ ❌ No Match? → Return Error Message
         ↓
HTTP Response to Streamlit
         ↓
Update Session State
         ↓
Show HealthBot Interface
```

### **Search & History Flow**
```
User Searches Health Topic
         ↓
Streamlit App
         ↓
1. Get Summary from HealthBot Logic
         ↓
2. Automatically call → POST /api/save-search
         ↓
Flask API adds to Search_History sheet in Excel
         ↓
User Takes Quiz & Gets Grade
         ↓
Call → POST /api/save-search (with grade)
         ↓
Grade is saved in Excel Search_History
         ↓
User can view history in Excel file
```

---

## 🖥️ Terminal Setup

```
Your Computer Screen:
┌────────────────────────────────────┐
│  Terminal 1                        │
│  $ python create_database.py       │
│  ✓ Database created successfully   │
│  [Close when done]                 │
└────────────────────────────────────┘
                    ↓
┌────────────────────────────────────┐        ┌──────────────────┐
│  Terminal 2                        │        │  Excel File      │
│  $ python login_api.py             │←─────→│ users_database   │
│  * Running on                      │        │ .xlsx            │
│  * http://127.0.0.1:5000          │        └──────────────────┘
│  [Keep running]                    │
└────────────────────────────────────┘
                    ↕️ API Calls
┌────────────────────────────────────┐        ┌──────────────────┐
│  Terminal 3 (or Browser)           │        │  Streamlit App   │
│  $ streamlit run app.py            │        │  http://         │
│  * https://localhost:8501          │←─────→│  localhost:8501  │
│  * Browser will open automatically │        └──────────────────┘
│  [Keep running]                    │
└────────────────────────────────────┘
```

---

## 📱 UI Flow

```
┌─────────────────────────────────────────────────┐
│         HealthBot - Initial Load                │
├─────────────────────────────────────────────────┤
│                                                 │
│     🩺 HealthBot                                │
│     Patient Education Assistant                │
│                                                 │
│   ┌─────────┬────────┐                         │
│   │ Login   │Register│                         │
│   └─────────┴────────┘                         │
│                                                 │
│   ┌──────────────────────────────────────┐     │
│   │ Email Address                        │     │
│   │ [___________________________]         │     │
│   │ Password                             │     │
│   │ [___________________________]         │     │
│   │                                      │     │
│   │  [🔓 Login]  [Demo Credentials]      │     │
│   └──────────────────────────────────────┘     │
│                                                 │
└─────────────────────────────────────────────────┘
         ↓ (After Login)
┌─────────────────────────────────────────────────┐
│     HealthBot - Main Interface                  │
├─────────────────────────────────────────────────┤
│           [🚪 Logout]                           │
│  👤 Logged in as: Admin User                    │
│                                                 │
│  🔍 What would you like to learn?              │
│  ┌──────────────────────────────────┐          │
│  │ e.g., diabetes, hypertension... │          │
│  │ [_____________________________]  │          │
│  │  [🔎 Learn]  [🧹 Clear]         │          │
│  └──────────────────────────────────┘          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔑 Key Components

### **1. Streamlit App (app.py)**
- Frontend UI
- User input collection
- Session management
- Communicates with API
- Displays results

### **2. Flask API (login_api.py)**
- Validates credentials
- Creates new users
- Manages search history
- Returns JSON responses
- Handles errors

### **3. Database (users_database.xlsx)**
- Stores user credentials
- Tracks search history
- Easy to view/edit
- Automatic backups possible

### **4. Database Creator (create_database.py)**
- Initializes Excel file
- Creates proper structure
- Adds sample data
- Formats sheets professionally

---

## 📊 Sample Database Tables

### **Table 1: Login Sheet**
```
┌──────────────────────┬──────────────┬──────────────┐
│ Email/Username       │ Password     │ Name         │
├──────────────────────┼──────────────┼──────────────┤
│ admin@healthbot.com  │ Admin@123    │ Admin User   │
│ user1@example.com    │ User@123     │ John Doe     │
│ user2@example.com    │ Pass@456     │ Jane Smith   │
│ test@example.com     │ Test@123     │ Test User    │ ← New registration
└──────────────────────┴──────────────┴──────────────┘
```

### **Table 2: Search_History Sheet**
```
┌──────────────────────┬─────────────────┬─────────────────┬───────┐
│ Email                │ Search Topic    │ Date            │ Grade │
├──────────────────────┼─────────────────┼─────────────────┼───────┤
│ admin@healthbot.com  │ Diabetes        │ 2026-03-23 ... │ A     │
│ admin@healthbot.com  │ Hypertension    │ 2026-03-23 ... │ B     │
│ user1@example.com    │ Anxiety         │ 2026-03-23 ... │ A     │
│ user1@example.com    │ Asthma          │ 2026-03-23 ... │ C     │ ← New search
└──────────────────────┴─────────────────┴─────────────────┴───────┘
```

---

## 🚀 Startup Sequence

```
START
  ↓
[1] User opens 3 terminals
  ↓
[2] Terminal 1: python create_database.py
    • Creates SQLite database
    • Initializes users table
    • Initializes search history table
  ↓
[3] Terminal 2: python login_api.py
    • API Server starts
    • Loads database
    • Listens on http://localhost:5000
    • Ready for requests
  ↓
[4] Terminal 3: streamlit run app.py
    • Streamlit App starts
    • Loads health bot logic
    • Initializes session state
    • Automatically opens browser at http://localhost:8501
  ↓
[5] User sees Web UI - Login Page
    • Can login with credentials
    • Can register new account
    • Can access health bot after login
  ↓
END (User interacts with app)
```

---

## 🔐 Security Layers

```
Layer 1: API Validation
    ├─ Email format check
    ├─ Password length check
    └─ Field requirement check

Layer 2: Database Lookup
    ├─ Check if user exists
    ├─ Verify password match
    └─ Return user info if valid

Layer 3: Session Management
    ├─ Store user email in session
    ├─ Store user name in session
    └─ Maintain logged_in flag

Layer 4: Application Access
    ├─ Check logged_in flag
    ├─ Show login page if not logged in
    └─ Show health bot if logged in
```

---

## 📈 Workflow Timeline

```
⏱️ TIME | ACTION
─────────────────────────────────────────────────────────
00:00   │ Start Applications
        │ • create_database.py
        │ • login_api.py
        │ • streamlit run app.py
        │
00:30   │ User opens browser to http://localhost:8501
        │
01:00   │ User enters credentials
        │ • Email: admin@healthbot.com
        │ • Password: Admin@123
        │
01:30   │ Streamlit sends POST to http://localhost:5000/api/login
        │
02:00   │ Flask API:
        │ • Loads users_database.xlsx
        │ • Finds user
        │ • Validates password
        │ • Returns success
        │
02:30   │ User logged in successfully
        │ • User badge appears
        │ • Health bot interface shows
        │
03:00   │ User searches "Diabetes"
        │ • Automatically calls /api/save-search
        │ • Topic saved to Search_History sheet
        │
04:00   │ User takes quiz and gets grade "A"
        │ • Grade saved to Search_History
        │
05:00   │ User clicks "Logout"
        │ • Session cleared
        │ • Redirected to login page
```

---

## 🎯 Quick Reference

| Task | Command | Location |
|------|---------|----------|
| Create Database | `python create_database.py` | Terminal 1 |
| Start API | `python login_api.py` | Terminal 2 |
| Start App | `streamlit run app.py` | Terminal 3 |
| Open Database | Double-click `users_database.xlsx` | File Explorer |
| Check Logs | View Terminal 2 & 3 | Consoles |
| Reset Database | Delete & re-run `create_database.py` | Terminal 1 |

---

## ✅ Verification Checklist

- [ ] All 3 terminals running without errors
- [ ] Database file exists: `users_database.xlsx`
- [ ] API shows: `Running on http://127.0.0.1:5000`
- [ ] Streamlit opens in browser
- [ ] Login page displays correctly
- [ ] Demo credentials work
- [ ] Can register new account
- [ ] Search history saves to Excel
- [ ] Grades recorded in database
- [ ] Logout works properly

---

**You're all set! 🎉 Your HealthBot login system is ready to use.**

For detailed instructions, see: **QUICK_START.md**
