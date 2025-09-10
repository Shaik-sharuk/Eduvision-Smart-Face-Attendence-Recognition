# 🎓 EduVision - Smart Face Recognition Attendance System  

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)  
![Flask](https://img.shields.io/badge/Flask-Framework-black?logo=flask)  
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green?logo=mongodb)  
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-orange?logo=opencv)  
![License](https://img.shields.io/badge/License-MIT-yellow?logo=open-source-initiative)  
![Status](https://img.shields.io/badge/Status-Active-success)  
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)  

---

## 📌 Overview
**EduVision** is a comprehensive web-based attendance management system that utilizes advanced **facial recognition technology** to automate student attendance tracking.  
Built with **Flask** and **MongoDB**, this system provides educational institutions with a modern, efficient, and accurate solution for managing attendance.

---

## ✨ Key Features
- ✅ **Facial Recognition Attendance**: Real-time attendance marking using face detection & recognition  
- ✅ **Multi-Image Registration**: Register students with multiple images for improved accuracy  
- ✅ **Manual Capture**: Manual attendance option  
- ✅ **Comprehensive Reporting**: Detailed attendance reports with visual analytics  
- ✅ **Student Management**: Full CRUD operations for student records  
- ✅ **Class Management**: Organize attendance by different classes/subjects  
- ✅ **Data Export**: Export attendance records to CSV format  
- ✅ **Responsive Design**: Works seamlessly on desktop and mobile  

---

## 🛠️ Technology Stack

**Backend**  
- Flask (Python Web Framework)  
- dlib-based Face Recognition  
- MongoDB (NoSQL database)  
- PyMongo (MongoDB driver)  

**Frontend**  
- Bootstrap 5 (Responsive UI)  
- JavaScript (Logic & API interactions)  
- Chart.js (Data visualization)  
- Webcam API (Browser-based camera access)  

**Computer Vision**  
- OpenCV (Image processing)  
- dlib (Facial recognition toolkit)  
- NumPy (Numerical computations for face encodings)  

---

## 📦 Installation & Setup

### ✅ Prerequisites
- Python 3.8+  
- MongoDB 4.4+  
- Modern browser with camera support  



## 🚀 Step-by-Step Setup

## Clone repository
git clone https://github.com/yourusername/Eduvision-Smart-Face-Attendence-Recognition.git
cd Eduvision-Smart-Face-Attendence-Recognition

## Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

## Install dependencies
pip install -r requirements.txt

## Run application
python app.py
Now, open http://localhost:5000 in your browser.




## 🎯 Usage Guide

### 👩‍🎓 Student Registration
- Navigate to Register Student

- Enter details & upload multiple facial images

- System processes and stores encodings

### 🕒 Taking Attendance
- Go to Take Attendance

- Select class

- Capture using webcam

- Review & confirm recognized students

### 📊 Generating Reports
- Access Reports

- View daily/subject-wise records

- Export data to CSV


---

📁 Project Structure
```
eduvision-face-attendance/
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── uploads/           # Temp image storage
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── take_attendance.html
│   ├── register.html
│   ├── reports.html
│   ├── login.html
│   └── register_user.html
└── README.md              # Documentation
```

---


## 🔧 API Endpoints
- GET / → Dashboard

- GET/POST /take_attendance → Attendance capture

- GET/POST /register_student → Register student

- GET /reports → Reports

- GET /export-csv → Export attendance

- GET/POST /login → Authentication

- GET/POST /register_user → New user registration

---

## 👥 Development Team
### 👨‍💻 Sharuk Shaik

- 📧 Email: shaiks.sharuk@gmail.com

- 🔗 LinkedIn: linkedin.com/in/sharu-shaik-b98659284

- 🎯 Role: Full Stack Developer & Project Lead


---

🤝 Contributing
- Fork this project

- Create feature branch → git checkout -b feature/AmazingFeature

- Commit changes → git commit -m 'Add AmazingFeature'

- Push branch → git push origin feature/AmazingFeature

- Open a Pull Request

---

📝 License
- This project is licensed under the MIT License – see the LICENSE file for details.

---

## 🙏 Acknowledgments
- face_recognition by Adam Geitgey

- Flask

- MongoDB

- Bootstrap


---


## ⚠️ Known Limitations
- Accuracy depends on hardware & lighting conditions

- Large student databases may require optimization

- Requires modern browser with camera support


---


## 📞 Support
- 📧 Email: shaiks.sharuk@gmail.com
- 🔗 LinkedIn: linkedin.com/in/sharu-shaik-b98659284
