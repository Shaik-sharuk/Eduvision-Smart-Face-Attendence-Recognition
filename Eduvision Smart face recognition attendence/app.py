#!/usr/bin/env python3
import os
import datetime
import numpy as np
import face_recognition
import mysql.connector
from flask import Flask, flash, make_response, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
log_file = 'eduvision.log'

file_handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

app = Flask(__name__)
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('EduVision application startup')

app.secret_key = 'eduvision_secret_123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SESSION_COOKIE_NAME'] = 'eduvision_session'

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'eduvision_user',
    'password': 'SecurePass123!',
    'database': 'eduvision_db',
    'auth_plugin': 'mysql_native_password'
}

# Initialize database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        app.logger.error(f"Database connection error: {err}")
        flash(f"Database error: {err}", 'danger')
        return None

# Create tables if not exists
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        try:
            # Create students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    face_encoding BLOB,
                    registered_on DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    class_name VARCHAR(50),
                    confidence FLOAT,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            ''')
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    role ENUM('admin', 'teacher') NOT NULL
                )
            ''')
            
            # Create default admin user if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, password, role) 
                    VALUES ('admin', 'admin123', 'admin')
                ''')
                app.logger.info("Created default admin user")
            
            conn.commit()
            app.logger.info("Database tables created successfully")
            
        except mysql.connector.Error as err:
            app.logger.error(f"Error creating tables: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

# Create directories if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Helper functions
def get_students():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return students

def get_attendance():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT a.*, s.name 
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.timestamp DESC
        LIMIT 20
    ''')
    attendance = cursor.fetchall()
    cursor.close()
    conn.close()
    return attendance

def get_attendance_stats():
    conn = get_db_connection()
    if not conn:
        return {
            'today_count': 0,
            'total_students': 0,
            'week_count': 0,
            'daily_data': []
        }
        
    cursor = conn.cursor()
    
    # Today's attendance
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) 
        FROM attendance 
        WHERE DATE(timestamp) = CURDATE()
    ''')
    today_count = cursor.fetchone()[0] or 0
    
    # Total students
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0] or 0
    
    # This week attendance
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) 
        FROM attendance 
        WHERE WEEK(timestamp) = WEEK(CURDATE())
    ''')
    week_count = cursor.fetchone()[0] or 0
    
    # Attendance by day
    cursor.execute('''
        SELECT DATE(timestamp) as day, COUNT(DISTINCT student_id) as count
        FROM attendance
        GROUP BY day
        ORDER BY day DESC
        LIMIT 7
    ''')
    daily_data = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return {
        'today_count': today_count,
        'total_students': total_students,
        'week_count': week_count,
        'daily_data': daily_data
    }

# Authentication middleware
def login_required(route_function):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return route_function(*args, **kwargs)
    wrapper.__name__ = route_function.__name__
    return wrapper

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password are required')
        
        conn = get_db_connection()
        if not conn:
            return render_template('login.html', error='Database connection failed')
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and user['password'] == password:
            session['user'] = {
                'username': user['username'],
                'role': user['role']
            }
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    stats = get_attendance_stats()
    attendance = get_attendance()
    students = get_students()
    return render_template('dashboard.html', stats=stats, attendance=attendance, students=students)

@app.route('/register', methods=['GET', 'POST'])
@login_required
def register_student():
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            name = request.form.get('name')
            image = request.files.get('image')
            
            if not student_id or not name or not image:
                flash('All fields are required', 'danger')
                return render_template('register.html')
            
            app.logger.info(f"Registration attempt for {name} ({student_id})")
            
            # Validate image
            if not image.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                flash('Invalid file type. Please upload JPG or PNG images.', 'danger')
                return render_template('register.html')
            
            # Save image
            filename = f"{student_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(filepath)
            app.logger.info(f"Image saved: {filepath}")
            
            # Process face encoding
            img = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(img)
            
            if len(face_locations) == 0:
                os.remove(filepath)
                flash('No face detected. Please try again with a clear face image.', 'danger')
                return render_template('register.html')
            
            face_encoding = face_recognition.face_encodings(img)[0]
            encoding_bytes = np.array(face_encoding).tobytes()
            
            # Save to database
            conn = get_db_connection()
            if not conn:
                flash('Database connection failed', 'danger')
                return render_template('register.html')
                
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO students (student_id, name, face_encoding)
                    VALUES (%s, %s, %s)
                ''', (student_id, name, encoding_bytes))
                conn.commit()
                flash(f'Student {name} registered successfully!', 'success')
                app.logger.info(f"Student {student_id} registered in database")
                
                # Redirect to success page or dashboard
                return redirect(url_for('dashboard'))
            except mysql.connector.IntegrityError as e:
                conn.rollback()
                if "Duplicate entry" in str(e):
                    flash(f'Student ID {student_id} already exists', 'danger')
                else:
                    flash(f'Database error: {str(e)}', 'danger')
                app.logger.error(f"Database error: {str(e)}")
            except Exception as e:
                conn.rollback()
                flash(f'Error saving to database: {str(e)}', 'danger')
                app.logger.error(f"Database error: {str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        except Exception as e:
            flash(f'Error processing registration: {str(e)}', 'danger')
            app.logger.error(f"Registration error: {str(e)}")
    
    # For GET requests or failed POSTs
    return render_template('register.html')

@app.route('/take_attendance', methods=['GET', 'POST'])
@login_required
def take_attendance():
    if request.method == 'POST':
        # Get image from webcam
        image_file = request.files.get('image')
        class_name = request.form.get('class_name', 'General')
        
        if not image_file:
            return jsonify({'status': 'error', 'message': 'No image provided'}), 400
        
        # Save temporary image
        filename = f"attendance_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        
        try:
            # Process image
            img = face_recognition.load_image_file(filepath)
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            
            # Get all students from database
            conn = get_db_connection()
            if not conn:
                return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
                
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT student_id, name, face_encoding FROM students')
            students = cursor.fetchall()
            
            recognized_students = []
            
            # Compare faces
            for face_encoding in face_encodings:
                for student in students:
                    try:
                        if not student['face_encoding']:
                            continue
                            
                        db_encoding = np.frombuffer(student['face_encoding'], dtype=np.float64)
                        matches = face_recognition.compare_faces([db_encoding], face_encoding)
                        face_distance = face_recognition.face_distance([db_encoding], face_encoding)[0]
                        confidence = (1 - face_distance) * 100
                        
                        if matches[0] and confidence > 70:  # Minimum 70% confidence
                            # Record attendance
                            cursor.execute('''
                                INSERT INTO attendance (student_id, class_name, confidence)
                                VALUES (%s, %s, %s)
                            ''', (student['student_id'], class_name, confidence))
                            recognized_students.append({
                                'student_id': student['student_id'],
                                'name': student['name'],
                                'confidence': f"{confidence:.2f}%"
                            })
                            break
                    except Exception as e:
                        app.logger.error(f"Error processing student {student['student_id']}: {str(e)}")
                        continue
            
            conn.commit()
            return jsonify({
                'status': 'success',
                'recognized': recognized_students,
                'count': len(recognized_students)
            })
            
        except Exception as e:
            app.logger.error(f"Attendance processing error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            if os.path.exists(filepath):
                os.remove(filepath)  # Clean up temp file
    
    # For GET requests
    return render_template('take_attendance.html')

@app.route('/reports')
@login_required
def reports():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'danger')
            return render_template('reports.html', 
                                  daily_data=[],
                                  student_data=[],
                                  class_data=[])
            
        cursor = conn.cursor(dictionary=True)
        
        # Daily attendance
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(DISTINCT student_id) as count
            FROM attendance
            GROUP BY date
            ORDER BY date DESC
            LIMIT 30
        ''')
        daily_data = cursor.fetchall()
        
        # Student attendance
        cursor.execute('''
            SELECT s.student_id, s.name, COUNT(a.id) as attendance_count
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name
            ORDER BY attendance_count DESC
        ''')
        student_data = cursor.fetchall()
        
        # Class attendance
        cursor.execute('''
            SELECT class_name, COUNT(*) as count
            FROM attendance
            GROUP BY class_name
            ORDER BY count DESC
        ''')
        class_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('reports.html', 
                              daily_data=daily_data,
                              student_data=student_data,
                              class_data=class_data)
        
    except Exception as e:
        app.logger.error(f"Error in reports route: {str(e)}")
        flash('An error occurred while generating reports', 'danger')
        return render_template('reports.html', 
                              daily_data=[],
                              student_data=[],
                              class_data=[])

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/export-csv')
@login_required
def export_csv():
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'danger')
            return redirect(url_for('reports'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Get student attendance data
        cursor.execute('''
            SELECT s.student_id, s.name, COUNT(a.id) as attendance_count, 
                   MAX(a.timestamp) as last_attendance
            FROM students s
            LEFT JOIN attendance a ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name
            ORDER BY s.name
        ''')
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create CSV content
        csv_content = "Student ID,Name,Attendance Count,Last Attendance\n"
        for row in data:
            last_attendance = row['last_attendance'].strftime('%Y-%m-%d') if row['last_attendance'] else 'Never'
            csv_content += f"{row['student_id']},{row['name']},{row['attendance_count']},{last_attendance}\n"
        
        # Create response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=attendance_report.csv'
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting CSV: {str(e)}")
        flash('An error occurred while exporting CSV', 'danger')
        return redirect(url_for('reports'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)