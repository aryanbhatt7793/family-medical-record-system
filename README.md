# MediQR – Family Medical Record System

A web-based medical information management and emergency access system developed as a mini project by **Aryan Bhatt and Archi**, under the guidance of **Mr. Dhruv Shah**.

MediQR allows users to maintain their medical information and share essential emergency details through a personal QR code. It also provides an approval-based access mechanism for sharing additional medical information when required.

---

## Project Overview

During medical emergencies, accessing important health information quickly can be difficult. Medical details may be stored in different documents or applications, making them difficult to locate when time is critical.

MediQR provides a centralized web application where users can maintain their medical profiles and make selected emergency information accessible through a QR code.

The system also allows visitors to request access to additional medical information. The account owner can approve or deny these requests, maintaining control over the information being shared.

## Problem Statement

Important medical information is not always readily available during emergencies. Finding relevant details about a person's medical history, conditions, or other emergency information can cause delays.

The objective of MediQR is to simplify emergency access to medical information through a QR-based system with owner-controlled access permissions.

## Project Objectives

- Develop a web-based medical information management system.
- Provide secure user registration and login functionality.
- Allow users to maintain their medical profiles.
- Generate unique QR codes for emergency access.
- Display essential emergency information through QR scanning.
- Allow visitors to request additional medical information.
- Provide approval and denial controls to the account owner.
- Generate downloadable PDF medical information.
- Make the application accessible through desktop and mobile browsers.

## Features

### 1. User Authentication
- User registration and login.
- Session-based authentication.
- Individual user dashboards.

### 2. Medical Profile Management
- Maintain personal and medical information.
- Access medical information through the dashboard.

### 3. QR-Based Emergency Access
- Generate a personal QR code for each user.
- Display and download the QR code.
- Allow emergency contacts to access basic emergency information by scanning the QR code.

### 4. Emergency Access Requests
- Visitors can request access to additional medical information.
- A reason for the request is required.
- The account owner can approve or deny requests.
- Additional medical information is displayed after approval.

### 5. PDF Generation
- Generate downloadable PDF medical information.
- Make medical information easier to access and share when needed.

### 6. Web Accessibility
- Browser-based application.
- Accessible through laptops, desktops, and smartphones.
- Dashboard notification sound can alert the owner to incoming access requests while the dashboard is open and active.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Authentication | Flask-Login |
| Database ORM | SQLAlchemy |
| Database | SQLite |
| QR Code Generation | Python QR Code Library |
| PDF Generation | ReportLab |
| Application Server | Gunicorn |
| Cloud Hosting | AWS EC2 |
| Operating System | Amazon Linux 2023 |
| Version Control | Git and GitHub |

## System Architecture

```text
              User / Emergency Contact
                         |
                         v
                  Web Interface
              HTML + CSS + JavaScript
                         |
                         v
                   Flask Backend
                         |
             +-----------+-----------+
             |                       |
             v                       v
       User Authentication     Emergency Access
                                  Workflow
             |                       |
             +-----------+-----------+
                         |
                         v
                   SQLite Database
                         |
                         v
              QR Code / PDF Generation
                         |
                         v
                    Gunicorn
                         |
                         v
                     AWS EC2
```

## Project Directory Structure

```text
family-medical-record-system/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── database/
│   └── medical.db
│
├── generated_qr/
│
├── generated_pdf/
│
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── emergency.html
│   ├── login.html
│   ├── medical_access.html
│   ├── request_access.html
│   ├── signup.html
│   └── waiting.html
│
└── README.md
```

*Note: The database and generated files are created or maintained locally when the application runs. They are excluded from the GitHub repository.*

## Installation and Setup

Follow these steps to run MediQR locally.

### Prerequisites

- Python 3.10 or later.
- pip (Python package manager).
- Git.
- A web browser.

### Step 1: Clone the Repository

```bash
git clone https://github.com/aryanbhatt7793/family-medical-record-system.git
```

Navigate into the project directory:

```bash
cd family-medical-record-system
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Register a new account to start using the application.

## Cloud Deployment

MediQR is deployed using Amazon Web Services (AWS).

### Deployment Environment

- Cloud Provider: Amazon Web Services.
- Service: Amazon EC2.
- Operating System: Amazon Linux 2023.
- Python Environment: Python virtual environment.
- Application Server: Gunicorn.
- Process Management: systemd.

Gunicorn runs the Flask application, while systemd manages the application as a background service. This allows the application to continue running independently of the developer's local computer, as long as the EC2 instance remains running.

## Team Members and Contributions

### Aryan Bhatt
- Designed and developed the Flask backend.
- Implemented user registration, login, and authentication.
- Integrated the SQLite database using SQLAlchemy.
- Developed medical profile management functionality.
- Implemented QR code generation and emergency access.
- Developed the emergency access request workflow.
- Implemented request approval and denial functionality.
- Integrated PDF generation and download.
- Configured AWS EC2 deployment and application hosting.

### Archi
- Contributed to frontend interface review and improvements.
- Worked on HTML templates and CSS styling.
- Prepared and maintained project documentation.
- Documented the application architecture and workflows.
- Performed functional testing of registration and login.
- Tested QR-based emergency access and request approval workflows.
- Verified application usability on desktop and mobile browsers.

**Note:** Contributions should be updated to reflect the work actually completed by each team member.

## Project Guide

**Mr. Dhruv Shah**

## Future Scope

The project can be enhanced with the following features:

- HTTPS implementation and improved data security.
- OTP-based emergency access verification.
- Push notifications for emergency access requests.
- Medical document upload and management.
- Family member profile management.
- Medicine and insurance record management.
- Access history and audit logs.
- Dedicated Android and iOS applications.

## Security Note

MediQR is an academic project and is not intended to replace professional medical record systems.

The current demonstration uses HTTP and should not be used to transmit real sensitive medical information. Additional security measures, including HTTPS, stronger secret management, CSRF protection, and access auditing, should be implemented before handling real medical data.

## Project Information

| Detail | Information |
|---|---|
| Project Name | Family Medical Record System (MediQR) |
| Project Type | Mini Project |
| Backend | Python Flask |
| Database | SQLite |
| Deployment | AWS EC2 |
| Version Control | GitHub |
| Team Members | Aryan Bhatt and Archi |
| Project Guide | Mr. Dhruv Shah |

## Repository

GitHub: https://github.com/aryanbhatt7793/family-medical-record-system

---

**Developed by Aryan Bhatt and Archi**  
*Under the guidance of Mr. Dhruv Shah.*
