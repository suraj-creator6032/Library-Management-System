
USE library_management;

-- =====================================================
-- 1. READ: Display all books with publisher/category
-- =====================================================

SELECT
    b.book_id,
    b.title,
    b.isbn,
    p.publisher_name,
    c.category_name,
    b.publication_year
FROM books AS b
INNER JOIN publishers AS p
    ON b.publisher_id = p.publisher_id
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.title;


-- =====================================================
-- 2. READ: Display books and their authors
-- =====================================================

SELECT
    b.book_id,
    b.title,
    a.author_name
FROM books AS b
INNER JOIN book_authors AS ba
    ON b.book_id = ba.book_id
INNER JOIN authors AS a
    ON ba.author_id = a.author_id
ORDER BY b.title, a.author_name;


-- =====================================================
-- 3. READ: Count physical copies of every book
-- =====================================================

SELECT
    b.book_id,
    b.title,
    COUNT(bc.copy_id) AS total_copies,
    SUM(
        CASE
            WHEN bc.copy_status = 'AVAILABLE' THEN 1
            ELSE 0
        END
    ) AS available_copies
FROM books AS b
LEFT JOIN book_copies AS bc
    ON b.book_id = bc.book_id
GROUP BY b.book_id, b.title
ORDER BY b.title;


-- =====================================================
-- 4. CREATE: Add a new book title
-- Replace the example values with real values.
-- Publisher and category IDs must already exist.
-- =====================================================

-- INSERT INTO books (
--     isbn,
--     title,
--     publisher_id,
--     category_id,
--     edition,
--     publication_year,
--     language
-- )
-- VALUES (
--     '9780000000001',
--     'Example Database Book',
--     1,
--     1,
--     'First Edition',
--     2026,
--     'English'
-- );


-- =====================================================
-- 5. CREATE: Associate an author with a book
-- Both IDs must already exist.
-- =====================================================

-- INSERT INTO book_authors (book_id, author_id)
-- VALUES (5, 1);


-- =====================================================
-- 6. CREATE: Register a physical copy
-- The referenced book must already exist.
-- Accession number must be unique.
-- =====================================================

-- INSERT INTO book_copies (
--     book_id,
--     accession_number,
--     acquisition_date,
--     copy_status,
--     shelf_location
-- )
-- VALUES (
--     5,
--     'ACC008',
--     CURRENT_DATE(),
--     'AVAILABLE',
--     'A-02'
-- );


-- =====================================================
-- 7. UPDATE: Change book publication information
-- =====================================================

-- UPDATE books
-- SET edition = 'Second Edition',
--     publication_year = 2025
-- WHERE book_id = 5;


-- =====================================================
-- 8. DELETE: Remove an author association
-- This removes only the relationship, not the author.
-- =====================================================

-- DELETE FROM book_authors
-- WHERE book_id = 5
--   AND author_id = 1;



-- =====================================================
-- 9. TRANSACTION: Create a book, author association,
--    and physical copies using explicit SQL.
-- =====================================================

START TRANSACTION;

-- Create the book title.
INSERT INTO books (
    isbn,
    title,
    publisher_id,
    category_id,
    edition,
    publication_year,
    language
)
VALUES (
    '9780000000002',
    'SQL Demonstration Book',
    1,
    1,
    'First Edition',
    2026,
    'English'
);

-- Save the newly generated book ID.
SET @new_book_id = LAST_INSERT_ID();

-- Associate an existing author.
INSERT INTO book_authors (book_id, author_id)
VALUES (@new_book_id, 1);

-- Register two physical copies.
INSERT INTO book_copies (
    book_id,
    accession_number,
    acquisition_date,
    copy_status,
    shelf_location
)
VALUES
    (@new_book_id, 'SQL-DEMO-001', CURRENT_DATE(), 'AVAILABLE', 'A-03'),
    (@new_book_id, 'SQL-DEMO-002', CURRENT_DATE(), 'AVAILABLE', 'A-03');

-- Verify the created book and copies.
SELECT
    b.book_id,
    b.title,
    bc.accession_number,
    bc.copy_status
FROM books AS b
INNER JOIN book_copies AS bc
    ON b.book_id = bc.book_id
WHERE b.book_id = @new_book_id;

-- Use COMMIT only if the verification is correct.
-- Otherwise, execute ROLLBACK instead.

-- COMMIT;
-- ROLLBACK;


-- =====================================================
-- 10. UPDATE: Modify existing book information
-- =====================================================

UPDATE books
SET
    title = 'Advanced Database Systems',
    edition = 'Second Edition',
    publication_year = 2025
WHERE book_id = 5;

-- Verify the update.
SELECT *
FROM books
WHERE book_id = 5;


-- =====================================================
-- 11. UPDATE: Change author associations
-- =====================================================

START TRANSACTION;

DELETE FROM book_authors
WHERE book_id = 5;

INSERT INTO book_authors (book_id, author_id)
VALUES
    (5, 1),
    (5, 2);

-- Verify the author associations.
SELECT
    b.title,
    a.author_name
FROM books AS b
INNER JOIN book_authors AS ba
    ON b.book_id = ba.book_id
INNER JOIN authors AS a
    ON ba.author_id = a.author_id
WHERE b.book_id = 5;

-- COMMIT;
-- ROLLBACK;


-- =====================================================
-- 12. INSERT: Register additional physical copies
-- =====================================================

INSERT INTO book_copies (
    book_id,
    accession_number,
    acquisition_date,
    copy_status,
    shelf_location
)
VALUES
    (5, 'ACC011', CURRENT_DATE(), 'AVAILABLE', 'A-03'),
    (5, 'ACC012', CURRENT_DATE(), 'AVAILABLE', 'A-03');


-- =====================================================
-- 13. REPORT: Inventory summary by book
-- =====================================================

SELECT
    b.book_id,
    b.title,
    COUNT(bc.copy_id) AS total_copies,
    SUM(
        CASE
            WHEN bc.copy_status = 'AVAILABLE' THEN 1
            ELSE 0
        END
    ) AS available_copies,
    SUM(
        CASE
            WHEN bc.copy_status = 'ISSUED' THEN 1
            ELSE 0
        END
    ) AS issued_copies
FROM books AS b
LEFT JOIN book_copies AS bc
    ON b.book_id = bc.book_id
GROUP BY b.book_id, b.title
ORDER BY b.title;



-- =====================================================
-- 14. SAFE DELETE: Delete a book only if it has no
--     loan history and no reservation history.
-- =====================================================

SET @target_book_id = 5;

START TRANSACTION;

-- Check whether the book has loan history.
SELECT COUNT(*) AS loan_history_count
FROM loans AS l
INNER JOIN book_copies AS bc
    ON l.copy_id = bc.copy_id
WHERE bc.book_id = @target_book_id;

-- Check whether the book has reservation history.
SELECT COUNT(*) AS reservation_count
FROM reservations
WHERE book_id = @target_book_id;

-- Execute the following DELETE statements only if
-- both counts are zero.

-- DELETE FROM book_authors
-- WHERE book_id = @target_book_id;

-- DELETE FROM book_copies
-- WHERE book_id = @target_book_id;

-- DELETE FROM books
-- WHERE book_id = @target_book_id;

-- COMMIT;
-- ROLLBACK;
