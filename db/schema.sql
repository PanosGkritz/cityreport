-- CityReport Database Schema

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    status_id INTEGER NOT NULL,
    latitude REAL,
    longitude REAL,
    address TEXT,
    photo_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    resolved_at TEXT,
    admin_comment TEXT,
    ai_priority TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (status_id) REFERENCES statuses(id)
);
