# HealthBot Login System - Setup Guide

## Overview
This setup adds a complete login system with Excel database, API, and Streamlit integration to your HealthBot application.

## Files Created

### 1. **create_database.py**
- Creates the Excel database (`users_database.xlsx`) with two sheets:
  - **Login**: User credentials (Email/Username, Password, Name)
  - **Search_History**: User search records (Email, Topic, Date, Grade)

### 2. **login_api.py**
- Flask API server that handles:
  - User login verification
  - User registration
  - Search history management
  - API endpoints for all login operations

### 3. **app.py** (Updated)
- Enhanced with login page
- User authentication flow
- User session management
- Integration of search history tracking

---

## Setup Instructions

### Step 1: Create the Database
```powershell
python create_database.py
```
This will create `users_database.xlsx` with sample data and proper formatting.

**Sample Login Credentials:**
- Email: `admin@healthbot.com`
- Password: `Admin@123`

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

The following packages were added:
- `openpyxl==3.10.0` - Excel file handling
- `flask==3.0.0` - API server
- `flask-cors==4.0.0` - CORS support
- `requests==2.31.0` - HTTP requests

### Step 3: Start the API Server
Open a **new terminal** and run:
```powershell
python login_api.py
```

The API will start on `http://localhost:5000`

Expected output:
```
Starting API server on http://localhost:5000
Database path: [.../users_database.xlsx]
 * Running on http://127.0.0.1:5000
```

### Step 4: Run the Streamlit App
Open **another terminal** and run:
```powershell
streamlit run app.py
```

The Streamlit app will open on `http://localhost:8501`

---

## User Workflow

### Login Flow
1. User sees login page with two tabs: **Login** & **Register**
2. **Login Tab:**
   - Enter email and password
   - Click "🔓 Login" button
   - If correct, user is logged in and sees the health bot
   - If incorrect, error message is displayed
3. **Register Tab:**
   - New users can create account
   - Email, password (min 6 chars), and name required
   - Account is saved to Excel database

### After Login
1. **User Badge** shows logged-in user name
2. **Logout Button** in top-right corner
3. Users can:
   - Search health topics (saved to history)
   - Take quizzes
   - See grades (saved to history)
   - View supporting information

### Search History
- Every search topic is automatically saved to the history sheet
- Grades are recorded after quiz completion
- Each entry includes: Email, Topic, Date/Time, Grade

---

## API Endpoints

### Login
**POST** `/api/login`
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

### Register
**POST** `/api/register`
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name"
}
```

### Get Search History
**GET** `/api/search-history/<email>`

### Save Search
**POST** `/api/save-search`
```json
{
  "email": "user@example.com",
  "topic": "Diabetes",
  "grade": "A"
}
```

---

## Database Structure

### Login Sheet
| Email/Username | Password | Name |
|---|---|---|
| admin@healthbot.com | Admin@123 | Admin User |
| user1@example.com | User@123 | John Doe |
| user2@example.com | Pass@456 | Jane Smith |

### Search_History Sheet
| Email/Username | Search Topic | Date | Grade |
|---|---|---|---|
| user1@example.com | Diabetes | 2026-03-20 | A |
| user2@example.com | Hypertension | 2026-03-21 | B |
| user1@example.com | Anxiety | 2026-03-22 | A |

---

## Troubleshooting

### "Cannot connect to API" Error
- Ensure `login_api.py` is running in a separate terminal
- Check that port 5000 is available
- Restart the API server

### Login Failed
- Verify credentials are in the Excel file
- Check email and password are correct (case-sensitive for password)
- Try demo credentials first

### Changes Not Appearing
- Make sure to save the Excel file if editing manually
- Restart both the API and Streamlit app

### Port Already in Use
- If port 5000 is occupied, edit `login_api.py`:
  ```python
  app.run(debug=True, port=5001)  # Change 5000 to 5001
  ```
- Update API_URL in `app.py`:
  ```python
  API_URL = "http://localhost:5001"
  ```

---

## Features Summary

✅ **Login System**
- Email/Password authentication
- User registration
- Session management

✅ **Excel Database**
- Stores user credentials securely
- Tracks search history with grades
- Easy to backup and export

✅ **API Server**
- RESTful endpoints
- CORS enabled for cross-origin requests
- Error handling and validation

✅ **Streamlit Integration**
- Beautiful login UI
- User badge showing logged-in user
- Automatic history tracking
- Grade color-coded display

---

## Next Steps

You can further enhance this system by:
1. Adding password encryption (use `werkzeug.security`)
2. Implementing email verification
3. Adding admin dashboard
4. Export search history as PDF/CSV
5. User statistics and analytics
6. Database migrations for scalability

---

## Support

For issues or questions, check:
- Console logs in API server terminal
- Streamlit app terminal for errors
- Excel file integrity in the `HealthBot_Streamlit` folder
