# Library Management System

A college Library Management System developed using **Django, Python, and MySQL**.

The application is designed to manage books, physical book copies, library members, borrowing, returns, reservations, fines, and payments.

## Technology Stack

- **Backend:** Python, Django 6.0.10
- **Database:** MySQL 8.0+
- **Frontend:** HTML, CSS, Bootstrap (planned)
- **Development environment:** Visual Studio Code
- **Version control:** Git and GitHub

## Project Features

- Book and book-copy management
- Author, publisher, and category management
- Student, faculty, and librarian management
- Book issue and return management
- Reservations
- Fine calculation and payment records
- User authentication
- Role-based access control
- Library reports and statistics

## Project Setup

Follow these instructions to run the project on your local computer.

### 1. Install the required software

Install the following:

- Python 3.14 (or a compatible Python version)
- MySQL Server 8.0 or newer
- MySQL Workbench (recommended)
- Git
- Visual Studio Code

### 2. Clone the repository

Open PowerShell or the VS Code terminal and execute:

```powershell
git clone https://github.com/YOUR_USERNAME/LibraryManagementSystem.git
```

Enter the project directory:

```powershell
cd LibraryManagementSystem
```

### 3. Create a Python virtual environment

```powershell
python -m venv library
```

Activate it:

```powershell
.\library\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```cmd
library\Scripts\activate.bat
```

### 4. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure the MySQL database

Start your MySQL Server.

Open MySQL Workbench and execute the SQL script:

`database/schema.sql`

This creates the `library_management` database and its 13 tables.

To insert the sample records, execute:

`database/sample_data.sql`

**Important:** Every team member must create their own local database. The database is not shared through GitHub.

### 6. Configure environment variables

Create a `.env` file in the project root, in the same directory as `manage.py`.

Use `.env.example` as a reference.

Add your local MySQL credentials:

```env
DJANGO_SECRET_KEY=YOUR_SECRET_KEY
DB_NAME=library_management
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_HOST=localhost
DB_PORT=3306
```

Generate your own Django secret key. Never commit your actual `.env` file.

### 7. Apply Django migrations

Make sure the MySQL database and its 13 original tables have been created before running migrations.

Execute:

```powershell
python manage.py migrate
```

This creates Django's authentication, session, admin, and user-profile tables.

Do not manually create Django's authentication tables.

### 8. Create an administrator account

```powershell
python manage.py createsuperuser
```

Follow the prompts to create your own administrator credentials.

### 9. Start the development server

```powershell
python manage.py runserver
```

Open the application:

- Application: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

## Common Development Commands

Check the Django project:

```powershell
python manage.py check
```

Start the development server:

```powershell
python manage.py runserver
```

Create migrations when changing Django-managed models:

```powershell
python manage.py makemigrations
```

Apply migrations:

```powershell
python manage.py migrate
```

## Team Collaboration

This is a private GitHub repository.

Team members must accept an invitation from the repository owner to access the source code.

Before starting work, pull the latest changes:

```powershell
git pull origin main
```

Create a separate branch for your task:

```powershell
git checkout -b feature/your-feature-name
```

After completing your work:

```powershell
git add .
git commit -m "Describe your changes"
git push -u origin feature/your-feature-name
```

Create a Pull Request on GitHub to merge your changes into the main branch.

Do not directly push unfinished features to `main`.

## Important Notes

- Do not commit `.env`, passwords, secret keys, or database backups containing private information.
- Do not commit your Python virtual environment.
- Existing library tables are managed manually in MySQL and represented by Django models with `managed=False`.
- The `user_profiles` table and Django authentication tables are managed through Django migrations.
- Each developer must maintain their own local MySQL database.

## Project Status

Under active development.
