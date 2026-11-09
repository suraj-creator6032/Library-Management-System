-- =====================================================
-- LIBRARY MANAGEMENT SYSTEM
-- Sample Database Records
-- =====================================================

USE library_management;


-- 1. DEPARTMENTS
INSERT INTO departments
(department_id, department_name, department_code)
VALUES
(1, 'Computer Science and Engineering', 'CSE'),
(2, 'Electronics and Communication Engineering', 'ECE'),
(3, 'Mechanical Engineering', 'ME'),
(4, 'Electrical Engineering', 'EE');


-- 2. MEMBERS
INSERT INTO members
(member_id, department_id, college_id, full_name,
 email, phone, member_type, joining_date, membership_status)
VALUES
(1, 1, 'EMP001', 'Amit Kumar',
 'amit@college.edu', '9876543210',
 'LIBRARIAN', '2024-01-01', 'ACTIVE'),

(2, 1, 'STU001', 'Rahul Sharma',
 'rahul@college.edu', '9876543211',
 'STUDENT', '2024-08-01', 'ACTIVE'),

(3, 2, 'FAC001', 'Priya Singh',
 'priya@college.edu', '9876543212',
 'FACULTY', '2023-07-01', 'ACTIVE'),

(4, 1, 'STU002', 'Ankit Kumar',
 'ankit@college.edu', '9876543213',
 'STUDENT', '2024-08-01', 'ACTIVE');


-- 3. AUTHORS
INSERT INTO authors
(author_id, author_name, biography)
VALUES
(1, 'Abraham Silberschatz', 'Computer science author and researcher.'),
(2, 'Henry F. Korth', 'Database systems author.'),
(3, 'S. Sudarshan', 'Computer science academic and author.'),
(4, 'Robert C. Martin', 'Software engineering author.'),
(5, 'Herbert Schildt', 'Programming author.');


-- 4. PUBLISHERS
INSERT INTO publishers
(publisher_id, publisher_name, address)
VALUES
(1, 'McGraw Hill', 'New York, USA'),
(2, 'Pearson', 'London, UK'),
(3, 'Prentice Hall', 'New Jersey, USA');


-- 5. CATEGORIES
INSERT INTO categories
(category_id, category_name, description)
VALUES
(1, 'Database Management', 'Books related to databases and DBMS.'),
(2, 'Programming', 'Programming languages and software development.'),
(3, 'Operating Systems', 'Operating system concepts and design.'),
(4, 'Computer Networks', 'Networking concepts and protocols.');


-- 6. BOOKS
INSERT INTO books
(book_id, isbn, title, publisher_id, category_id,
 edition, publication_year, language)
VALUES
(1, '9780078022159', 'Database System Concepts',
 1, 1, '7th Edition', 2019, 'English'),

(2, '9780132350884', 'Clean Code',
 2, 2, '1st Edition', 2008, 'English'),

(3, '9781119800361', 'Operating System Concepts',
 1, 3, '10th Edition', 2021, 'English'),

(4, '9780132126953', 'Computer Networking',
 2, 4, '5th Edition', 2010, 'English');


-- 7. BOOK_AUTHORS
INSERT INTO book_authors
(book_id, author_id)
VALUES
(1, 1),
(1, 2),
(1, 3),
(2, 4),
(3, 1);


-- 8. BOOK_COPIES
INSERT INTO book_copies
(copy_id, book_id, accession_number,
 acquisition_date, copy_status, shelf_location)
VALUES
(1, 1, 'ACC001', '2024-01-10', 'ISSUED', 'A-101'),
(2, 1, 'ACC002', '2024-01-10', 'AVAILABLE', 'A-101'),
(3, 1, 'ACC003', '2024-01-10', 'AVAILABLE', 'A-101'),
(4, 2, 'ACC004', '2024-02-15', 'AVAILABLE', 'B-201'),
(5, 2, 'ACC005', '2024-02-15', 'AVAILABLE', 'B-201'),
(6, 3, 'ACC006', '2024-03-20', 'AVAILABLE', 'C-301'),
(7, 4, 'ACC007', '2024-03-20', 'AVAILABLE', 'D-401');


-- 9. LOANS
INSERT INTO loans
(loan_id, copy_id, member_id, issued_by,
 issue_date, due_date, return_date, loan_status)
VALUES
(1, 1, 2, 1,
 CURDATE(), DATE_ADD(CURDATE(), INTERVAL 14 DAY),
 NULL, 'ISSUED'),

(2, 4, 3, 1,
 DATE_SUB(CURDATE(), INTERVAL 20 DAY),
 DATE_SUB(CURDATE(), INTERVAL 6 DAY),
 CURDATE(), 'RETURNED');


-- 10. RESERVATIONS
INSERT INTO reservations
(reservation_id, book_id, member_id,
 reservation_date, reservation_status, expiry_date)
VALUES
(1, 3, 4,
 NOW(), 'PENDING', DATE_ADD(NOW(), INTERVAL 7 DAY));


-- 11. FINES
INSERT INTO fines
(fine_id, loan_id, fine_amount, fine_status, calculated_at)
VALUES
(1, 2, 30.00, 'PARTIALLY_PAID', NOW());


-- 12. PAYMENTS
INSERT INTO payments
(payment_id, fine_id, amount, payment_date, payment_method)
VALUES
(1, 1, 5.00, NOW(), 'CASH');


-- 13. LIBRARY_SETTINGS
INSERT INTO library_settings
(setting_id, setting_key, setting_value, description)
VALUES
(1, 'MAX_BOOKS_STUDENT', '3',
 'Maximum books a student can borrow'),

(2, 'MAX_BOOKS_FACULTY', '5',
 'Maximum books a faculty member can borrow'),

(3, 'MAX_BOOKS_LIBRARIAN', '3',
 'Maximum books a librarian can borrow'),

(4, 'LOAN_PERIOD_DAYS', '14',
 'Default borrowing period in days'),

(5, 'FINE_PER_DAY', '5.00',
 'Fine charged per overdue day');


-- =====================================================
-- END OF SAMPLE DATA
-- =====================================================