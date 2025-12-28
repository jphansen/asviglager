#!/usr/bin/env python3
"""
Create SQLite database from converted SQL file.
"""

import sqlite3
import sys


def create_database(sql_file, db_file):
    """Create SQLite database from SQL file."""
    
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Read the SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Split the script into individual statements
    # Simple approach: split on semicolons
    statements = sql_script.split(';')
    
    # Execute each statement
    for i, statement in enumerate(statements):
        statement = statement.strip()
        if not statement:
            continue
        
        # Skip CREATE SCHEMA as SQLite doesn't support it
        if statement.upper().startswith('CREATE SCHEMA'):
            print(f"Skipping statement {i}: CREATE SCHEMA")
            continue
        
        try:
            cursor.execute(statement)
            print(f"Executed statement {i}: {statement[:50]}...")
        except sqlite3.Error as e:
            print(f"Error executing statement {i}: {e}")
            print(f"Statement: {statement[:100]}...")
            # Try to continue with next statement
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"\nDatabase created: {db_file}")
    print("Note: Some statements may have failed due to SQLite limitations.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_sqlite_db.py <sql_file> <db_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    db_file = sys.argv[2]
    create_database(sql_file, db_file)
