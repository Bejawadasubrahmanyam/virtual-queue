# VirtualQ – Virtual Queue Management System

A Flask + Supabase web app for managing queues digitally. Users submit applications, receive a unique token, and can track their live queue status.

---

## Stack

- **Backend**: Python / Flask
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Jinja2 templates + Bootstrap 5 + custom CSS

---

## Project Structure

```
project/
├── app.py                  # Flask application & routes
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── schema.sql              # Supabase database schema
└── templates/
    ├── base.html           # Navbar + footer layout
    ├── index.html          # Landing page
    ├── login.html          # Login form
    ├── register.html       # Registration form
    ├── dashboard.html      # User dashboard
    ├── admin.html          # Admin dashboard
    └── queue.html          # Live queue board
```

---

## Quick Setup

### 1. Create a Supabase project
1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Open **SQL Editor** and run the contents of `schema.sql`.
3. Copy your **Project URL** and **anon/public API key** from  
   `Project Settings → API`.

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in SUPABASE_URL, SUPABASE_KEY, SECRET_KEY
```

### 3. Create & activate virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the app
```bash
python app.py
```
Visit `http://localhost:5000`

---

## Features

| Feature | Description |
|---------|-------------|
| User registration & login | Role-based: `user` or `admin` |
| Submit applications | Subject + description form |
| Unique token generation | 6-character alphanumeric token per application |
| User dashboard | View all personal applications with status |
| Admin dashboard | View all applications, update status |
| Live queue board | Public view of Waiting / Processing tokens |
| Flash messages | Success, error, and info feedback |
| Footer | Links, how-it-works, system status |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret key |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public API key |

---

## Security Notes

- **Passwords** are stored in plain text in this demo. In production, use `werkzeug.security.generate_password_hash` / `check_password_hash`.
- Enable **Row Level Security (RLS)** in Supabase for production deployments.
- Move `SECRET_KEY` to a secure secret manager for production.

---

## Database Schema (summary)

```sql
users (id, email, password, role, created_at)
applications (id, user_id, email, subject, description, token, status, created_at)
```

See `schema.sql` for the full DDL.
