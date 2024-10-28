CREATE TABLE authors (
    author VARCHAR(100) PRIMARY KEY,
    about TEXT
);

CREATE TABLE quotes (
    id UUID PRIMARY KEY,
    text VARCHAR(255) NOT NULL,
    category VARCHAR(70) NOT NULL,
    author VARCHAR(100),
    FOREIGN KEY (author) REFERENCES authors(author)
);

CREATE TABLE tags (
    tag VARCHAR(100) PRIMARY KEY
);

CREATE TABLE quotes_tags_link (
    quote_id UUID,
    tag VARCHAR(100),
    FOREIGN KEY (quote_id) REFERENCES quotes(id),
    FOREIGN KEY (tag) REFERENCES tags(tag)
);

-- only insert changes when pages change
CREATE TABLE pagesnum_changes (
    pagesnum INTEGER,
    time_stamp DATE
)