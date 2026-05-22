# NovaCare — Hospital Patient Management System

A desktop application for managing hospital patient records and appointments, built with Python and CustomTkinter.

---

## Features

- **Secure login & sign up** — per-user accounts with bcrypt-hashed passwords
- **Data isolation** — each user account sees and manages only its own patient records
- **Patient records** — add, update, delete, and view full patient profiles
- **Appointment management** — track doctor assignments and appointment dates
- **Export to CSV** — one-click export of all appointment records
- **Live search & table view** — scrollable appointment records with alternating row styling
- **Patient summary panel** — one-click formatted summary of any selected record
- **Refined dark UI** — consistent indigo-on-dark colour scheme throughout

---

## Requirements

- Python 3.9+
- MySQL 8.0+

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Database Setup

1. Create a MySQL database named `hospital`:
   ```sql
   CREATE DATABASE hospital;
   ```

2. Create the `appointments` table:
   ```sql
   USE hospital;

   CREATE TABLE appointments (
       PatientID          INT AUTO_INCREMENT PRIMARY KEY,
       NameofDoctor       VARCHAR(100),
       Department         VARCHAR(50),
       PatientName        VARCHAR(100),
       PatientDateOfBirth DATE,
       Gender             ENUM('Male', 'Female', 'Other'),
       PatientAddress     VARCHAR(255),
       PatientAge         INT,
       InsuranceProvider  VARCHAR(100),
       BloodGroup         VARCHAR(5),
       PhoneNumber        VARCHAR(20),
       BloodPressure      TEXT,
       DateOfAppointment  DATE,
       DoctorID           VARCHAR(50),
       Nationality        VARCHAR(100),
       Email              VARCHAR(150),
       Medication         VARCHAR(255),
       FurtherInfo        VARCHAR(255),
       user_id            INT NULL
   );

   CREATE INDEX idx_user_id ON appointments(user_id);
   ```

3. The `users` table is created automatically on first launch.

4. Copy `.env.example` to `.env` and fill in your database credentials:
   ```bash
   cp .env.example .env
   ```

---

## Running the App

Always launch via `auth.py` — this is the entry point:

```bash
python auth.py
```

- **Sign Up** to create a new account
- **Login** to access your patient records
- The main application opens automatically after a successful login

> Running `hospital.py` directly is also supported for development, but no user isolation will be applied without a `user_id`.

---

## Project Structure

```
NovaCare/
├── auth.py          # Login & sign up window (entry point)
├── hospital.py      # Main patient management application
├── db.py            # Database connection pool (reads from .env)
├── records.py       # Pure filtering and sorting logic
├── validate.py      # Input validation logic
├── tests/           # Pytest test suite
├── .env             # Your local credentials — never committed
├── .env.example     # Template for setting up credentials
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| GUI        | CustomTkinter (tkinter-based) |
| Database   | MySQL via mysql-connector-python (connection pooling) |
| Auth       | bcrypt password hashing       |
| Language   | Python 3                      |
