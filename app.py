from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

app.secret_key = 'your_secret_key'

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'  # Your MySQL password
app.config['MYSQL_DB'] = 'energy_saver'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Event logging function
def log_event(event_type, description, user_id=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = f"User ID: {user_id}" if user_id else "Anonymous"
    logging.info(f"{timestamp} - {event_type} - {description} - {user_info}")

@app.route('/')
def index():
    # First page showing welcome message with login/register buttons
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        try:
            # Check if email already exists
            cur.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cur.fetchone()
            
            if account:
                flash('Email already exists!', 'danger')
            else:
                # Insert new user
                cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                          (username, email, password))
                mysql.connection.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
                
        except Exception as e:
            flash('Registration failed!', 'danger')
            print(f"Error: {e}")
        finally:
            cur.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        
        # Create cursor
        cur = mysql.connection.cursor()
        
        try:
            # Get user by email and password
            cur.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            account = cur.fetchone()
            
            if account:
                # Create session data
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email/password!', 'danger')
                
        except Exception as e:
            flash('Login failed!', 'danger')
            print(f"Error: {e}")
        finally:
            cur.close()
            
    return render_template('login.html')

@app.route('/home')
def home():
    # Check if user is logged in
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    return render_template('home.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/weather-tips')
def weather_tips():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template('weather_tips.html', username=session['username'])

@app.route('/energy_calculator', methods=['GET', 'POST'])
def energy_calculator():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get data from the form
            lighting = float(request.form['lighting'])
            heating = float(request.form['heating'])
            cooling = float(request.form['cooling'])
            appliances = float(request.form['appliances'])
            total_energy = lighting + heating + cooling + appliances
            total_cost = total_energy * float(request.form['costPerKWh'])
            budget = float(request.form['budget'])
            
            # Insert into database
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO energy_calculations 
                (user_id, lighting, heating, cooling, appliances, total_energy, total_cost, budget) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (session['id'], lighting, heating, cooling, appliances, total_energy, total_cost, budget))
            mysql.connection.commit()
            cursor.close()
            
            return "Success"
            
        except Exception as e:
            print(f"Error: {e}")
            return str(e), 400
            
    return render_template('energy_calculator.html', username=session['username'])

# Test cases function
def run_tests():
    tests = [
        {
            'name': 'Valid Login Test',
            'email': 'test@test.com',
            'password': 'test123',
            'expected': 'success'
        },
        {
            'name': 'Invalid Login Test',
            'email': 'wrong@test.com',
            'password': 'wrong123',
            'expected': 'failure'
        },
        {
            'name': 'Empty Fields Test',
            'email': '',
            'password': '',
            'expected': 'failure'
        }
    ]
    
    results = []
    for test in tests:
        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', 
                         (test['email'], test['password']))
            account = cursor.fetchone()
            cursor.close()
            
            result = 'success' if account else 'failure'
            passed = result == test['expected']
            results.append({
                'test_name': test['name'],
                'passed': passed,
                'expected': test['expected'],
                'actual': result
            })
            
        except Exception as e:
            results.append({
                'test_name': test['name'],
                'passed': False,
                'error': str(e)
            })
    
    return results

if __name__ == '__main__':
    # Run tests before starting the application
    test_results = run_tests()
    for result in test_results:
        log_event('TEST', f"Test: {result['test_name']} - Passed: {result['passed']}")
    
    app.run(debug=True)
