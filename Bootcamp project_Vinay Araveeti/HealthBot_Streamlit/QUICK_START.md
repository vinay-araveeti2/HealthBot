# HealthBot - Quick Start Guide

## Quick Setup (2 minutes)

### Manual Setup

**You can use the Terminal in VS Code or your command prompt:**

#### Step 1 - Create Database:
```powershell
python create_database.py
```

#### Step 2 - Start API Server (in a new Terminal):
```powershell
python login_api.py
```
Wait until you see: `Running on http://127.0.0.1:5000`

#### Step 3 - Start Streamlit App (in another new Terminal):
```powershell
streamlit run app.py
```
This will automatically open the app in your browser at `http://localhost:8501`

---

### Alternative: Full Manual Setup



## Testing the System

### Login Test

1. **Open the Streamlit app** (automatically opens, or go to `http://localhost:8501`)

2. **You'll see the login page with two tabs:**
   - 🔐 Login
   - 📝 Register

3. **Try the demo credentials:**
   - Email: `admin@healthbot.com`
   - Password: `Admin@123`
   - Click "🔓 Login"

4. **Expected Result:**
   - ✅ You should see a welcome message
   - ✅ Balloons animation plays
   - ✅ You're redirected to the main app
   - ✅ A user badge shows "Logged in as: Admin User"

---

### Registration Test

1. **In the same login page, click the "📝 Register" tab**

2. **Fill in the form:**
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `Test@123`
   - Confirm Password: `Test@123`
   - Click "📝 Create Account"

3. **Expected Result:**
   - ✅ Success message appears
   - ✅ You can now login with these credentials
   - ✅ Go back to Login tab and try logging in

---

### Full Workflow Test

#### 1. **Login**
   - Use `admin@healthbot.com` / `Admin@123`

#### 2. **Search a Health Topic**
   - Click the input field
   - Type: `Diabetes`
   - Click "🔎 Learn"
   - Expected: Gets summary from API

#### 3. **View Summary**
   - You should see a detailed summary about diabetes
   - Click "✅ I'm ready for a quick quiz"

#### 4. **Take Quiz**
   - A comprehension question appears
   - Type an answer in the text area
   - Click "📌 Submit Answer"
   - Expected: Gets graded (A, B, C, D, or F)

#### 5. **View Results**
   - Grade is displayed with color
   - Explanation of your answer
   - Supporting information/citations

#### 6. **Check Your Options**
   - "🔁 Learn another topic" - Search a new topic
   - "👋 Start New Session" - Reset and go back

#### 7. **Logout**
   - Click "🚪 Logout" button (top-right)
   - You're back at the login page

---

## Verify Database

### Check the Excel File
The database file is located at:
```
c:\Users\lkmuser\Bootcamp project_Vinay Araveeti\HealthBot_Streamlit\users_database.xlsx
```

#### Login Sheet (Tab 1)
Shows all registered users:
- admin@healthbot.com | Admin@123 | Admin User
- user1@example.com | User@123 | John Doe
- (New registrations will appear here)

#### Search_History Sheet (Tab 2)
Shows all user searches and grades:
- admin@healthbot.com | Diabetes | 2026-03-23 12:34:56 | A
- (New searches will appear here)

---

## Testing Scenarios

### ✓ Positive Tests (Should Pass)

| Scenario | Action | Expected |
|---|---|---|
| Valid Login | admin@healthbot.com / Admin@123 | ✅ Login successful |
| Invalid Password | admin@healthbot.com / WrongPassword | ❌ Error message |
| Non-existent Email | fake@mail.com / password | ❌ User not found |
| Valid Registration | New email + password | ✅ Account created |
| Duplicate Email | admin@healthbot.com (register) | ❌ User already exists |
| Short Password | email + 5 chars | ❌ Password too short |
| Empty Fields | Leave fields blank | ❌ Required fields warning |
| Search Topic | Enter "Anxiety" | ✅ Summary generated |
| Quiz Answer | Submit answer | ✅ Graded |
| History Saved | Check Excel file | ✅ Topic appears in history |
| Logout | Click logout | ✅ Back to login page |

---

## Troubleshooting

### Problem: "Cannot connect to API"
**Solution:**
- Check if Terminal 2 (API server) is running
- Look for: `Running on http://127.0.0.1:5000`
- Restart the API server if needed

### Problem: Login says "User not found"
**Solution:**
- Try demo credentials: `admin@healthbot.com` / `Admin@123`
- Make sure database was created: Check if `users_database.xlsx` exists
- Run `python create_database.py` again

### Problem: Page is blank after login
**Solution:**
- Refresh the page (F5)
- Check Streamlit console for errors
- Restart Streamlit app

### Problem: Old password still works after change
**Solution:**
- API is working with the current Excel file
- Database changes take effect immediately
- Close and reopen Streamlit if caching issues

---

## API Testing (Optional)

Test the API endpoints directly using PowerShell or Postman:

### Test Login Endpoint
```powershell
$body = @{
    email = "admin@healthbot.com"
    password = "Admin@123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method POST -Body $body -ContentType "application/json"
```

### Test Health Endpoint
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET
```

### Test Get History
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/search-history/admin@healthbot.com" -Method GET
```

---

## File Structure

```
HealthBot_Streamlit/
├── app.py                  # Main Streamlit app (updated with login)
├── login_api.py           # Flask API server
├── create_database.py     # Database initialization script
├── users_database.xlsx    # Excel database (auto-created)

├── LOGIN_SETUP.md         # Detailed setup guide (this file)
├── requirements.txt       # Python dependencies
├── healthbot_graph.py     # Original health bot logic
├── prompts.py            # Original prompts
└── __pycache__/          # Cache files
```

---

## What's New?

### Files Added:
1. **login_api.py** - Flask API for authentication
2. **create_database.py** - Excel database creator

4. **LOGIN_SETUP.md** - Setup guide
5. **users_database.xlsx** - User database (created automatically)

### Files Modified:
1. **app.py** - Added login system and integration
2. **requirements.txt** - Added new dependencies

### Features Added:
✅ User login/registration system
✅ Excel database for users
✅ Search history tracking
✅ Grade recording
✅ Session management
✅ User authentication
✅ API endpoints

---

## Support & Help

### Check Logs:
- **API Server Console:** Shows login attempts, errors
- **Streamlit Console:** Shows page interactions, errors

### Common Messages:
```
✓ Login successful      → User authenticated
✓ Database created      → users_database.xlsx ready
✓ API running          → http://localhost:5000 active
✓ Search saved         → History recorded
```

---

## Next Use

For future use, simply:
1. Open 3 terminals and run:
   - Terminal 1: `python create_database.py`
   - Terminal 2: `python login_api.py`
   - Terminal 3: `streamlit run app.py`
2. Wait for the app to open
3. Login and use HealthBot

**The database and API will remember all previous users and history!**
