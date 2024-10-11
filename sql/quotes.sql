-- -- Table with Incrementing Integer ID
-- CREATE TABLE books (
--     id INTEGER PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     price DECIMAL(10, 2) NOT NULL,
--     availability INTEGER NOT NULL,
--     star_rating DECIMAL(3, 2),
--     category VARCHAR(70) NOT NULL
-- );

-- -- Table with UUID (Other RDBMS)
-- CREATE TABLE books (
--     id VARCHAR(36) PRIMARY KEY,
--     title VARCHAR(255) NOT NULL,
--     price DECIMAL(10, 2) NOT NULL,
--     availability INTEGER NOT NULL,
--     star_rating DECIMAL(3, 2),
--     category VARCHAR(70) NOT NULL
-- );

-- Table with UUID (Postgres - supports UUID natively)
CREATE TABLE quotes (
    id UUID PRIMARY KEY,
    text VARCHAR(255) NOT NULL,
    category VARCHAR(70) NOT NULL,
    author VARCHAR(100) REFERENCES authors(author)
);

CREATE TABLE tags (
    tag VARCHAR(100) PRIMARY KEY
)

CREATE TABLE quotes_tags_link (
    quote_id UUID,
    tag VARCHAR(100),
    FOREIGN KEY (quote_id) REFERENCES quotes(id),
    FOREIGN KEY (tag) REFERENCES tags(tag)
)

CREATE TABLE authors (
    author VARCHAR(100) PRIMARY KEY,
    about TEXT
)