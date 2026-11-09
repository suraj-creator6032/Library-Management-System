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

### 5. Configure the MySQL Database

Each team member must create their own local MySQL database. The database is not hosted on GitHub.

The project includes two SQL files inside the `database/` directory:

| File | Purpose |
|---|---|
| `schema.sql` | Creates the database and all 13 tables |
| `sample_data.sql` | Inserts sample records into the tables |

#### Step 5.1: Start MySQL Server

Make sure your local MySQL Server is running.

Open MySQL Workbench and connect to your local MySQL instance.

#### Step 5.2: Create the Database and Tables

1. Open MySQL Workbench.
2. Connect to your local MySQL Server.
3. Open the project file `database/schema.sql`.
4. Execute the entire SQL script using the lightning button or `Ctrl + Shift + Enter`.

This script creates the database:

```sql
library_management
```

It also creates the following 13 tables:

1. departments
2. members
3. authors
4. publishers
5. categories
6. books
7. book_authors
8. book_copies
9. loans
10. reservations
11. fines
12. payments
13. library_settings

#### Step 5.3: Insert Sample Records

After successfully creating all tables:

1. Open `database/sample_data.sql`.
2. Execute the complete SQL script.

This inserts sample departments, members, authors, publishers, categories, books, book copies, loans, reservations, fines, payments and library settings.

**Important:** Execute `schema.sql` before `sample_data.sql`. The sample data script depends on the tables and their foreign-key relationships already existing.

Do not execute the sample data script repeatedly because duplicate primary keys and unique values may cause errors.

#### Step 5.4: Verify the Database

Execute the following queries in MySQL Workbench:

```sql
USE library_management;

SHOW TABLES;

SELECT * FROM departments;
SELECT * FROM members;
SELECT * FROM books;
SELECT * FROM book_copies;
SELECT * FROM loans;
```

You should see all 13 tables and their corresponding sample records.

#### Step 5.5: Configure Django Database Connection

Create a `.env` file in the project root directory (the same directory as `manage.py`).

Use `.env.example` as a reference.

Configure your own local MySQL credentials:

```env
DJANGO_SECRET_KEY=YOUR_SECRET_KEY
DB_NAME=library_management
DB_USER=root
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_HOST=localhost
DB_PORT=3306
```

Replace `YOUR_MYSQL_PASSWORD` with your own MySQL password.

If your MySQL root account has no password, leave `DB_PASSWORD` empty.

Never upload your actual `.env` file to GitHub.

#### Step 5.6: Apply Django Migrations

Once the database and its 13 original tables are ready, return to the project terminal.

Make sure your virtual environment is activated, then execute:

```powershell
python manage.py migrate
```

This creates the additional Django authentication, session, admin and user-profile tables.

The original 13 library tables are not recreated because their Django models use `managed = False`.

#### Step 5.7: Verify Django Connection

Execute:

```powershell
python manage.py check
```

If no errors are reported, the Django project configuration is valid.

You can also inspect the existing database tables using:

```powershell
python manage.py inspectdb
```

### Database Setup Order

Always follow this order when setting up the project on a new computer:

1. Install and start MySQL Server.
2. Execute `database/schema.sql`.
3. Execute `database/sample_data.sql`.
4. Create and configure the `.env` file.
5. Install Python dependencies.
6. Run `python manage.py migrate`.
7. Create a Django administrator using `python manage.py createsuperuser`.
8. Start the server using `python manage.py runserver`.

**Note:** Every developer has an independent local MySQL database. Changes to one developer's local database do not automatically appear in another developer's database. Database schema changes must be shared through updated SQL scripts and coordinated with the team.


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
