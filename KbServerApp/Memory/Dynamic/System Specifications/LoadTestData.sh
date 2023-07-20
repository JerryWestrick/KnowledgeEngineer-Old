#!/bin/bash

# Path to SQLite executable
SQLITE="/path/to/sqlite3"

# Path to SQLTestData.sql file
SQL_FILE="/path/to/SQLTestData.sql"

# Name of the SQLite database
DB_NAME="BookStore.db"

# Load test data into SQLite database
$SQLITE $DB_NAME < $SQL_FILE