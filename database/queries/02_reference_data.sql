
USE library_management;

-- =====================================================
-- 1. INSERT: Add an author
-- =====================================================

INSERT INTO authors (author_name, biography)
VALUES (
    'Andrew S. Tanenbaum',
    'Computer science author and educator.'
);


-- =====================================================
-- 2. INSERT: Add a publisher
-- =====================================================

INSERT INTO publishers (publisher_name, address)
VALUES (
    'Example Academic Publications',
    'New Delhi, India'
);


-- =====================================================
-- 3. INSERT: Add a category
-- =====================================================

INSERT INTO categories (category_name, description)
VALUES (
    'Artificial Intelligence',
    'Books related to artificial intelligence and machine learning.'
);


-- =====================================================
-- 4. SELECT: Display all authors
-- =====================================================

SELECT
    author_id,
    author_name,
    biography
FROM authors
ORDER BY author_name;


-- =====================================================
-- 5. SELECT: Display all publishers
-- =====================================================

SELECT
    publisher_id,
    publisher_name,
    address
FROM publishers
ORDER BY publisher_name;


-- =====================================================
-- 6. SELECT: Display all categories
-- =====================================================

SELECT
    category_id,
    category_name,
    description
FROM categories
ORDER BY category_name;


-- =====================================================
-- 7. UPDATE: Modify author information
-- =====================================================

-- Replace the ID with an existing author ID.
-- UPDATE authors
-- SET biography = 'Updated author biography.'
-- WHERE author_id = 1;


-- =====================================================
-- 8. UPDATE: Modify publisher information
-- =====================================================

-- UPDATE publishers
-- SET address = 'Updated publisher address'
-- WHERE publisher_id = 1;


-- =====================================================
-- 9. UPDATE: Modify category information
-- =====================================================

-- UPDATE categories
-- SET description = 'Updated category description'
-- WHERE category_id = 1;


-- =====================================================
-- 10. JOIN: Display books with authors
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
-- 11. JOIN: Display books with publisher/category
-- =====================================================

SELECT
    b.title,
    p.publisher_name,
    c.category_name
FROM books AS b
INNER JOIN publishers AS p
    ON b.publisher_id = p.publisher_id
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.title;


-- =====================================================
-- 12. AGGREGATE: Number of books in each category
-- =====================================================

SELECT
    c.category_name,
    COUNT(b.book_id) AS total_books
FROM categories AS c
LEFT JOIN books AS b
    ON c.category_id = b.category_id
GROUP BY c.category_id, c.category_name
ORDER BY total_books DESC;
