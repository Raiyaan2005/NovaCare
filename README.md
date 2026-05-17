# NovaCare — Hospital Patient Management System

A desktop application for managing hospital patient records and appointments, built with Python and CustomTkinter.

---

## Features

- **Secure login & sign up** — per-user accounts with SHA-256 hashed passwords
- **Data isolation** — each user account sees and manages only its own patient records
- **Patient records** — add, update, delete, and view full patient profiles
- **Appointment management** — track doctor assignments and appointment dates
- **Live search & table view** — scrollable appointment records with alternating row styling
- **Patient summary panel** — one-click formatted summary of any selected record
- **Refined dark UI** — consistent indigo-on-dark colour scheme throughout

---

## Requirements

- Python 3.9+
- MySQL 8.0+
- Python packages:
  ```
  customtkinter
  mysql-connector-python
  ```

Install dependencies:
```bash
pip install customtkinter mysql-connector-python
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
       PatientID          VARCHAR(20),
       NameofDoctor       VARCHAR(100),
       Department         VARCHAR(100),
       PatientName        VARCHAR(100),
       PatientDateOfBirth DATE,
       Gender             VARCHAR(20),
       PatientAddress     VARCHAR(255),
       PatientAge         INT,
       InsuranceProvider  VARCHAR(100),
       BloodGroup         VARCHAR(10),
       PhoneNumber        VARCHAR(15),
       BloodPressure      VARCHAR(30),
       DateOfAppointment  DATE,
       DoctorID           VARCHAR(20),
       Nationality        VARCHAR(50),
       Email              VARCHAR(100),
       Medication         VARCHAR(255),
       FurtherInfo        TEXT,
       user_id            INT NULL
   );
   ```

3. The `users` table and the `user_id` column on `appointments` are created automatically on first launch.

4. Update the database credentials in both `hospital.py` and `auth.py` if yours differ from the defaults:
   ```python
   DB_CONFIG = dict(host="localhost", user="root", password="your_password", database="hospital")
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
├── auth.py        # Login & sign up window (entry point)
├── hospital.py    # Main patient management application
└── README.md
```

---

## Tech Stack

| Layer      | Technology                    |
|------------|-------------------------------|
| GUI        | CustomTkinter (tkinter-based) |
| Database   | MySQL via mysql-connector-python |
| Auth       | SHA-256 password hashing      |
| Language   | Python 3                      |
