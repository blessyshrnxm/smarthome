from flask import Flask, render_template, request, redirect, url_for, flash  
from flask_mysqldb import MySQL  
from flask_bcrypt import Bcrypt  
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  

app = Flask(__name__)  
app.secret_key = 'your_secret_key_here'  

# MySQL Configuration  
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = '123456'  
app.config['MYSQL_DB'] = 'energy_saver'  
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  

mysql = MySQL(app)  
bcrypt = Bcrypt(app)  
login_manager = LoginManager(app)  
login_manager.login_view = 'login'  


class User(UserMixin):  
    def __init__(self, id, username):  
        self.id = id  
        self.username = username  

@login_manager.user_loader  
def load_user(user_id):  
    cur = mysql.connection.cursor()  
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))  
    user = cur.fetchone()  
    cur.close()  
    if user:  
        return User(user['id'], user['username'])  
    return None  

@app.route('/')  
def home():  
    return render_template('index.html')  

@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST':  
        username = request.form['username']  
        email = request.form['email']  
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')  

        cur = mysql.connection.cursor()  
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))  
        mysql.connection.commit()  
        cur.close()  

        flash('Registration successful! Please log in.', 'success')  
        return redirect(url_for('login'))  

    return render_template('register.html')  

@app.route('/login', methods=['GET', 'POST'])  
def login():  
    if request.method == 'POST':  
        email = request.form['email']  
        password = request.form['password']  

        cur = mysql.connection.cursor()  
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))  
        user = cur.fetchone()  
        cur.close()  

        if user and bcrypt.check_password_hash(user['password'], password):  
            login_user(User(user['id'], user['username']))  
            return redirect(url_for('dashboard'))  

        flash('Invalid credentials. Try again!', 'danger')  
    return render_template('login.html')  

@app.route('/dashboard')  
@login_required  
def dashboard():  
    cur = mysql.connection.cursor()  
    cur.execute("SELECT * FROM energy_usage WHERE user_id = %s", (current_user.id,))  
    energy_data = cur.fetchall()  
    cur.close()  
    return render_template('dashboard.html', energy_data=energy_data)  

@app.route('/logout')  
@login_required  
def logout():  
    logout_user()  
    return redirect(url_for('home'))  

if __name__ == '__main__':  
    app.run(debug=True)  
