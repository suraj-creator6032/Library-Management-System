-- =====================================================
-- LIBRARY MANAGEMENT SYSTEM
-- Database Schema
-- MySQL 8.0+
-- =====================================================

CREATE DATABASE IF NOT EXISTS library_management;

USE library_management;


-- 1. DEPARTMENTS
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(20) NOT NULL UNIQUE
);


-- 2. MEMBERS
CREATE TABLE IF NOT EXISTS members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT,
    college_id VARCHAR(30) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(15),
    member_type VARCHAR(20) NOT NULL,
    joining_date DATE NOT NULL,
    membership_status VARCHAR(20) DEFAULT 'ACTIVE',

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);


-- 3. AUTHORS
CREATE TABLE IF NOT EXISTS authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(150) NOT NULL,
    biography TEXT
);


-- 4. PUBLISHERS
CREATE TABLE IF NOT EXISTS publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(150) NOT NULL UNIQUE,
    address TEXT
);


-- 5. CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);


-- 6. BOOKS
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(255) NOT NULL,
    publisher_id INT NOT NULL,
    category_id INT NOT NULL,
    edition VARCHAR(50),
    publication_year INT,
    language VARCHAR(50),

    FOREIGN KEY (publisher_id)
        REFERENCES publishers(publisher_id),

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);


-- 7. BOOK_AUTHORS
CREATE TABLE IF NOT EXISTS book_authors (
    book_id INT,
    author_id INT,

    PRIMARY KEY (book_id, author_id),

    FOREIGN KEY (book_id)
        REFERENCES books(book_id),

    FOREIGN KEY (author_id)
        REFERENCES authors(author_id)
);


-- 8. BOOK_COPIES
CREATE TABLE IF NOT EXISTS book_copies (
    copy_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    accession_number VARCHAR(50) NOT NULL UNIQUE,
    acquisition_date DATE,
    copy_status VARCHAR(20) DEFAULT 'AVAILABLE',
    shelf_location VARCHAR(50),

    FOREIGN KEY (book_id)
        REFERENCES books(book_id)
);


-- 9. LOANS
CREATE TABLE IF NOT EXISTS loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    copy_id INT NOT NULL,
    member_id INT NOT NULL,
    issued_by INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    loan_status VARCHAR(20) DEFAULT 'ISSUED',

    FOREIGN KEY (copy_id)
        REFERENCES book_copies(copy_id),

    FOREIGN KEY (member_id)
        REFERENCES members(member_id),

    FOREIGN KEY (issued_by)
        REFERENCES members(member_id)
);


-- 10. RESERVATIONS
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    member_id INT NOT NULL,
    reservation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    reservation_status VARCHAR(20) DEFAULT 'PENDING',
    expiry_date DATETIME,

    FOREIGN KEY (book_id)
        REFERENCES books(book_id),

    FOREIGN KEY (member_id)
        REFERENCES members(member_id)
);


-- 11. FINES
CREATE TABLE IF NOT EXISTS fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL UNIQUE,
    fine_amount DECIMAL(10,2) NOT NULL,
    fine_status VARCHAR(20) DEFAULT 'PENDING',
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (loan_id)
        REFERENCES loans(loan_id)
);


-- 12. PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    fine_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(30),

    FOREIGN KEY (fine_id)
        REFERENCES fines(fine_id)
);


-- 13. LIBRARY_SETTINGS
CREATE TABLE IF NOT EXISTS library_settings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value VARCHAR(255) NOT NULL,
    description TEXT
);


-- =====================================================
-- END OF DATABASE SCHEMA
-- =====================================================