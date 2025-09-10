#!/usr/bin/env python3
import os
import datetime
import numpy as np
import face_recognition
from pymongo import MongoClient, ASCENDING
from flask import Flask, flash, make_response, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import logging
from logging.handlers import RotatingFileHandler
from bson.binary import Binary
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

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
# Configurations for MongoDB
app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
app.config['MONGO_DB_NAME'] = 'eduvision_db'

# Increase timeout for face recognition
app.config['FACE_RECOGNITION_TIMEOUT'] = 30  # seconds

app.logger.info('EduVision application startup')

app.secret_key = 'eduvision_secret_123'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SESSION_COOKIE_NAME'] = 'eduvision_session'

# # MongoDB Configuration
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "eduvision_db"

# Initialize MongoDB connection

def get_db():
    """Get MongoDB database connection with proper error handling"""
    try:
        # Update with your actual MongoDB connection string
        client = MongoClient(
            app.config.get('MONGO_URI', 'mongodb://localhost:27017/'),
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000  # 10 second connection timeout
        )
        
        # Test the connection
        client.admin.command('ismaster')
        
        db_name = app.config.get('MONGO_DB_NAME', 'eduvision_db')
        return client[db_name]
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        app.logger.error(f"MongoDB connection failed: {str(e)}")
        return None
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return None
# Create collections if not exists
def init_db():
    db = get_db()
    if db is None:
        app.logger.error("Database connection failed during initialization")
        return
        
    # Create collections
    collections = ['students', 'attendance', 'users']
    for col in collections:
        if col not in db.list_collection_names():
            db.create_collection(col)
            app.logger.info(f"Created collection: {col}")
    
    # Create indexes
    db.students.create_index([("student_id", ASCENDING)], unique=True)
    db.attendance.create_index([("timestamp", ASCENDING)])
    db.users.create_index([("username", ASCENDING)], unique=True)
    
    # Create default admin user if not exists
    if db.users.count_documents({"username": "admin"}) == 0:
        db.users.insert_one({
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        })
        app.logger.info("Created default admin user")

# Create directories if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

# Helper functions
def get_students():
    db = get_db()
    if db is None:
        return []
    return list(db.students.find().sort("registered_on", -1))

def get_attendance():
    db = get_db()
    if db is None:
        return []
    
    # Using MongoDB aggregation to join collections
    pipeline = [
        {
            "$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "student_id",
                "as": "student_info"
            }
        },
        {"$unwind": "$student_info"},
        {"$sort": {"timestamp": -1}},
        {"$limit": 20},
        {
            "$project": {
                "student_id": 1,
                "timestamp": 1,
                "class_name": 1,
                "confidence": 1,
                "name": "$student_info.name"
            }
        }
    ]
    
    return list(db.attendance.aggregate(pipeline))

def get_attendance_stats():
    db = get_db()
    if db is None:
        return {
            'today_count': 0,
            'total_students': 0,
            'week_count': 0,
            'daily_data': []
        }
    
    # Today's attendance
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_end = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    today_count = db.attendance.count_documents({
        "timestamp": {"$gte": today_start, "$lte": today_end}
    })
    
    # Total students
    total_students = db.students.count_documents({})
    
    # This week attendance (unique students)
    week_start = datetime.datetime.now() - datetime.timedelta(days=7)
    week_count = len(db.attendance.distinct("student_id", {
        "timestamp": {"$gte": week_start}
    }))
    
    # Attendance by day (last 7 days)
    daily_data = []
    for i in range(7):
        day = datetime.date.today() - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)
        
        count = db.attendance.count_documents({
            "timestamp": {"$gte": day_start, "$lte": day_end}
        })
        daily_data.append((day.strftime("%Y-%m-%d"), count))
    
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
        
        db = get_db()
        if db is None:
            return render_template('login.html', error='Database connection failed')
            
        user = db.users.find_one({"username": username})
        
        if user and user['password'] == password:
            session['user'] = {
                'username': user['username'],
                'role': user['role']
            }
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'teacher')
        
        if not username or not password:
            return render_template('register_user.html', error='Username and password are required')
        
        if password != confirm_password:
            return render_template('register_user.html', error='Passwords do not match')
        
        db = get_db()
        if db is None:
            return render_template('register_user.html', error='Database connection failed')
        
        # Check if username exists
        if db.users.find_one({"username": username}):
            return render_template('register_user.html', error='Username already exists')
        
        # Create new user
        db.users.insert_one({
            "username": username,
            "password": password,
            "role": role
        })
        
        flash('User registered successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register_user.html')

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
        name = request.form.get('name')
        student_id = request.form.get('student_id')
        image_files = request.files.getlist('images')  # Allow multiple images
        
        if not name or not student_id or not image_files:
            flash('Please fill all fields and upload at least one image', 'danger')
            return redirect(url_for('register'))
        
        # Get MongoDB connection
        db = get_db()
        if db is None:
            flash('Database connection failed', 'danger')
            return redirect(url_for('register'))
            
        # Check if student already exists
        if db.students.find_one({'student_id': student_id}):
            flash('Student ID already exists', 'danger')
            return redirect(url_for('register'))
        
        # Process multiple images for better recognition
        face_encodings = []
        for image_file in image_files:
            if image_file.filename == '':
                continue
                
            # Save temporary image
            filename = f"temp_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            
            try:
                # Process image
                img = face_recognition.load_image_file(filepath)
                
                # Try different models for face detection
                face_locations = face_recognition.face_locations(img, model="hog")
                if not face_locations:
                    face_locations = face_recognition.face_locations(img, model="cnn")
                
                if face_locations:
                    # Get face encodings
                    encodings = face_recognition.face_encodings(img, face_locations, num_jitters=2)
                    if encodings:
                        face_encodings.extend(encodings)
                
            except Exception as e:
                app.logger.error(f"Error processing image {image_file.filename}: {str(e)}")
            finally:
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        if not face_encodings:
            flash('No faces detected in the uploaded images', 'danger')
            return redirect(url_for('register'))
        
        # Calculate average encoding for better recognition
        avg_encoding = np.mean(face_encodings, axis=0)
        
        # Store student data
        db.students.insert_one({
            'student_id': student_id,
            'name': name,
            'face_encoding': avg_encoding.tobytes(),
            'registration_date': datetime.datetime.now(),
            'image_count': len(face_encodings)
        })
        
        flash(f'Student {name} registered successfully with {len(face_encodings)} facial encodings', 'success')
        return redirect(url_for('manage_students'))
    
    return render_template('register.html')

# ... rest of the code remains the same ...
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
            # Process image with enhanced settings
            img = face_recognition.load_image_file(filepath)
            
            # Try multiple face detection models
            face_locations = face_recognition.face_locations(img, model="hog")
            if not face_locations:
                face_locations = face_recognition.face_locations(img, model="cnn")
                
            face_encodings = face_recognition.face_encodings(img, face_locations, num_jitters=2)
            
            # Get MongoDB connection
            db = get_db()
            if db is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
                
            # Get all students from database
            students_collection = db['students']
            students = list(students_collection.find({}))
            
            recognized_students = []
            
            # Compare faces with enhanced matching
            for face_encoding in face_encodings:
                best_match = None
                best_confidence = 0
                
                for student in students:
                    try:
                        if 'face_encoding' not in student or not student['face_encoding']:
                            continue
                            
                        # Convert stored encoding back to numpy array
                        db_encoding = np.frombuffer(student['face_encoding'], dtype=np.float64)
                        
                        # Use lower tolerance for more strict matching
                        matches = face_recognition.compare_faces([db_encoding], face_encoding, tolerance=0.5)
                        face_distance = face_recognition.face_distance([db_encoding], face_encoding)[0]
                        confidence = (1 - face_distance) * 100
                        
                        # Track the best match
                        if matches[0] and confidence > best_confidence:
                            best_match = student
                            best_confidence = confidence
                            
                    except Exception as e:
                        app.logger.error(f"Error processing student {student.get('student_id', 'unknown')}: {str(e)}")
                        continue
                
                # Only accept matches with sufficient confidence
                if best_match and best_confidence > 65:  # Lowered threshold to 65%
                    # Check if already recorded today (prevent duplicates)
                    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    existing_attendance = db.attendance.find_one({
                        'student_id': best_match['student_id'],
                        'timestamp': {'$gte': today_start},
                        'class_name': class_name
                    })
                    
                    if not existing_attendance:
                        # Record attendance
                        db.attendance.insert_one({
                            'student_id': best_match['student_id'],
                            'timestamp': datetime.datetime.now(),
                            'class_name': class_name,
                            'confidence': best_confidence
                        })
                    
                    recognized_students.append({
                        'student_id': best_match['student_id'],
                        'name': best_match['name'],
                        'confidence': f"{best_confidence:.2f}%",
                        'already_recorded': existing_attendance is not None
                    })
            
            return jsonify({
                'status': 'success',
                'recognized': recognized_students,
                'count': len([s for s in recognized_students if not s['already_recorded']])
            })
            
        except Exception as e:
            app.logger.error(f"Attendance processing error: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
            
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)  # Clean up temp file
                
    return render_template('take_attendance.html')


@app.route('/reports')
@login_required
def reports():
    try:
        db = get_db()
        # Check if database connection is valid by attempting a simple operation
        try:
            # Try to list collections to verify connection
            db.list_collection_names()
        except Exception as db_error:
            app.logger.error(f"Database connection failed: {str(db_error)}")
            flash('Database connection failed. Please check your database configuration.', 'danger')
            return render_template('reports.html', 
                                  daily_data=[],
                                  student_data=[],
                                  class_data=[])
        
        # Daily attendance (last 30 days)
        daily_data = []
        try:
            daily_data = list(db.attendance.aggregate([
                {
                    "$group": {
                        "_id": {"$dateToString": { "format": "%Y-%m-%d", "date": "$timestamp" }},
                        "count": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": -1}},
                {"$limit": 30},
                {
                    "$project": {
                        "date": "$_id",
                        "count": 1,
                        "_id": 0
                    }
                }
            ]))
        except Exception as e:
            app.logger.error(f"Error retrieving daily data: {str(e)}")
            flash('Error retrieving daily attendance data', 'warning')
        
        # Student attendance
        student_data = []
        try:
            student_data = list(db.attendance.aggregate([
                {
                    "$group": {
                        "_id": "$student_id",
                        "attendance_count": {"$sum": 1},
                        "last_attendance": {"$max": "$timestamp"}
                    }
                },
                {
                    "$lookup": {
                        "from": "students",
                        "localField": "_id",
                        "foreignField": "student_id",
                        "as": "student_info"
                    }
                },
                {"$unwind": "$student_info"},
                {
                    "$project": {
                        "student_id": "$_id",
                        "name": "$student_info.name",
                        "attendance_count": 1,
                        "last_attendance": 1
                    }
                },
                {"$sort": {"attendance_count": -1}}
            ]))
        except Exception as e:
            app.logger.error(f"Error retrieving student data: {str(e)}")
            flash('Error retrieving student attendance data', 'warning')
        
        # Class attendance
        class_data = []
        try:
            class_data = list(db.attendance.aggregate([
                {
                    "$group": {
                        "_id": "$class_name",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "class_name": "$_id",
                        "count": 1,
                        "_id": 0
                    }
                },
                {"$sort": {"count": -1}}
            ]))
        except Exception as e:
            app.logger.error(f"Error retrieving class data: {str(e)}")
            flash('Error retrieving class attendance data', 'warning')
        
        # Log data retrieval results
        app.logger.info(f"Retrieved {len(daily_data)} daily records, {len(student_data)} student records, {len(class_data)} class records")
        
        return render_template('reports.html', 
                              daily_data=daily_data,
                              student_data=student_data,
                              class_data=class_data)
        
    except Exception as e:
        app.logger.error(f"Unexpected error in reports route: {str(e)}")
        flash('An unexpected error occurred while generating reports', 'danger')
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
        db = get_db()
        # Check if database connection is valid by attempting a simple operation
        try:
            # Try to list collections to verify connection
            db.list_collection_names()
        except Exception as db_error:
            app.logger.error(f"Database connection failed: {str(db_error)}")
            # Return a plain text error response instead of redirecting
            response = make_response("Database connection failed")
            response.headers['Content-Type'] = 'text/plain'
            response.status_code = 500
            return response
            
        # Get student attendance data
        student_data = list(db.attendance.aggregate([
            {
                "$group": {
                    "_id": "$student_id",
                    "attendance_count": {"$sum": 1},
                    "last_attendance": {"$max": "$timestamp"}
                }
            },
            {
                "$lookup": {
                    "from": "students",
                    "localField": "_id",
                    "foreignField": "student_id",
                    "as": "student_info"
                }
            },
            {"$unwind": "$student_info"},
            {
                "$project": {
                    "student_id": "$_id",
                    "name": "$student_info.name",
                    "attendance_count": 1,
                    "last_attendance": 1
                }
            }
        ]))
        
        # Create CSV content
        csv_content = "Student ID,Name,Attendance Count,Last Attendance\n"
        for row in student_data:
            last_attendance = row['last_attendance'].strftime('%Y-%m-%d %H:%M') if row.get('last_attendance') else 'Never'
            # Escape any commas in names to prevent CSV format issues
            name = str(row['name']).replace('"', '""') if row.get('name') else ''
            csv_content += f'"{row["student_id"]}","{name}",{row["attendance_count"]},{last_attendance}\n'
        
        # Create response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=attendance_report.csv'
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting CSV: {str(e)}")
        # Return a plain text error response instead of redirecting
        response = make_response(f"Error generating CSV: {str(e)}")
        response.headers['Content-Type'] = 'text/plain'
        response.status_code = 500
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)