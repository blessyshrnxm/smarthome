from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from database import init_db, get_db, get_user_by_email
from datetime import datetime

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
    MYSQL_HOST=os.getenv('MYSQL_HOST', 'localhost'),
    MYSQL_USER=os.getenv('MYSQL_USER', 'root'),
    MYSQL_PASSWORD=os.getenv('MYSQL_PASSWORD', '123456'),
    MYSQL_DB=os.getenv('MYSQL_DB', 'energy_saver'),
    MYSQL_CURSORCLASS='DictCursor'
)

# Initialize extensions
init_db(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.eco_points = user_data.get('eco_points', 0)

@login_manager.user_loader
def load_user(user_id):
    mysql = get_db()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return User(user) if user else None

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            
            mysql = get_db()
            cur = mysql.connection.cursor()
            
            # Check if email exists
            if get_user_by_email(email):
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Insert new user
            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            mysql.connection.commit()
            cur.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = get_user_by_email(email)
        
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(user)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
            
        flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    mysql = get_db()
    cur = mysql.connection.cursor()
    
    # Get user's energy usage data
    cur.execute("""
        SELECT DATE(date) as date, power_usage 
        FROM energy_usage 
        WHERE user_id = %s 
        ORDER BY date DESC 
        LIMIT 30
    """, (current_user.id,))
    energy_data = cur.fetchall()
    
    # Get energy saving tips
    cur.execute("""
        SELECT t.*, u.username, COUNT(l.id) as likes
        FROM energy_tips t
        LEFT JOIN users u ON t.user_id = u.id
        LEFT JOIN tip_likes l ON t.id = l.tip_id
        GROUP BY t.id
        ORDER BY likes DESC
        LIMIT 5
    """)
    tips = cur.fetchall()
    
    # Get leaderboard
    cur.execute("""
        SELECT username, eco_points 
        FROM users 
        ORDER BY eco_points DESC 
        LIMIT 5
    """)
    leaderboard = cur.fetchall()
    
    cur.close()
    
    return render_template('dashboard.html',
                         energy_data=energy_data,
                         tips=tips,
                         leaderboard=leaderboard)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/energy-usage', methods=['POST'])
@login_required
def log_energy_usage():
    if not request.is_json:
        return jsonify({'error': 'Missing JSON'}), 400
        
    data = request.get_json()
    
    appliance = data.get('appliance')
    power_usage = data.get('power_usage')
    usage_time = data.get('usage_time')

    if not all([appliance, power_usage, usage_time]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        mysql = get_db()
        cur = mysql.connection.cursor()
        
        # Log energy usage
        cur.execute(
            "INSERT INTO energy_usage (user_id, appliance, power_usage, usage_time, date) VALUES (%s, %s, %s, %s, NOW())",
            (current_user.id, appliance, power_usage, usage_time)
        )
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'message': 'Energy usage logged successfully'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
