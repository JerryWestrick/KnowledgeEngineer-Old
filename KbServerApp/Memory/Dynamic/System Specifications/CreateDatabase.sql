-- Create the Admins table
CREATE TABLE IF NOT EXISTS Admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Create the Operators table
CREATE TABLE IF NOT EXISTS Operators (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Create the Users table
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Create the Books table
CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price REAL NOT NULL
);

-- Create the Transactions table
CREATE TABLE IF NOT EXISTS Transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    transaction_date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (book_id) REFERENCES Books (id)
);

-- Create the Logs table
CREATE TABLE IF NOT EXISTS Logs (
    id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,
    log_message TEXT NOT NULL
);

-- Create the Library table
CREATE TABLE IF NOT EXISTS Library (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (book_id) REFERENCES Books (id)
);

-- Create the Reviews table
CREATE TABLE IF NOT EXISTS Reviews (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (book_id) REFERENCES Books (id)
);