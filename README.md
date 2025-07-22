# 🎓 EduVision – Smart Face Attendance Recognition System

**EduVision** is a smart, secure, and easy-to-use face recognition-based attendance system, built mainly for educational institutions. It’s designed to make attendance tracking simple and contactless using facial recognition. Only verified faculty members can access and manage the system, ensuring complete control and privacy.

---

## ✨ What This Project Does

This system allows faculty members to:
- Log in securely
- Register students by their ID, name, and a clear face photo
- Take attendance using live camera and face recognition
- View attendance reports
- Export those reports to Excel (CSV format)

The goal is to eliminate manual errors, save time, and provide a contactless attendance solution.

---

## 👨‍🏫 Who Can Use It?

Only authorized faculty members can access the system after logging in. Once logged in, they'll see a dashboard and menu options like:

- **Dashboard**
- **Register Student**
- **Take Attendance**
- **Reports**

---

## 🧑‍🎓 Student Registration

The "Register Student" page allows the faculty to add a student by:
- Entering their Student ID and Name
- Uploading a **clear, front-facing photo**

Once submitted, the student data and facial encoding are saved into the database. Only these registered faces can be recognized later.

---

## 📸 Taking Attendance

From the **Take Attendance** page:
- The camera will activate
- Faculty can select a subject
- The system will recognize and mark attendance only for the registered students
- If the face is matched from the database, attendance is marked

---

## 📊 Reports & Exports

The **Reports** page shows detailed attendance records:
- Daily and subject-wise attendance
- How many students were present
- Attendance statistics
- Export to Excel using the **"Export to CSV"** button

---

## 📈 Dashboard Overview

The **Dashboard** gives a quick overview of:
- Total number of registered students
- How many attended today
- Weekly attendance summary
- Recent attendance activity

All the key stats in one place!

---

## 🛠 Built With

- **Backend**: Python (Flask), Dlib, OpenCV
- **Frontend**: HTML, CSS (plain), JavaScript
- **Database**: MySQL
- **Libraries**: NumPy, Pandas, MySQL Connector

---

## 💻 How to Run This Project

1. **Clone this repo**:
```bash
git clone https://github.com/your-username/eduvision-face-attendance.git
cd eduvision-face-attendance


📂 Project Structure (Simplified)

EduVision/
├── app.py                # Main app
├── register_face.py      # Student registration logic
├── take_attendance.py    # Face recognition script
├── static/               # CSS, JS
├── templates/            # HTML pages
├── dataset/              # Stored face images
├── encodings/            # Stored face encodings
└── requirements.txt



🧠 Notes
The system works best with clear and bright lighting.

Make sure the student’s photo is front-facing and not blurry during registration.

Attendance will only be marked if the face is recognized and already registered.



👨‍💻 Developed By
Shaik Sharu

📧 Email: shaiks.sharuk@gmail.com
🔗 LinkedIn: sharu-shaik-b98659284
💻 GitHub: Shaik-sharuk

