#!/usr/bin/env python3
"""
Create SQLite database schema only (CREATE TABLE statements).
"""

import sqlite3
import re
import sys


def create_schema(sql_file, db_file):
    """Create SQLite database schema from SQL file."""
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Read the SQL file
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract CREATE TABLE statements (including CREATE UNIQUE INDEX)
    # Simple regex to find CREATE statements
    create_pattern = r'CREATE (?:MEMORY )?TABLE .*?'
    create_pattern += r'(?=\);|$|CREATE|INSERT|SET|GRANT)'
    create_statements = re.findall(create_pattern,
                                   content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(create_statements)} CREATE TABLE statements")
    
    # Also find CREATE UNIQUE INDEX statements
    index_pattern = r'CREATE UNIQUE INDEX .*?'
    index_pattern += r'(?=\);|$|CREATE|INSERT|SET|GRANT)'
    index_statements = re.findall(index_pattern,
                                  content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(index_statements)} CREATE UNIQUE INDEX statements")
    
    # Convert MEMORY TABLE to CREATE TABLE and fix data types
    converted_statements = []
    
    for stmt in create_statements:
        # Convert MEMORY TABLE to CREATE TABLE
        stmt = re.sub(r'CREATE MEMORY TABLE', 'CREATE TABLE',
                      stmt, flags=re.IGNORECASE)
        # Convert data types
        stmt = re.sub(r'VARCHAR\([0-9]+\)', 'TEXT', stmt)
        stmt = re.sub(r'BIGINT', 'INTEGER', stmt)
        stmt = re.sub(r'NUMERIC\(10,2\)', 'REAL', stmt)
        stmt = re.sub(r'BOOLEAN', 'INTEGER', stmt)
        stmt = re.sub(r'DATE', 'TEXT', stmt)
        # Remove PUBLIC schema prefix
        stmt = re.sub(r'PUBLIC\.', '', stmt)
        # Quote reserved keywords
        stmt = re.sub(r'\bUSER\b', '"USER"', stmt)
        stmt = re.sub(r'\bVERSION\b', '"VERSION"', stmt)
        converted_statements.append(stmt)
    
    for stmt in index_statements:
        # Remove PUBLIC schema prefix
        stmt = re.sub(r'PUBLIC\.', '', stmt)
        converted_statements.append(stmt)
    
    # Execute each statement
    success_count = 0
    error_count = 0
    
    for i, stmt in enumerate(converted_statements):
        # Ensure statement ends with semicolon
        if not stmt.strip().endswith(';'):
            stmt = stmt.strip() + ';'
        
        try:
            cursor.execute(stmt)
            success_count += 1
            if success_count % 10 == 0:
                print(f"Created {success_count} schema objects...")
        except sqlite3.Error as e:
            error_count += 1
            print(f"Error executing statement {i}: {e}")
            print(f"Statement: {stmt[:100]}...")
    
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()
    
    print(f"\nSchema creation summary:")
    print(f"  Successfully created: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total tables in database: {len(tables)}")
    
    # List tables
    print("\nTables created:")
    for table in tables[:20]:  # Show first 20 tables
        print(f"  - {table[0]}")
    if len(tables) > 20:
        extra = len(tables) - 20
        print(f"  ... and {extra} more")
    
    conn.close()
    print(f"\nDatabase schema created: {db_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python create_schema_only.py <sql_file> <db_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    db_file = sys.argv[2]
    create_schema(sql_file, db_file)
