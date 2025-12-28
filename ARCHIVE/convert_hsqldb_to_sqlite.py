#!/usr/bin/env python3
"""
Convert HSQLDB SQL script to SQLite3 compatible SQL.
"""

import re
import sys


def convert_hsqldb_to_sqlite(input_file, output_file):
    """Convert HSQLDB SQL to SQLite SQL."""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = []
    
    for line in lines:
        # Remove HSQLDB-specific SET DATABASE commands
        if line.strip().startswith('SET DATABASE'):
            continue
            
        # Remove SET FILES commands
        if line.strip().startswith('SET FILES'):
            continue
            
        # Remove SET SCHEMA commands (we'll handle schema differently)
        if line.strip().startswith('SET SCHEMA'):
            continue
            
        # Remove ALTER USER commands
        if line.strip().startswith('ALTER USER'):
            continue
            
        # Remove CREATE USER commands (SQLite doesn't have user management)
        if line.strip().startswith('CREATE USER'):
            continue
            
        # Remove GRANT statements (SQLite doesn't have GRANT)
        if line.strip().startswith('GRANT'):
            continue
            
        # Remove ALTER SEQUENCE
        if 'ALTER SEQUENCE' in line:
            continue
            
        # Convert MEMORY TABLE to CREATE TABLE
        line = re.sub(r'CREATE MEMORY TABLE', 'CREATE TABLE', line)
        
        # Convert data types
        # VARCHAR(16777216) -> TEXT
        line = re.sub(r'VARCHAR\(16777216\)', 'TEXT', line)
        # VARCHAR(255) -> TEXT
        line = re.sub(r'VARCHAR\(255\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(500\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(256\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(100\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(50\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(36\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(32\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(20\)', 'TEXT', line)
        line = re.sub(r'VARCHAR\(10\)', 'TEXT', line)
        # BIGINT -> INTEGER
        line = re.sub(r'BIGINT', 'INTEGER', line)
        # NUMERIC(10,2) -> REAL
        line = re.sub(r'NUMERIC\(10,2\)', 'REAL', line)
        # BOOLEAN -> INTEGER (SQLite uses 0/1 for boolean)
        line = re.sub(r'BOOLEAN', 'INTEGER', line)
        # DATE -> TEXT (SQLite doesn't have DATE type, we'll store as TEXT)
        line = re.sub(r'DATE', 'TEXT', line)
        
        # Remove PUBLIC schema prefix
        line = re.sub(r'PUBLIC\.', '', line)
        
        # Quote reserved keywords - USER is a reserved keyword in SQLite
        line = re.sub(r'\bUSER\b', '"USER"', line)
        # VERSION might also be problematic
        line = re.sub(r'\bVERSION\b', '"VERSION"', line)
        
        # Keep INSERT statements as-is (they should work with converted schema)
        
        converted_lines.append(line)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)
    
    print(f"Converted {len(lines)} lines to SQLite format")
    print(f"Output written to {output_file}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_hsqldb_to_sqlite.py "
              "<input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_hsqldb_to_sqlite(input_file, output_file)
