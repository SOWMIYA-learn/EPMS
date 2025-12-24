🏥 Electronic Patient Management System (EPMS)

A lightweight and efficient web-based Electronic Patient Management System (EPMS) developed using Python Flask.
This system enables secure digital management of patient records, report uploads, and QR-code–based public patient access, providing a clean and user-friendly interface for healthcare administrators.

⭐ Features
🧑‍⚕️ Patient Registration & Management

Add new patient records

Edit and update patient details

View individual patient information

Display all patients in a structured table

📄 Medical Records & Reports

Upload and store patient reports/documents

View uploaded files securely

📱 QR Code / Public Patient Access

Automatically generate QR code for each patient

Scan QR code to view public patient details on mobile

Public view shows limited, non-sensitive information

🔐 Secure Login System

User authentication with login and registration

Protected routes for internal access

📊 Dashboard Overview

Quick access to patient records

Simple and intuitive navigation

🛠️ Tech Stack
Component	Technology
Frontend	HTML5, CSS3, JavaScript
Backend	Python (Flask)
Database	SQLite
Libraries	Flask-SQLAlchemy, QRCode, Pillow
Tools	VS Code, Git
📁 Project Structure
EPMS/
├── app.py                # Main Flask application
├── models.py             # Database models
├── patient.db            # SQLite database
├── .gitignore
│
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── add_patient.html
│   ├── edit_patient.html
│   ├── view_patient.html
│   ├── patients_table.html
│   ├── public_patient.html
│   └── layout.html
│
├── uploads/              # Uploaded patient files
├── venv/                 # Virtual environment
└── README.md             # Project documentation

🚀 How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/SOWMIYA-learn/EPMS.git
cd EPMS

2️⃣ Create & Activate Virtual Environment
python -m venv venv


Windows

venv\Scripts\activate


Linux / macOS

source venv/bin/activate

3️⃣ Install Dependencies
pip install flask flask-sqlalchemy qrcode pillow

4️⃣ Run the Application
python app.py

5️⃣ Open in Browser
http://127.0.0.1:5000/

📌 QR Code Functionality

Each patient record generates a unique QR code

Scanning the QR opens a public patient details page

Optimized for mobile viewing

Sensitive information remains protected

📌 Future Enhancements

Role-based access control (Admin, Doctor, Staff)

Cloud deployment (Render / AWS)

Advanced patient search and filtering

Appointment scheduling module

Email / SMS notifications

Analytics and reporting dashboard

🤝 Contributions

Contributions are welcome!
Feel free to fork this repository, improve features, and submit pull requests.

👩‍💻 Author

Sowmiya S
Second Year ECE | Aspiring IT Professional
Interests: Python, Web Development, AI

📄 License

This project is released under the MIT License and is intended for educational and learning purposes.
