CREATE DATABASE quotes_db;
USE quotes_db;
show tables;
CREATE TABLE quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote TEXT,
    author VARCHAR(255),
    tags VARCHAR(255)
);

USE quotes_db;
SHOW TABLES;
SELECT COUNT(*) FROM quotes;
SELECT * FROM quotes LIMIT 5;
SELECT COUNT(*) AS total_quotes FROM quotes;
SELECT COUNT(DISTINCT author) AS unique_authors FROM quotes;
SELECT * 
FROM quotes
WHERE tags LIKE '%inspirational%';

