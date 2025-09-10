EduVision - Smart Face Recognition Attendance System
Overview
EduVision is a comprehensive web-based attendance management system that utilizes advanced facial recognition technology to automate student attendance tracking. Built with Flask and MongoDB, this system provides educational institutions with a modern, efficient, and accurate solution for managing student attendance.

✨ Key Features
Facial Recognition Attendance: Real-time attendance marking using face detection and recognition

Multi-Image Registration: Register students with multiple images for improved recognition accuracy

Automated & Manual Capture: Both automatic and manual attendance capture options

Comprehensive Reporting: Detailed attendance reports with visual analytics

Student Management: Complete CRUD operations for student records

Class Management: Organize attendance by different classes/subjects

Data Export: Export attendance records to CSV format

Responsive Design: Works seamlessly on desktop and mobile devices

🛠️ Technology Stack
Backend
Flask: Python web framework

Face Recognition: dlib-based facial recognition library

MongoDB: NoSQL database for flexible data storage

PyMongo: MongoDB Python driver

Frontend
Bootstrap 5: Responsive UI framework

JavaScript: Frontend logic and API interactions

Chart.js: Data visualization for reports

Webcam API: Browser-based camera access

Computer Vision
OpenCV: Image processing

dlib: Machine learning toolkit for facial recognition

NumPy: Numerical computations for face encodings

📦 Installation & Setup
Prerequisites
Python 3.8+

MongoDB 4.4+

Modern web browser with camera support

Step-by-Step Setup
Clone the repository

bash
git clone https://github.com/yourusername/eduvision-face-attendance.git
cd eduvision-face-attendance
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Configure MongoDB

Install and start MongoDB service

The application will automatically create the necessary database and collections

Run the application

bash
python app.py
Access the system

Open http://localhost:5000 in your browser

Use the default credentials:

Username: admin

Password: admin123

🎯 Usage Guide
Student Registration
Navigate to "Register Student"

Enter student details and upload multiple facial images

System processes and stores facial encodings for recognition

Taking Attendance
Go to "Take Attendance" page

Select appropriate class

Position students in front of camera

Use capture button to process attendance

Review recognized students and confirm

Generating Reports
Access "Reports" section

View daily attendance trends

Analyze student-wise attendance records

Export data to CSV for further analysis

📁 Project Structure
text
eduvision-face-attendance/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── static/               # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # Temporary image storage
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── take_attendance.html
│   ├── register.html
│   ├── reports.html
│   ├── login.html
│   └── register_user.html
└── README.md             # Project documentation
🔧 API Endpoints
GET / - Dashboard

GET/POST /take_attendance - Attendance capture

GET/POST /register_student - Student registration

GET /reports - Attendance reports

GET /export-csv - Export attendance data

GET/POST /login - User authentication

GET/POST /register_user - User registration

👥 Development Team
This project was developed by:

Sharuk Shaik

Email: shaiks.sharuk@gmail.com

LinkedIn: linkedin.com/in/sharu-shaik-b98659284

Role: Full Stack Developer & Project Lead

🤝 Contributing
Fork the project

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
face_recognition library by Adam Geitgey

Flask team for the excellent web framework

MongoDB for the robust database solution

Bootstrap for the responsive UI components

⚠️ Known Limitations
Performance depends on hardware capabilities

Recognition accuracy varies with lighting conditions

Large student databases may require optimization

Requires modern browser with camera support

📞 Support
For support, please contact:

Email: shaiks.sharuk@gmail.com

LinkedIn: linkedin.com/in/sharu-shaik-b98659284

Note: This system is designed for educational purposes and should be tested thoroughly before deployment in production environments.

