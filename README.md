# Library Management System

A web-based **Library Management System** developed using Django, Python, MySQL, HTML and Tailwind CSS. The application is designed to manage the daily operations of a college library, including book inventory, library members, book circulation and reference data.

This project is developed as part of our **Database Management Systems (DBMS) academic project**.

---

## 1. Project Overview

The Library Management System provides a centralized platform for managing a college library.

It supports different library member types:

- **Students** – Browse the book catalogue and view book availability.
- **Faculty** – Access the library catalogue and related information.
- **Librarians** – Manage books, physical copies, authors, publishers and categories.

The application uses Django for backend development and MySQL as its relational database.

## 2. Features

### Authentication and Access Control
- User login and logout.
- Django authentication system.
- User profiles linked to library membership records.
- Role-based access control for librarians and other members.

### Dashboard
- Total book titles.
- Total physical copies.
- Available copies.
- Currently issued books.
- Pending reservations.
- Outstanding fine balance.
- Member account information.

### Books Catalogue
- Browse registered books.
- Search by title, ISBN or author.
- Filter books by category.
- View publisher and publication information.
- View physical copy availability.
- Pagination for catalogue results.

### Book Management
- Add new books.
- Edit existing book information.
- Associate multiple authors with a book.
- Register multiple physical copies.
- Manage accession numbers and shelf locations.
- Safe deletion with protection for historical loan and reservation records.

### Reference Data Management
- Add and edit authors.
- Add and edit publishers.
- Add and edit book categories.

---

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| Frontend | HTML, Tailwind CSS |
| Database | MySQL 8.0+ |
| Database Interface | MySQL Workbench |
| JavaScript | Vanilla JavaScript |
| CSS Build Tool | Tailwind CSS CLI |
| Code Editor | Visual Studio Code |
| Version Control | Git and GitHub |

---

## 4. Database Design

The project uses a relational MySQL database named `library_management`.

### Database Tables

| Table | Purpose |
|---|---|
| departments | Stores department information |
| members | Stores student, faculty and librarian records |
| authors | Stores author information |
| publishers | Stores publisher information |
| categories | Stores book categories |
| books | Stores book title and bibliographic information |
| book_authors | Resolves the many-to-many relationship between books and authors |
| book_copies | Stores individual physical copies |
| loans | Stores book issue and return records |
| reservations | Stores book reservation records |
| fines | Stores fines associated with loans |
| payments | Stores fine payment records |
| library_settings | Stores configurable library settings |

Django's built-in authentication tables are used for application login. The `user_profiles` table connects Django user accounts to existing library members.

### Database Relationships

- One department can have multiple members.
- One publisher can publish multiple books.
- One category can contain multiple books.
- A book can have multiple authors, and an author can write multiple books.
- One book can have multiple physical copies.
- One member can have multiple loans.
- One physical copy can have multiple historical loan records.
- A loan can have an associated fine.
- A fine can have multiple payments.
- A member can make multiple reservations.

---

## 5. DBMS Concepts

The project is designed to demonstrate practical database concepts, including:

- Primary keys and foreign keys.
- Entity integrity and referential integrity.
- One-to-one, one-to-many and many-to-many relationships.
- Database normalization up to 3NF.
- SQL DDL and DML operations.
- SELECT queries and filtering.
- Joins across multiple tables.
- Aggregate functions and GROUP BY.
- Subqueries.
- Database views.
- Stored procedures.
- Triggers.
- Transactions and rollback.
- Indexing and query optimization.
- Constraints and data validation.

SQL demonstration files are maintained separately in the `database/queries/` directory.

---

## 6. Project Structure

```text
Library Management System/
│
├── LibraryManagementSystem/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── library_app/
│   ├── migrations/
│   ├── templates/
│   │   └── library_app/
│   ├── static/
│   │   └── library_app/
│   ├── admin.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── database/
│   ├── schema.sql
│   ├── sample_data.sql
│   └── queries/
│       ├── 01_book_management.sql
│       └── 02_reference_data.sql
│
├── static/
│   ├── src/
│   │   └── input.css
│   └── css/
│       └── output.css
│
├── .env.example
├── .gitignore
├── manage.py
├── package.json
├── package-lock.json
├── requirements.txt
└── README.md
```

---

## 7. Installation and Setup

### Prerequisites

Install the following software:

- Python 3.14 (or a compatible version supported by the project's Django release).
- MySQL Server 8.0 or later.
- MySQL Workbench.
- Node.js LTS and npm.
- Git.

### Step 1: Clone the Repository

```bash
git clone <REPOSITORY_URL>
cd "Library Management System"
```

### Step 2: Create a Python Virtual Environment

Windows PowerShell:

```powershell
python -m venv library
```

Activate it:

```powershell
.\library\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\library\Scripts\Activate.ps1
```

### Step 3: Install Python Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root by copying `.env.example`.

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local MySQL credentials and a new Django secret key.

Example:

```env
DJANGO_SECRET_KEY=your-generated-secret-key
DEBUG=True

DB_NAME=library_management
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

**Never commit `.env` to GitHub.**

### Step 5: Set Up the MySQL Database

Open MySQL Workbench.

Execute the SQL files in this order:

1. `database/schema.sql`
2. `database/sample_data.sql`

The first file creates the database and its 13 application tables. The second inserts demonstration data.

Do not execute `sample_data.sql` repeatedly on an already populated database, because duplicate primary keys may cause errors.

### Step 6: Install Frontend Dependencies

From the project root:

```powershell
npm install
```

### Step 7: Apply Django Migrations

Make sure your virtual environment is activated and the MySQL database is running.

```powershell
python manage.py migrate
```

The existing library tables are managed through SQL and represented by unmanaged Django models. Django migrations handle Django-managed tables, including authentication and the user profile relationship.

Do not regenerate or alter the existing library database schema through Django migrations.

### Step 8: Create a Django Administrator

```powershell
python manage.py createsuperuser
```

Follow the prompts to create an administrator account.

Use Django Admin to create normal Django user accounts and link them to existing library members through `UserProfile`.

### Step 9: Start Tailwind CSS

Open a terminal in the project root:

```powershell
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/css/output.css --watch
```

Keep this terminal running during development.

### Step 10: Start the Django Server

Open another terminal, activate the virtual environment, and execute:

```powershell
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

---

## 8. Development Workflow

During development, two processes should normally be running:

**Terminal 1 – Tailwind watcher**

```powershell
npx @tailwindcss/cli -i ./static/src/input.css -o ./static/css/output.css --watch
```

**Terminal 2 – Django server**

```powershell
python manage.py runserver
```

When Python dependencies change, update `requirements.txt`:

```powershell
pip freeze > requirements.txt
```

When Node dependencies change, commit the updated `package.json` and `package-lock.json`, but do not commit `node_modules/`.

---

## 9. Team Development Guidelines

- Keep all application functionality inside the existing `library_app` Django application.
- Do not create unnecessary additional Django apps.
- Use the existing database schema unless a database change is discussed and approved by the team.
- Keep SQL demonstration queries in `database/queries/`.
- Use Django forms for input validation.
- Apply backend authorization to restricted operations.
- Use transactions for operations involving multiple related database changes.
- Never commit database passwords, secret keys or local environment files.
- Test changes before merging them into the shared project.

---

## 10. Security Notes

- Keep `DEBUG=True` only for local development.
- Use a unique secret key for each development environment.
- Never upload `.env` or real database credentials.
- Use appropriate permissions for different member types.
- Validate user input on the server side.
- Protect state-changing operations against CSRF.
- Use transactions where multiple related database changes must succeed together.

---

## 11. Current Project Scope

The current implementation focuses on:

- Authentication and user profiles.
- Dashboard.
- Books catalogue.
- Book details.
- Book creation and editing.
- Physical copy registration.
- Author, publisher and category management.
- Safe book deletion.

Additional modules can be developed as the project scope requires.

---

## 12. Contributors

Developed by a team of three students as part of an academic DBMS project.

---

**Project:** Library Management System  
**Backend:** Django  
**Database:** MySQL  
**Frontend:** HTML and Tailwind CSS  
**Purpose:** College Library Management and DBMS Demonstration
