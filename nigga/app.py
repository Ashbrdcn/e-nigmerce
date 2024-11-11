from flask import Flask, request, render_template, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secure random key in production

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='ecommercedb',
            user='root',
            password=''
        )
        if conn.is_connected():
            print("Database connected successfully.")
        return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/')
def home():
    # Display home page after login/signup if user is authenticated
    if 'user_id' in session:
        return render_template('home.html')
    else:
        flash("You need to log in first.")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error")
            return redirect(url_for('login'))
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash("Both email and password are required")
            return redirect(url_for('login'))

        cursor = conn.cursor()
        query = "SELECT id, password, role FROM userstb WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if user and user[1] == password:
            session['user_id'] = user[0]  # Store user ID in session
            session['role'] = user[2]  # Store user role
            flash("Logged in successfully")
            return redirect(url_for('home'))  # Redirect to homepage
        else:
            flash("Invalid email or password")
            return redirect(url_for('login'))

        conn.close()

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Failed to connect to the database")
            return redirect(url_for('signup'))

        email = request.form.get('email')
        password = request.form.get('password')
        role = 'user'  # Default role is 'user'

        if not email or not password:
            flash("Email and password are required")
            return redirect(url_for('signup'))

        cursor = conn.cursor()
        query = "INSERT INTO userstb (email, password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (email, password, role))
        conn.commit()
        flash("User registered successfully!")
        conn.close()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    
    # Flash message (optional)
    flash("You have been logged out.")
    
    # Redirect to the login page
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
