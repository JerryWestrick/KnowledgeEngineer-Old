-- Insert test data for Admins
INSERT INTO Admins (username, password) VALUES
    ('admin1', 'password1'),
    ('admin2', 'password2'),
    ('admin3', 'password3');

-- Insert test data for Operators
INSERT INTO Operators (username, password) VALUES
    ('operator1', 'password1'),
    ('operator2', 'password2'),
    ('operator3', 'password3');

-- Insert test data for Users
INSERT INTO Users (username, password) VALUES
    ('user1', 'password1'),
    ('user2', 'password2'),
    ('user3', 'password3');

-- Insert test data for Books
INSERT INTO Books (title, author, price) VALUES
    ('Book 1', 'Author 1', 10.99),
    ('Book 2', 'Author 2', 12.99),
    ('Book 3', 'Author 3', 9.99);

-- Insert test data for Transactions
INSERT INTO Transactions (user_id, book_id, transaction_date) VALUES
    (1, 1, '2021-01-01'),
    (1, 2, '2021-01-02'),
    (2, 1, '2021-01-03');

-- Insert test data for Logs
INSERT INTO Logs (log_date, log_message) VALUES
    ('2021-01-01', 'Log message 1'),
    ('2021-01-02', 'Log message 2'),
    ('2021-01-03', 'Log message 3');

-- Insert test data for Library
INSERT INTO Library (user_id, book_id) VALUES
    (1, 1),
    (1, 2),
    (2, 1);

-- Insert test data for Reviews
INSERT INTO Reviews (user_id, book_id, review_text) VALUES
    (1, 1, 'Review 1'),
    (1, 2, 'Review 2'),
    (2, 1, 'Review 3');