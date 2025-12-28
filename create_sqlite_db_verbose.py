#!/usr/bin/env python3
"""
Create SQLite database from converted SQL file - verbose version.
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
    
    print(f"Read SQL script: {len(sql_script)} characters")
    
    # Split the script into individual statements
    # Simple approach: split on semicolons
    statements = sql_script.split(';')
    print(f"Found {len(statements)} statements")
    
    # Execute each statement
    success_count = 0
    error_count = 0
    skip_count = 0
    
    for i, statement in enumerate(statements):
        statement = statement.strip()
        if not statement:
            skip_count += 1
            continue
        
        # Skip CREATE SCHEMA as SQLite doesn't support it
        if statement.upper().startswith('CREATE SCHEMA'):
            print(f"Skipping statement {i}: CREATE SCHEMA")
            skip_count += 1
            continue
        
        # Print first 100 chars of statement for debugging
        stmt_preview = statement[:100].replace('\n', ' ')
        
        try:
            cursor.execute(statement)
            success_count += 1
            if success_count % 10 == 0:  # Print progress every 10 statements
                print(f"Executed {success_count} statements...")
        except sqlite3.Error as e:
            error_count += 1
            print(f"Error executing statement {i}: {e}")
            print(f"Statement preview: {stmt_preview}...")
            # Try to continue with next statement
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"\nSummary:")
    print(f"  Total statements: {len(statements)}")
    print(f"  Successfully executed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Skipped: {skip_count}")
    print(f"\nDatabase file: {db_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_sqlite_db_verbose.py <sql_file> <db_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    db_file = sys.argv[2]
    create_database(sql_file, db_file)
