# Secure Cloud Data Sharing with Intrusion Monitoring

## Overview
Secure Cloud Data Sharing with Intrusion Monitoring is a Flask-based cybersecurity project designed to provide secure cloud file storage and controlled file sharing. The system uses encryption, multi-level authorization, intrusion detection, account lockout mechanisms, and email-based key distribution to protect sensitive data from unauthorized access.

---

## Features

- User Registration and Login
- Secure File Upload and Download
- Fernet File Encryption
- Multi-Level File Access Approval
- Intrusion Detection and Monitoring
- Account Lockout after Multiple Failed Attempts
- Email Alerts for Security Violations
- Admin Intruder Monitoring Dashboard
- Download Activity Tracking
- Responsive Glassmorphism UI Design

---

## Technology Stack

### Backend
- Python Flask

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Bootstrap Icons

### Database
- MySQL

### Security
- Cryptography (Fernet Encryption)
- Flask-Mail SMTP Integration

---

## System Workflow

1. User uploads a file.
2. File is encrypted and stored securely.
3. Another user sends a request to access the file.
4. Server A verifies the request.
5. Server B verifies the request.
6. File owner grants final approval.
7. Secret decryption key is emailed to requester.
8. User downloads and decrypts the file securely.

---

## Intrusion Detection Mechanism

- Accounts are blocked after 3 failed login attempts.
- Accounts are blocked after 3 incorrect decryption key attempts.
- Intrusion details including IP address and date are stored in the database.
- Security alert emails are automatically sent.
- Admin can monitor and unblock users.

---

## Database Tables

- user
- files
- requests
- intrusion
- downloads

---

## Project Structure

```text
data-breach edit/
│
├── static/
├── templates/
├── dataset/
├── report/
├── app.py
├── import_db.py
├── create_admin.py
├── add_columns.py
├── drop_table.py
└── encryption_key.key
