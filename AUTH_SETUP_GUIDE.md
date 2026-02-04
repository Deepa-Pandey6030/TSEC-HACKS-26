# Simple Auth System - Setup Guide (Hackathon MVP)

## Architecture Overview

```
Frontend (React)
├── Login Page → calls /api/v1/auth/login
├── Signup Page → calls /api/v1/auth/signup
├── Protected Dashboard → checks session, calls /api/v1/auth/check-session
└── AuthContext → manages session state + stores sessionToken in localStorage

Backend (FastAPI)
├── MongoDB (Atlas Cloud)
├── User DB (pymongo)
└── Auth Routes:
    ├── POST /api/v1/auth/signup → create user
    ├── POST /api/v1/auth/login → verify credentials
    ├── POST /api/v1/auth/check-session → check if session valid
    ├── GET /api/v1/auth/me → get current user
    └── POST /api/v1/auth/logout → clear session
```

## Backend Setup

### 1. MongoDB Atlas Connection

Update your `.env` file with:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=your_db_name
```

### 2. Install Dependencies

```bash
cd Backend
pip install -r requirements.txt
```

Note: `pymongo` was added to requirements.txt

### 3. Run Backend

```bash
cd Backend
python main.py
```

Backend will start on `http://localhost:8000`

Test auth endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "password123"}'
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd Frontend
npm install
```

### 2. Run Frontend

```bash
npm run dev
```

Frontend will start on `http://localhost:5173`

### 3. Test Auth Flow

- Go to `/login` or `/signup`
- Create account
- Session token stored in localStorage
- Navigate to `/protected-dashboard`
- User stays logged in on refresh
- Click logout to clear session

## How It Works

### Session Storage (Simple Approach)

**Backend:**
- In-memory dictionary: `active_sessions = {session_token: user_id}`
- On login: creates UUID token, stores in dict
- On logout: deletes token from dict
- On check-session: validates token exists

**Frontend:**
- localStorage stores `sessionToken` after login
- AuthContext checks session on app load
- Passes `sessionToken` to API calls
- On logout: removes `sessionToken` from localStorage

### Database Schema

**MongoDB - users collection:**
```json
{
  "_id": ObjectId,
  "email": "user@example.com",
  "name": "User Name",
  "password": "plaintext_password",
  "created_at": ISODate
}
```

## API Endpoints Reference

### Signup
```
POST /api/v1/auth/signup

Request:
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "message": "Signup successful",
  "user": {
    "id": "user_id",
    "email": "john@example.com",
    "name": "John Doe"
  },
  "token": "session_token_uuid"
}
```

### Login
```
POST /api/v1/auth/login

Request:
{
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "message": "Login successful",
  "user": { ... },
  "token": "session_token_uuid"
}
```

### Check Session
```
POST /api/v1/auth/check-session

Request:
{
  "session_token": "uuid_token"
}

Response:
{
  "valid": true,
  "user": {
    "id": "user_id",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

### Logout
```
POST /api/v1/auth/logout

Request:
{
  "session_token": "uuid_token"
}

Response:
{
  "success": true,
  "message": "Logged out successfully"
}
```

### Get Current User
```
GET /api/v1/auth/me?session_token=uuid_token

Response:
{
  "id": "user_id",
  "email": "john@example.com",
  "name": "John Doe"
}
```

## Frontend Components

### AuthContext (`src/context/AuthContext.jsx`)
- `user` - Current user object
- `isAuthenticated` - Boolean flag
- `loading` - Loading state
- `login(userData, token)` - Set user + token
- `logout()` - Clear user + token
- Auto-checks session on app load

### Auth Service (`src/services/auth.js`)
- `signup(name, email, password)` - Create account
- `login(email, password)` - Login user
- `logout()` - Logout user

### Pages
- `Login.jsx` - Login form
- `Signup.jsx` - Signup form
- `ProtectedDashboard.jsx` - Example protected page (redirects if not logged in)

## Troubleshooting

### "MongoDB Connection Failed"
- Check `.env` file has correct `MONGODB_URL`
- Verify MongoDB Atlas credentials
- Ensure IP is whitelisted in MongoDB Atlas

### "Session Invalid"
- Backend session store clears on server restart (expected for MVP)
- Logout and login again after backend restart

### "CORS Error"
- Backend already has CORS enabled for all origins
- Check frontend is calling `http://localhost:8000`

### "User Already Exists"
- Email must be unique
- Use different email or delete user from MongoDB

## Next Steps (For Hackathon)

1. ✅ Basic auth working
2. Add user profile fields (bio, avatar, etc.)
3. Add protected API routes (check sessionToken)
4. Build more protected pages
5. Add email verification (optional)
6. Add password reset (optional)

## Important Notes

⚠️ **This is MVP for hackathon:**
- No password hashing (plain text)
- Session only lives while server is running
- No database backup
- No rate limiting
- No email verification

For production, add:
- bcrypt for passwords
- JWT or secure cookies
- Database persistence
- Rate limiting
- Email verification
