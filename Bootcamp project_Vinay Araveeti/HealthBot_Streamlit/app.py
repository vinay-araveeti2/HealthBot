import streamlit as st
import requests
from healthbot_graph import init_env, build_graph, HealthBotState, node_grade_answer
import json
import sqlite3
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="HealthBot", 
    page_icon="🩺", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- Custom CSS for Modern UI ----
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 100%);
        padding: 2rem 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2.5rem;
        border-radius: 16px;
        margin: 0 0 2.5rem 0;
        color: white;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
        color: white;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 0.8rem;
        color: rgba(255, 255, 255, 0.95);
        line-height: 1.4;
    }
    
    /* Login header */
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0 0 0.5rem 0;
    }
    
    .login-subtitle {
        font-size: 0.95rem;
        color: #718096;
        font-weight: 500;
        margin: 1.5rem 0;
    }
    
    /* Card styling */
    .card-container {
        background: white;
        border-radius: 14px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    
    .card-container:hover {
        box-shadow: 0 8px 28px rgba(0, 0, 0, 0.10);
        transform: translateY(-1px);
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.7rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: #2d3748;
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }
    
    /* User badge */
    .user-badge {
        background: linear-gradient(135deg, #f0f4f8 0%, #e8eef5 100%);
        border-left: 4px solid #667eea;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: #2d3748;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.85rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        background-color: #f8fafc !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background-color: white !important;
    }
    
    /* Password input */
    .stPassword > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 0.85rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        background-color: #f8fafc !important;
    }
    
    .stPassword > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        background-color: white !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] button {
        background-color: transparent;
        border-bottom: 3px solid #e2e8f0;
        color: #718096;
        font-weight: 600;
        padding: 1rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom-color: #667eea !important;
        color: #667eea !important;
    }
    
    /* Admin panel styling */
    .admin-section {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-left: 5px solid #667eea;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0;
    }
    
    .admin-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    /* Data frame styling */
    .stDataFrame {
        background: white;
        border-radius: 10px;
    }
    
    /* Metric styling */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

init_env()
graph = build_graph()

# ---- Database helper functions ----
DB_PATH = Path(__file__).parent / "users_database.db"

def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users():
    """Get all users from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email_username, password,name, created_at FROM Login ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return [dict(u) for u in users]
    except Exception as e:
        return []

def get_all_search_history():
    """Get all search history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT email_username, search_topic, date, grade FROM Search_History ORDER BY created_at DESC')
        history = cursor.fetchall()
        conn.close()
        return [dict(h) for h in history]
    except Exception as e:
        return []

def add_user_to_db(email, password, name):
    """Add new user to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Login (email_username, password, name)
            VALUES (?, ?, ?)
        ''', (email.lower(), password, name))
        conn.commit()
        conn.close()
        return True, "User added successfully"
    except sqlite3.IntegrityError:
        return False, "User already exists"
    except Exception as e:
        return False, str(e)

def add_search_history_to_db(email, topic, grade=""):
    """Add search history to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO Search_History (email_username, search_topic, date, grade)
            VALUES (?, ?, ?, ?)
        ''', (email.lower(), topic, date, grade))
        conn.commit()
        conn.close()
        return True, "History added successfully"
    except Exception as e:
        return False, str(e)

# ---- Initialize session state ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.is_admin = False

if "state" not in st.session_state:
    st.session_state.state = HealthBotState()
if "phase" not in st.session_state:
    st.session_state.phase = "topic"

# ---- API Configuration ----
API_URL = "http://localhost:5000"

def login_user(email, password):
    """Call login API"""
    try:
        response = requests.post(
            f"{API_URL}/api/login",
            json={"email": email, "password": password},
            timeout=5
        )
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to API. Make sure login_api.py is running on port 5000"
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def register_user(email, password, name):
    """Call register API"""
    try:
        response = requests.post(
            f"{API_URL}/api/register",
            json={"email": email, "password": password, "name": name},
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def save_to_history(email, topic, grade=""):
    """Save search to user history"""
    try:
        requests.post(
            f"{API_URL}/api/save-search",
            json={"email": email, "topic": topic, "grade": grade},
            timeout=5
        )
    except:
        pass

# ---- LOGIN PAGE ----
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-header">
                <h1 class="login-title">🩺 HealthBot</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.05rem; color: #718096; font-weight: 500;">Your AI-Powered Patient Education Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Tab selector
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        # ---- LOGIN TAB ----
        with tab1:
            st.markdown("""
                <p class="login-subtitle">Enter your credentials to access HealthBot</p>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            
            login_email = st.text_input(
                "Email Address",
                placeholder="user@example.com",
                key="login_email"
            )
            
            st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
            
            login_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            if st.button("🔓 Login", use_container_width=True, key="login_btn"):
                if login_email and login_password:
                    with st.spinner("Verifying credentials..."):
                        result = login_user(login_email, login_password)
                    
                    if result.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.user_email = result["user"]["email"]
                        st.session_state.user_name = result["user"]["name"]
                        # Check if admin
                        st.session_state.is_admin = result["user"]["email"].lower() == "admin@healthbot.com"
                        st.success(f"✅ Welcome, {result['user']['name']}!")
                        st.balloons()
                        import time
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {result.get('message', 'Unknown error')}")
                else:
                    st.warning("⚠️ Please enter both email and password")
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            st.info("💡 **New user?** Create an account in the Register tab to get started!")
        
        # ---- REGISTER TAB ----
        with tab2:
            st.markdown("""
                <p class="login-subtitle">Create a new account</p>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            
            reg_name = st.text_input(
                "Full Name",
                placeholder="John Doe",
                key="reg_name"
            )
            
            st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
            
            reg_email = st.text_input(
                "Email Address",
                placeholder="user@example.com",
                key="reg_email"
            )
            
            st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
            
            reg_password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 6 characters",
                key="reg_password"
            )
            
            st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)
            
            reg_password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Repeat your password",
                key="reg_password_confirm"
            )
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            if st.button("📝 Create Account", use_container_width=True, key="register_btn"):
                if not reg_name or not reg_email or not reg_password:
                    st.warning("⚠️ Please fill in all fields")
                elif len(reg_password) < 6:
                    st.warning("⚠️ Password must be at least 6 characters")
                elif reg_password != reg_password_confirm:
                    st.warning("⚠️ Passwords do not match")
                else:
                    with st.spinner("Creating account..."):
                        result = register_user(reg_email, reg_password, reg_name)
                    
                    if result.get("success"):
                        st.success(f"✅ Account created! You can now login.")
                        st.info("Please switch to the Login tab and sign in with your credentials.")
                    else:
                        st.error(f"❌ Registration failed: {result.get('message', 'Unknown error')}")
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            st.info("✨ Your account will be created instantly and you'll be able to start your learning journey right away!")

# ---- MAIN APP (After Login) ----
else:
    # ---- Header with logout ----
    col1, col2, col3 = st.columns([5, 0.5, 1])
    with col3:
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.session_state.user_name = None
            st.session_state.is_admin = False
            st.session_state.phase = "topic"
            st.session_state.state = HealthBotState()
            st.rerun()
    
    # ---- Header ----
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🩺 HealthBot</h1>
            <p class="header-subtitle">Your AI-Powered Patient Education Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Show user info badge
    st.markdown(f"""
        <div class="user-badge">
            👤 Logged in as: <strong>{st.session_state.user_name}</strong>
        </div>
    """, unsafe_allow_html=True)
    
    # ---- ADMIN PANEL ----
    if st.session_state.is_admin:
        st.markdown("""
            <div class="admin-section">
                <div class="admin-title">⚙️ Admin Dashboard</div>
        """, unsafe_allow_html=True)
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(
            ["📊 View Users", "📋 View History", "➕ Add User", "📝 Add History"]
        )
        
        # ---- View Users Tab ----
        with admin_tab1:
            st.subheader("All Users")
            users = get_all_users()
            if users:
                users_data = []
                for user in users:
                    users_data.append({
                        "ID": user.get("id"),
                        "Email": user.get("email_username"),
                        "Name": user.get("name"),
                        "Password": user.get("password"),
                        "Created": user.get("created_at", "N/A")
                    })
                st.dataframe(users_data, use_container_width=True)
                st.info(f"📊 Total Users: {len(users_data)}")
            else:
                st.warning("No users found")
        
        # ---- View History Tab ----
        with admin_tab2:
            st.subheader("Search History")
            history = get_all_search_history()
            if history:
                history_data = []
                for h in history:
                    history_data.append({
                        "Email": h.get("email_username"),
                        "Topic": h.get("search_topic"),
                        "Date": h.get("date"),
                        "Grade": h.get("grade") or "Pending"
                    })
                st.dataframe(history_data, use_container_width=True)
                st.info(f"📋 Total Searches: {len(history_data)}")
            else:
                st.warning("No search history found")
        
        # ---- Add User Tab ----
        with admin_tab3:
            st.subheader("Add New User")
            with st.form("add_user_form"):
                new_email = st.text_input("Email Address", placeholder="user@example.com")
                new_name = st.text_input("Full Name", placeholder="John Doe")
                new_password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                submitted = st.form_submit_button("➕ Add User", use_container_width=True)
                
                if submitted:
                    if not new_email or not new_name or not new_password:
                        st.error("❌ Please fill in all fields")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        success, message = add_user_to_db(new_email, new_password, new_name)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
        
        # ---- Add History Tab ----
        with admin_tab4:
            st.subheader("Add Search History")
            with st.form("add_history_form"):
                hist_email = st.text_input("User Email", placeholder="user@example.com")
                hist_topic = st.text_input("Search Topic", placeholder="e.g., Diabetes")
                hist_grade = st.selectbox("Grade", ["", "A", "B", "C", "D", "F"])
                submitted_hist = st.form_submit_button("📝 Add History", use_container_width=True)
                
                if submitted_hist:
                    if not hist_email or not hist_topic:
                        st.error("❌ Email and topic are required")
                    else:
                        success, message = add_search_history_to_db(hist_email, hist_topic, hist_grade)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ---- Phase: Topic ----
    if st.session_state.phase == "topic":
        st.markdown("""
            <div class="card-container">
                <h2 class="section-header">🔍 What would you like to learn?</h2>
                <p style="color: #4a5568; font-size: 1rem; line-height: 1.6;">Enter a health topic or medical condition to get started with your personalized education journey.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            topic = st.text_input(
                "Health Topic or Medical Condition",
                placeholder="e.g., diabetes, hypertension, anxiety...",
                label_visibility="collapsed"
            )
        
        with col2:
            learn_btn = st.button(
                "🔎 Learn",
                use_container_width=True,
                disabled=not topic.strip(),
                key="learn_btn"
            )
        
        with col3:
            clear_btn = st.button(
                "🧹 Clear",
                use_container_width=True,
                key="clear_btn"
            )

        if learn_btn and topic.strip():
            st.session_state.state.topic = topic.strip()
            with st.spinner("🔄 Searching reputable sources and preparing your summary..."):
                result = graph.invoke(st.session_state.state)
                st.session_state.state = HealthBotState(**result)
            
            # Save to history
            save_to_history(st.session_state.user_email, topic)
            
            st.session_state.phase = "summary"
            st.rerun()

        if clear_btn:
            st.session_state.state = HealthBotState()
            st.session_state.phase = "topic"
            st.rerun()

    # ---- Phase: Summary ----
    elif st.session_state.phase == "summary":
        st.markdown(f"""
            <div class="card-container">
                <h2 class="section-header">📘 Summary: {st.session_state.state.topic}</h2>
                <div style="line-height: 1.8; color: #2d3748; font-size: 0.95rem;">
                    {st.session_state.state.summary or "No summary generated."}
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ I'm ready for a quick quiz", use_container_width=True, key="quiz_btn"):
                st.session_state.phase = "quiz"
                st.rerun()
        
        with col2:
            if st.button("🔄 Learn another topic", use_container_width=True, key="new_topic_btn"):
                st.session_state.state = HealthBotState()
                st.session_state.phase = "topic"
                st.rerun()

    # ---- Phase: Quiz ----
    elif st.session_state.phase == "quiz":
        st.markdown("""
            <div class="card-container">
                <h2 class="section-header">📝 Quick Comprehension Check</h2>
                <p style="color: #4a5568; margin-bottom: 1rem;">Test your understanding with this question based on the summary.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card-container">
                <p style="color: #667eea; font-weight: 600; font-size: 1.1rem;">❓ Question</p>
                <p style="color: #2d3748; font-size: 1rem; line-height: 1.6;">""" + (st.session_state.state.quiz_question or "No quiz question generated.") + """</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        answer = st.text_area(
            "Your Answer",
            height=140,
            placeholder="Type your answer here...",
            label_visibility="collapsed"
        )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📌 Submit Answer", use_container_width=True, disabled=not answer.strip(), key="submit_btn"):
                st.session_state.state.patient_answer = answer.strip()
                with st.spinner("🔄 Grading your answer..."):
                    st.session_state.state = node_grade_answer(st.session_state.state)
                st.session_state.phase = "grade"
                st.rerun()

        with col2:
            if st.button("⬅️ Back to Summary", use_container_width=True, key="back_summary_btn"):
                st.session_state.phase = "summary"
                st.rerun()

    # ---- Phase: Grade ----
    elif st.session_state.phase == "grade":
        # Grade badge styling
        grade = st.session_state.state.grade
        grade_colors = {
            "A": "#48bb78",
            "B": "#38a169",
            "C": "#ecc94b",
            "D": "#f6ad55",
            "F": "#fc8181"
        }
        grade_color = grade_colors.get(grade, "#667eea")
        
        st.markdown(f"""
            <div class="card-container" style="text-align: center;">
                <p style="color: #718096; font-size: 0.9rem; margin-bottom: 0.5rem;">Your Performance</p>
                <div style="font-size: 3.5rem; font-weight: 700; color: {grade_color}; margin: 0.5rem 0;">
                    {grade}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="card-container">
                <p style="color: #667eea; font-weight: 600; font-size: 1.1rem;">💡 Explanation</p>
                <p style="color: #2d3748; line-height: 1.7;">""" + (st.session_state.state.grade_explanation or "") + """</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.state.grade_citations:
            st.markdown("""
                <div class="card-container">
                    <p style="color: #667eea; font-weight: 600; font-size: 1.1rem;">📖 Supporting Information</p>
                </div>
            """, unsafe_allow_html=True)
            
            for i, citation in enumerate(st.session_state.state.grade_citations, 1):
                st.markdown(f"""
                    <div style="background: #f7fafc; border-left: 4px solid #667eea; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; color: #2d3748;">
                        <p style="margin: 0; font-size: 0.9rem;">{citation}</p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        # Save grade to history
        save_to_history(st.session_state.user_email, st.session_state.state.topic, grade)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔁 Learn another topic", use_container_width=True, key="reset_btn"):
                st.session_state.state = HealthBotState()
                st.session_state.phase = "topic"
                st.rerun()

        with col2:
            if st.button("👋 Start New Session", use_container_width=True, key="exit_btn"):
                st.session_state.phase = "topic"
                st.session_state.state = HealthBotState()
                st.info("✨ Session reset. Ready to learn something new?")
                st.rerun()
