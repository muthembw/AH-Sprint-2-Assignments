from flask import Flask, render_template_string, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'student_records_secret_key_2025'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'student_records',
    'user': 'root',
    'password': 'masila11216'  # Replace with your MySQL password
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database and table"""
    try:
        # First connect without specifying database
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database')
        
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_records")
        cursor.close()
        conn.close()
        
        # Now connect to the database and create table
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE
            )
            """
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database and table created successfully")
            return True
    except Error as e:
        print(f"❌ Error initializing database: {e}")
        return False

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Records System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 15px;
            text-align: center;
        }
        
        .nav a {
            display: inline-block;
            margin: 5px;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background 0.3s;
        }
        
        .nav a:hover {
            background: #0056b3;
        }
        
        .content {
            padding: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-control {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            font-size: 16px;
        }
        
        .btn-primary {
            background: #007bff;
            color: white;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-danger {
            background: #dc3545;
            color: white;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #212529;
        }
        
        .btn:hover {
            opacity: 0.8;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: bold;
        }
        
        .table tr:hover {
            background: #f5f5f5;
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Student Records System</h1>
            <p>Manage your student database</p>
        </div>
        
        <div class="nav">
            <a href="/">📊 Home</a>
            <a href="/add">➕ Add Student</a>
            <a href="/students">👥 View All</a>
            <a href="/search">🔍 Search</a>
        </div>
        
        <div class="content">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ 'success' if category == 'success' else 'danger' }}">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            {{ content|safe }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Home page with dashboard"""
    try:
        conn = get_db_connection()
        if not conn:
            content = """
            <h2>❌ Database Connection Error</h2>
            <p>Unable to connect to the database. Please check your MySQL setup.</p>
            <p>Make sure MySQL is running and the password is correct.</p>
            """
            return render_template_string(HTML_TEMPLATE, content=content)
        
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM students")
        total_students = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(age) FROM students")
        avg_age = cursor.fetchone()[0]
        avg_age = round(avg_age, 1) if avg_age else 0
        
        # Get recent students
        cursor.execute("SELECT * FROM students ORDER BY id DESC LIMIT 5")
        recent_students = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Build content
        content = f"""
        <h2>📊 Dashboard</h2>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_students}</div>
                <div>Total Students</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{avg_age}</div>
                <div>Average Age</div>
            </div>
        </div>
        """
        
        if recent_students:
            content += """
            <h3>📋 Recent Students</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for student in recent_students:
                content += f"""
                    <tr>
                        <td>{student[0]}</td>
                        <td>{student[1]}</td>
                        <td>{student[2]}</td>
                        <td>{student[3]}</td>
                        <td>
                            <a href="/edit/{student[0]}" class="btn btn-warning">✏️ Edit</a>
                            <a href="/delete/{student[0]}" class="btn btn-danger" 
                               onclick="return confirm('Are you sure?')">🗑️ Delete</a>
                        </td>
                    </tr>
                """
            
            content += """
                </tbody>
            </table>
            """
        else:
            content += """
            <div class="alert alert-success">
                <h3>👋 Welcome!</h3>
                <p>No students in the database yet. <a href="/add">Add your first student</a> to get started!</p>
            </div>
            """
        
        return render_template_string(HTML_TEMPLATE, content=content)
        
    except Exception as e:
        content = f"<h2>❌ Error</h2><p>Error loading dashboard: {str(e)}</p>"
        return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Add new student"""
    if request.method == 'POST':
        try:
            name = request.form['name'].strip()
            age = int(request.form['age'])
            email = request.form['email'].strip()
            
            if not name or not email:
                flash('Name and email are required!', 'error')
                return redirect('/add')
            
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed', 'error')
                return redirect('/add')
            
            cursor = conn.cursor()
            query = "INSERT INTO students (name, age, email) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, age, email))
            conn.commit()
            
            flash(f'✅ Student "{name}" added successfully!', 'success')
            cursor.close()
            conn.close()
            
            return redirect('/students')
            
        except mysql.connector.IntegrityError:
            flash('❌ Email already exists! Please use a different email.', 'error')
            return redirect('/add')
        except ValueError:
            flash('❌ Please enter a valid age!', 'error')
            return redirect('/add')
        except Exception as e:
            flash(f'❌ Error adding student: {str(e)}', 'error')
            return redirect('/add')
    
    # GET request - show form
    content = """
    <h2>➕ Add New Student</h2>
    
    <form method="POST">
        <div class="form-group">
            <label for="name">Student Name:</label>
            <input type="text" class="form-control" id="name" name="name" required>
        </div>
        
        <div class="form-group">
            <label for="age">Age:</label>
            <input type="number" class="form-control" id="age" name="age" min="1" max="120" required>
        </div>
        
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" class="form-control" id="email" name="email" required>
        </div>
        
        <button type="submit" class="btn btn-success">✅ Add Student</button>
        <a href="/" class="btn btn-primary">🏠 Back to Home</a>
    </form>
    """
    
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/students')
def view_students():
    """View all students"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return redirect('/')
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY id")
        students = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        content = "<h2>👥 All Students</h2>"
        
        if students:
            content += """
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Email</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for student in students:
                content += f"""
                    <tr>
                        <td>{student[0]}</td>
                        <td>{student[1]}</td>
                        <td>{student[2]}</td>
                        <td>{student[3]}</td>
                        <td>
                            <a href="/edit/{student[0]}" class="btn btn-warning">✏️ Edit</a>
                            <a href="/delete/{student[0]}" class="btn btn-danger" 
                               onclick="return confirm('Are you sure?')">🗑️ Delete</a>
                        </td>
                    </tr>
                """
            
            content += f"""
                </tbody>
            </table>
            <p><strong>Total Students: {len(students)}</strong></p>
            """
        else:
            content += """
            <div class="alert alert-success">
                <h3>📭 No Students Found</h3>
                <p><a href="/add">Add your first student</a> to get started!</p>
            </div>
            """
        
        return render_template_string(HTML_TEMPLATE, content=content)
        
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search_student():
    """Search for students"""
    content = """
    <h2>🔍 Search Students</h2>
    
    <form method="POST">
        <div class="form-group">
            <label for="search_type">Search by:</label>
            <select class="form-control" id="search_type" name="search_type">
                <option value="name">Name</option>
                <option value="id">ID</option>
                <option value="email">Email</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="search_term">Search term:</label>
            <input type="text" class="form-control" id="search_term" name="search_term" required>
        </div>
        
        <button type="submit" class="btn btn-primary">🔍 Search</button>
    </form>
    """
    
    if request.method == 'POST':
        try:
            search_term = request.form['search_term'].strip()
            search_type = request.form['search_type']
            
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed', 'error')
                return render_template_string(HTML_TEMPLATE, content=content)
            
            cursor = conn.cursor()
            
            if search_type == 'id':
                cursor.execute("SELECT * FROM students WHERE id = %s", (int(search_term),))
            elif search_type == 'name':
                cursor.execute("SELECT * FROM students WHERE name LIKE %s", (f"%{search_term}%",))
            elif search_type == 'email':
                cursor.execute("SELECT * FROM students WHERE email LIKE %s", (f"%{search_term}%",))
            
            students = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if students:
                content += f"""
                <h3 style="margin-top: 30px;">Search Results ({len(students)} found)</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Age</th>
                            <th>Email</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for student in students:
                    content += f"""
                        <tr>
                            <td>{student[0]}</td>
                            <td>{student[1]}</td>
                            <td>{student[2]}</td>
                            <td>{student[3]}</td>
                            <td>
                                <a href="/edit/{student[0]}" class="btn btn-warning">✏️ Edit</a>
                                <a href="/delete/{student[0]}" class="btn btn-danger" 
                                   onclick="return confirm('Are you sure?')">🗑️ Delete</a>
                            </td>
                        </tr>
                    """
                
                content += """
                    </tbody>
                </table>
                """
            else:
                content += f'<div class="alert alert-danger">No students found matching "{search_term}"</div>'
                
        except ValueError:
            content += '<div class="alert alert-danger">Please enter a valid ID number</div>'
        except Exception as e:
            content += f'<div class="alert alert-danger">Search error: {str(e)}</div>'
    
    return render_template_string(HTML_TEMPLATE, content=content)

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit student information"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return redirect('/')
        
        cursor = conn.cursor()
        
        if request.method == 'POST':
            name = request.form['name'].strip()
            age = int(request.form['age'])
            email = request.form['email'].strip()
            
            query = "UPDATE students SET name = %s, age = %s, email = %s WHERE id = %s"
            cursor.execute(query, (name, age, email, student_id))
            conn.commit()
            
            flash(f'✅ Student "{name}" updated successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect('/students')
        
        # GET request - show form with current data
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not student:
            flash('Student not found!', 'error')
            return redirect('/students')
        
        content = f"""
        <h2>✏️ Edit Student</h2>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Student Name:</label>
                <input type="text" class="form-control" id="name" name="name" value="{student[1]}" required>
            </div>
            
            <div class="form-group">
                <label for="age">Age:</label>
                <input type="number" class="form-control" id="age" name="age" value="{student[2]}" min="1" max="120" required>
            </div>
            
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" class="form-control" id="email" name="email" value="{student[3]}" required>
            </div>
            
            <button type="submit" class="btn btn-success">💾 Update Student</button>
            <a href="/students" class="btn btn-primary">🏠 Back to Students</a>
        </form>
        """
        
        return render_template_string(HTML_TEMPLATE, content=content)
        
    except Exception as e:
        flash(f'Error editing student: {str(e)}', 'error')
        return redirect('/students')

@app.route('/delete/<int:student_id>')
def delete_student(student_id):
    """Delete a student"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return redirect('/')
        
        cursor = conn.cursor()
        
        # Get student name before deleting
        cursor.execute("SELECT name FROM students WHERE id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            flash('Student not found!', 'error')
        else:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            conn.commit()
            flash(f'✅ Student "{student[0]}" deleted successfully!', 'success')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect('/students')

if __name__ == '__main__':
    print("🚀 Starting Student Records Web Application...")
    
    # Initialize database
    if init_database():
        print("✅ Database initialized successfully")
        print("🌐 Starting web server...")
        print("📱 Open your browser and go to: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        print("❌ Failed to initialize database. Please check your MySQL setup.")
        print("Make sure:")
        print("1. MySQL server is running")
        print("2. Your password is correct in the DB_CONFIG")
        print("3. You can connect to MySQL manually")