# Frontend ↔️ Backend Auth Connection Guide

## Setup

### 1. Backend - Update MongoDB URL in `.env`

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=nolan_db
```

### 2. Start Backend

```bash
cd Backend
python main.py
```

You should see:
```
✅ API Key 1 loaded: ...
✅ Uvicorn running on http://0.0.0.0:8000
```

### 3. Start Frontend

```bash
cd Frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

## Testing the Connection

### Quick Test in Browser Console

1. Open Frontend: `http://localhost:5173`
2. Open Browser Console (F12)
3. Run test:

```javascript
// Full test flow
authTest.runQuickTest()

// Or individual tests:
authTest.testBackendConnection()
authTest.testSignup('John Doe', 'john@example.com', 'password123')
authTest.testLogin('john@example.com', 'password123')
authTest.testCheckSession()
authTest.testLogout()
```

### Manual Testing

**1. Signup**
- Go to `http://localhost:5173/signup`
- Fill in name, email, password
- Click "Sign Up"
- Should see success message and redirect to home (auto-logged in)

**2. Check Session Persists**
- Refresh the page (F5)
- Should stay logged in (no redirect to login)
- Navigate to `/protected-dashboard`
- Should see user info displayed

**3. Logout**
- Click "Logout" button on protected dashboard
- Should redirect to login page
- Try accessing `/protected-dashboard` again
- Should redirect to login

**4. Login**
- Go to `http://localhost:5173/login`
- Enter email and password
- Click "Login"
- Should redirect to home and be logged in

## What's Connected

### Frontend → Backend API Calls

```
Frontend                          Backend
├── /signup               →  POST /api/v1/auth/signup
├── /login                →  POST /api/v1/auth/login
├── /logout               →  POST /api/v1/auth/logout
└── /check-session        →  POST /api/v1/auth/check-session
```

### Session Flow

1. **User Signs Up**
   ```
   Signup Form → signup() → /api/v1/auth/signup
   ← Returns {user, token}
   → Stores token in localStorage
   → AuthContext updates with user data
   → Auto-login + redirect to home
   ```

2. **Page Refresh**
   ```
   AuthContext mounted → checkAuth()
   → Gets token from localStorage
   → Calls /api/v1/auth/check-session
   ← Returns {valid, user}
   → Sets user state if valid
   ```

3. **Logout**
   ```
   Logout Button → logout()
   → Calls /api/v1/auth/logout
   → Clears token from localStorage
   → Clears user state
   → Redirects to /login
   ```

## Troubleshooting

### "Cannot reach backend" Error

**Problem:** Frontend can't connect to backend

**Solutions:**
1. Check backend is running: `http://localhost:8000/health` should return `{status: "healthy"}`
2. Check CORS is enabled in FastAPI (it is by default)
3. Check firewall isn't blocking port 8000

### "Database connection failed" on Backend

**Problem:** Backend can't connect to MongoDB

**Solutions:**
1. Check `MONGODB_URL` in `.env` is correct
2. Verify credentials (username/password)
3. Check IP is whitelisted in MongoDB Atlas
4. Check `MONGODB_DB_NAME` is set

### "Email already registered" Error

**Problem:** User already exists in database

**Solutions:**
- Use a different email
- Or clear the database in MongoDB Atlas and try again

### Session Lost After Refresh

**Problem:** Not staying logged in after page refresh

**Solutions:**
1. Check browser allows localStorage (check DevTools → Application → LocalStorage)
2. Check `/check-session` endpoint is returning valid response
3. Run `authTest.testCheckSession()` in console to debug

## Files Changed

**Backend:**
- `app/api/auth.py` - All auth endpoints
- `app/db/user_db.py` - MongoDB operations
- `app/models/user.py` - User schemas
- `main.py` - Includes auth router

**Frontend:**
- `src/services/auth.js` - API calls
- `src/context/AuthContext.jsx` - Session state
- `src/pages/Login.jsx` - Login form
- `src/pages/Signup.jsx` - Signup form
- `src/pages/ProtectedDashboard.jsx` - Protected page example
- `src/utils/authDebug.js` - Testing tools

## Next Steps

✅ Signup & Login working  
✅ Session persists across pages  
✅ Protected routes work  
✅ Logout clears session  

Ready for feature building! 🚀
