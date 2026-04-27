from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models.database import get_db_connection, init_database
from utils.auth import hash_password, verify_password, validate_email, validate_username
import os
import mysql.connector

# Import ML modules
try:
    from ml.mood_predictor import predict_mood, train_model
    from ml.pattern_analyzer import analyze_patterns
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML modules not available yet")

app = Flask(__name__)
app.secret_key = 'student_mood_analyzer_secret_key_2026'

# Initialize database on startup
try:
    init_database()
    print("Database initialized!")
except Exception as e:
    print(f"Database initialization warning: {e}")

# === Helpers ===

def calculate_risk_level(behavior_data):
    if not behavior_data:
        return 'Unknown'
    latest = behavior_data[-1]
    sleep = latest.get('sleep_hours', 0)
    study = latest.get('study_hours', 0)
    social = latest.get('social_hours', 0)

    if sleep < 6 and study > 8 and social < 1:
        return 'High'
    if sleep < 6 or study > 8 or social < 1:
        return 'Medium'
    return 'Low'

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page - landing page or dashboard redirect"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('welcome.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()

    cursor.execute('SELECT COUNT(*) as count FROM mood_entries WHERE user_id = %s', (session['user_id'],))
    mood_count = cursor.fetchone()['count']
    cursor.execute('SELECT COUNT(*) as count FROM behavior_logs WHERE user_id = %s', (session['user_id'],))
    behavior_count = cursor.fetchone()['count']

    cursor.close()
    conn.close()

    return render_template('profile.html', user=user, mood_count=mood_count, behavior_count=behavior_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not validate_username(username):
            flash('Username must be 3-20 characters (alphanumeric and underscore only)!', 'danger')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address!', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return render_template('register.html')
        
        # Hash password
        password_hash = hash_password(password)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, password_hash)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry
                flash('Username or email already exists!', 'danger')
            else:
                flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT id, username, email, password FROM users WHERE username = %s',
            (username,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and verify_password(password, user['password']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash(f'Welcome back, {user["username"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard - shows recent entries and quick stats"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get recent mood entries
    cursor.execute('''
        SELECT mood_level, mood_note, entry_date 
        FROM mood_entries 
        WHERE user_id = %s 
        ORDER BY entry_date DESC 
        LIMIT 7
    ''', (session['user_id'],))
    recent_moods = cursor.fetchall()
    
    # Get recent behavior logs
    cursor.execute('''
        SELECT sleep_hours, study_hours, exercise_minutes, social_hours, log_date 
        FROM behavior_logs 
        WHERE user_id = %s 
        ORDER BY log_date DESC 
        LIMIT 7
    ''', (session['user_id'],))
    recent_behaviors = cursor.fetchall()
    
    # Get counts
    cursor.execute('SELECT COUNT(*) as count FROM mood_entries WHERE user_id = %s', (session['user_id'],))
    mood_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM behavior_logs WHERE user_id = %s', (session['user_id'],))
    behavior_count = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    avg_sleep = round(sum([b['sleep_hours'] for b in recent_behaviors]) / len(recent_behaviors), 1) if recent_behaviors else 0
    avg_study = round(sum([b['study_hours'] for b in recent_behaviors]) / len(recent_behaviors), 1) if recent_behaviors else 0
    avg_social = round(sum([b['social_hours'] for b in recent_behaviors]) / len(recent_behaviors), 1) if recent_behaviors else 0
    risk_level = calculate_risk_level(recent_behaviors)
    greeting_name = session.get('username', 'Student')

    return render_template('index.html', 
                         username=greeting_name,
                         recent_moods=recent_moods,
                         recent_behaviors=recent_behaviors,
                         mood_count=mood_count,
                         behavior_count=behavior_count,
                         avg_sleep=avg_sleep,
                         avg_study=avg_study,
                         avg_social=avg_social,
                         risk_level=risk_level)

@app.route('/mood_entry', methods=['GET', 'POST'])
def mood_entry():
    """Log daily mood"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        mood_level = int(request.form['mood_level'])
        mood_note = request.form.get('mood_note', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'INSERT INTO mood_entries (user_id, mood_level, mood_note, entry_date) VALUES (%s, %s, %s, CURDATE())',
            (session['user_id'], mood_level, mood_note)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Mood entry saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('mood_entry.html')

@app.route('/behavior_log', methods=['GET', 'POST'])
def behavior_log():
    """Log daily behavior activities"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        sleep_hours = float(request.form['sleep_hours'])
        study_hours = float(request.form['study_hours'])
        exercise_minutes = int(request.form['exercise_minutes'])
        social_hours = float(request.form['social_hours'])
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'INSERT INTO behavior_logs (user_id, sleep_hours, study_hours, exercise_minutes, social_hours, log_date) VALUES (%s, %s, %s, %s, %s, CURDATE())',
            (session['user_id'], sleep_hours, study_hours, exercise_minutes, social_hours)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Behavior log saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('behavior_log.html')

@app.route('/analytics')
def analytics():
    """AI-powered analytics and insights"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all mood data for charts
    cursor.execute('''
        SELECT mood_level, mood_note, entry_date 
        FROM mood_entries 
        WHERE user_id = %s 
        ORDER BY entry_date
    ''', (session['user_id'],))
    mood_data = cursor.fetchall()
    
    # Get all behavior data
    cursor.execute('''
        SELECT sleep_hours, study_hours, exercise_minutes, social_hours, log_date 
        FROM behavior_logs 
        WHERE user_id = %s 
        ORDER BY log_date
    ''', (session['user_id'],))
    behavior_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Prepare data for charts
    mood_labels = [m['entry_date'].strftime('%Y-%m-%d') if m['entry_date'] else '' for m in mood_data]
    mood_values = [m['mood_level'] for m in mood_data]
    
    sleep_values = [b['sleep_hours'] for b in behavior_data]
    study_values = [b['study_hours'] for b in behavior_data]
    exercise_values = [b['exercise_minutes'] for b in behavior_data]
    behavior_labels = [b['log_date'].strftime('%Y-%m-%d') if b['log_date'] else '' for b in behavior_data]
    
    # AI Analysis
    prediction = None
    patterns = None
    
    has_data = len(mood_data) > 0 and len(behavior_data) > 0

    if ML_AVAILABLE and len(behavior_data) >= 3:
        try:
            prediction = predict_mood(behavior_data)
        except Exception as e:
            print(f"ML Analysis error: {e}")

    if has_data:
        try:
            patterns = analyze_patterns(mood_data, behavior_data)
        except Exception as e:
            print(f"Pattern analysis error: {e}")

    return render_template('analytics.html',
                         mood_labels=mood_labels,
                         mood_values=mood_values,
                         behavior_labels=behavior_labels,
                         sleep_values=sleep_values,
                         study_values=study_values,
                         exercise_values=exercise_values,
                         prediction=prediction,
                         patterns=patterns,
                         has_data=has_data)

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found!'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, error_message='Access forbidden!'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message='Server error occurred!'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', '5001'))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)