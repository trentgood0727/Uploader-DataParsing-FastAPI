CREATE TABLE file_records (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    status VARCHAR(50), -- status（ex: Uploading, parsing, completed, failed)
    uploaded_at TIMESTAMP DEFAULT NOW() -- CURRENT_TIMESTAMP
);

CREATE TABLE parsed_content (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES file_records(id),
    content TEXT
);

ALTER DATABASE file_upload_db SET timezone TO 'Asia/Taipei';
