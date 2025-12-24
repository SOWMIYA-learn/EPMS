# 🏥 Electronic Patient Management System (EPMS)

A lightweight and efficient web-based Electronic Patient Management System (EPMS) developed using Python Flask.  
The system digitizes patient records, enables secure data handling, supports report uploads, and provides QR-code–based public patient access optimized for mobile devices.

This project is designed as an academic and portfolio-ready healthcare application, demonstrating backend development, database integration, and real-world workflow implementation.

----

## ⭐ Features

### 🧑‍⚕️ Patient Registration & Management
- Add, update, view, and manage patient records  
- Display all patients in a structured table  
- View individual patient profiles  

### 📄 Medical Records & Reports
- Upload and store patient medical reports  
- Secure server-side file handling  

### 📱 QR Code / Public Patient Access
- Automatically generate a unique QR code for each patient  
- Scan QR code to access public patient details on mobile  
- Public view restricted to non-sensitive information  

### 🔐 Secure Authentication
- User login and registration system  
- Protected routes for internal access  

### 🎨 Clean User Interface
- Simple and responsive UI using HTML, CSS, and JavaScript  
- Organized layout with reusable templates  

---

## 🛠️ Tech Stack

| Component | Technology |
|--------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python (Flask) |
| Database | SQLite |
| Libraries | Flask-SQLAlchemy, QRCode, Pillow |
| Tools | VS Code, Git |

---

## 📁 Project Structure
EPMS/
├── app.py # Main Flask application
├── models.py # Database models
├── patient.db # SQLite database
├── .gitignore
│
├── static/
│ ├── css/
│ │ └── styles.css
│ └── js/
│ └── main.js
│
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── add_patient.html
│ ├── edit_patient.html
│ ├── view_patient.html
│ ├── patients_table.html
│ ├── public_patient.html
│ └── layout.html
│
├── uploads/ # Uploaded patient reports
├── venv/ # Virtual environment
└── README.md # Project documentation


---

## 🚀 How to Run the Project

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/SOWMIYA-learn/EPMS.git
cd EPMS

## 2️⃣ Create & Activate Virtual Environment

Create a virtual environment:
```bash
python -m venv venv

Activate the virtual environment:
**Windows**
```bash
venv\Scripts\activate
**Linux / macOS**
```bash
source venv/bin/activate

## 3️⃣ Install Dependencies
```bash
pip install flask flask-sqlalchemy qrcode pillow

## 4️⃣ Run the Application
```bash
python app.py

## 5️⃣ Open in Browser
```cpp
http://127.0.0.1:5000/

👩‍💻 Author

Sowmiya S

📄 License

This project is released under the MIT License and is intended for educational and learning purposes.










