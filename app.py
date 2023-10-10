import sqlite3

# Create a SQLite database connection
conn = sqlite3.connect('../userdb.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create the users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    firstName TEXT,
    lastName TEXT,
    email TEXT UNIQUE
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def get_db_connection():
    conn = sqlite3.connect('../userdb.db')
    conn.row_factory = sqlite3.Row
    return conn


# User Registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']

        # Check for password match
        if password != confirmPassword:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate username or email
        cursor.execute('SELECT * FROM users WHERE username=? OR email=?', (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username or email already exists', 'error')
            conn.close()
            return redirect(url_for('signup'))

        # Insert the new user into the database
        cursor.execute('INSERT INTO users (username, password, firstName, lastName, email) VALUES (?, ?, ?, ?, ?)',
                       (username, password, firstName, lastName, email))
        conn.commit()
        conn.close()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            flash('Login successful', 'success')
            return redirect(url_for('welcome', name=username))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/welcome/<name>')
def welcome(name):
    # Pass the user information to the template
    user = {'username': name}
    return render_template('welcome.html', user=user)
