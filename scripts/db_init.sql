-- scripts/db_init.sql
CREATE TABLE IF NOT EXISTS sales (
    order_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    product_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    total_amount NUMERIC(12,2) GENERATED ALWAYS AS (quantity*price) STORED,
    country TEXT NOT NULL
);-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total_amount NUMERIC(10,2),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table used to track files detected in MinIO
-- This table ensures files are processed exactly once
-- and allows retries when failures occur.

CREATE TABLE IF NOT EXISTS processed_files (

    -- Primary identifier
    id SERIAL PRIMARY KEY,

    -- MinIO bucket where file exists
    bucket_name VARCHAR(255) NOT NULL,

    -- Full object path in MinIO (must be unique)
    object_name TEXT NOT NULL UNIQUE,

    -- Entity type derived from folder name
    -- Example: users, products, orders, order_items
    entity_type VARCHAR(50) NOT NULL,

    -- File metadata from MinIO
    file_size BIGINT,
    etag VARCHAR(255),
    last_modified TIMESTAMP,

    -- Processing lifecycle status
    -- detected → processing → processed
    -- or failed (with retries)
    status VARCHAR(20) DEFAULT 'detected',

    -- Retry control
    retry_count INT DEFAULT 0,
    max_retries INT DEFAULT 3,

    -- Timestamps
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_processed_files_status
ON processed_files(status);

-- Index for entity filtering
CREATE INDEX IF NOT EXISTS idx_processed_files_entity
ON processed_files(entity_type);

-- Index for retry logic
CREATE INDEX IF NOT EXISTS idx_processed_files_retry
ON processed_files(status, retry_count);

-- Index for detection ordering
CREATE INDEX IF NOT EXISTS idx_processed_files_detected_at
ON processed_files(detected_at);