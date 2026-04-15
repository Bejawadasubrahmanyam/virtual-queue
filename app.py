from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from postgrest.exceptions import APIError
import os
import random
import string
from functools import wraps

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# ─── Supabase Config ───────────────────────────────────────────────────────────
# From your provided values:
#   project ref: bjgohrlybpasxekuvjoa
#   anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJqZ29ocmx5YnBhc3hla3V2am9hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxNDE1NTYsImV4cCI6MjA5MDcxNzU1Nn0.qpy9mftYmlkieLwlyjNzcSqXs9spUQVpiDK5wrFV5w8
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://bjgohrlybpasxekuvjoa.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJqZ29ocmx5YnBhc3hla3V2am9hIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxNDE1NTYsImV4cCI6MjA5MDcxNzU1Nn0.qpy9mftYmlkieLwlyjNzcSqXs9spUQVpiDK5wrFV5w8')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ─── Helpers ───────────────────────────────────────────────────────────────────
def generate_token(length=6):
    """Generate a random uppercase alphanumeric token."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_email'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_email'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated


def require_schema(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            supabase.table('users').select('id').limit(1).execute()
            supabase.table('applications').select('id').limit(1).execute()
        except APIError as e:
            err = ''
            if e.args and isinstance(e.args[0], dict):
                err = e.args[0].get('message', str(e))
            else:
                err = str(e)

            if 'Could not find the table' in err or 'PGRST205' in err:
                flash('Supabase tables are missing. Run schema.sql in Supabase SQL Editor and restart app.', 'danger')
                return render_template('index.html')
            raise
        return f(*args, **kwargs)
    return decorated


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
@require_schema
def register():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role     = request.form.get('role', 'user')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('register'))

        # Check if user already exists
        existing = supabase.table('users').select('id').eq('email', email).execute()
        if existing.data:
            flash('An account with that email already exists.', 'warning')
            return redirect(url_for('register'))

        # Insert new user (plain password stored – hash in production!)
        supabase.table('users').insert({
            'email':    email,
            'password': password,
            'role':     role
        }).execute()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@require_schema
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        result = supabase.table('users') \
            .select('*') \
            .eq('email', email) \
            .eq('password', password) \
            .execute()

        if result.data:
            user = result.data[0]
            session['user_email'] = user['email']
            session['user_id']    = user['id']
            session['role']       = user['role']
            flash(f"Welcome back, {user['email']}!", 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
@require_schema
def user_dashboard():
    user_id = session['user_id']

    if request.method == 'POST':
        subject     = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()

        if not subject or not description:
            flash('Subject and description are required.', 'danger')
            return redirect(url_for('user_dashboard'))

        token = generate_token()
        # Ensure uniqueness
        while supabase.table('applications').select('id').eq('token', token).execute().data:
            token = generate_token()

        supabase.table('applications').insert({
            'user_id':     user_id,
            'email':       session['user_email'],
            'subject':     subject,
            'description': description,
            'token':       token,
            'status':      'Waiting'
        }).execute()

        flash(f'Application submitted! Your token is <strong>{token}</strong>.', 'success')
        return redirect(url_for('user_dashboard'))

    apps = supabase.table('applications') \
        .select('*') \
        .eq('user_id', user_id) \
        .order('created_at', desc=True) \
        .execute()

    return render_template('dashboard.html', applications=apps.data)


@app.route('/admin', methods=['GET', 'POST'])
@admin_required
@require_schema
def admin_dashboard():
    if request.method == 'POST':
        doc_id = request.form.get('doc_id')
        status = request.form.get('status')

        if doc_id and status in ('Waiting', 'Processing', 'Completed'):
            supabase.table('applications') \
                .update({'status': status}) \
                .eq('id', doc_id) \
                .execute()
            flash('Status updated successfully.', 'success')
        else:
            flash('Invalid update request.', 'danger')

        return redirect(url_for('admin_dashboard'))

    apps = supabase.table('applications') \
        .select('*') \
        .order('created_at', desc=True) \
        .execute()

    return render_template('admin.html', applications=apps.data)


@app.route('/queue')
@require_schema
def queue_status():
    try:
        apps = supabase.table('applications') \
            .select('*') \
            .in_('status', ['Waiting', 'Processing']) \
            .order('created_at') \
            .execute()
        return render_template('queue.html', applications=apps.data, error=None)
    except Exception as e:
        return render_template('queue.html', applications=[], error=str(e))


# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
