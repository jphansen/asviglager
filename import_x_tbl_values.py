#!/usr/bin/env python3
"""
Import data from X_TBL_VALUES.sql file into SQLite database.

This script reads the X_TBL_VALUES.sql file which contains INSERT statements
and imports the data into a SQLite database.
"""

import sqlite3
import re
import sys
import os


def parse_insert_statement(line):
    """
    Parse an INSERT statement line and extract table name and values.
    
    Expected format: INSERT INTO table_name VALUES('value1','value2',...)
    Returns: (table_name, list_of_values)
    """
    # Match INSERT INTO pattern
    pattern = r'INSERT INTO (\w+) VALUES\((.*)\)'
    match = re.match(pattern, line.strip())
    if not match:
        return None, None
    
    table_name = match.group(1)
    values_str = match.group(2)
    
    # Parse the values string
    values = []
    current_value = ''
    in_quotes = False
    escape_next = False
    i = 0
    length = len(values_str)
    
    while i < length:
        char = values_str[i]
        
        if escape_next:
            current_value += char
            escape_next = False
            i += 1
            continue
            
        if char == '\\' and i + 1 < length:
            # Check if this is a Unicode escape sequence
            next_char = values_str[i + 1]
            if next_char == 'u':
                # Unicode escape sequence \uXXXX
                if i + 5 < length:
                    unicode_seq = values_str[i+2:i+6]
                    try:
                        # Convert Unicode escape to character
                        char_val = chr(int(unicode_seq, 16))
                        current_value += char_val
                        # Skip the entire \uXXXX sequence (6 characters)
                        i += 6
                        continue
                    except ValueError:
                        # If conversion fails, keep the literal backslash
                        current_value += char
                        i += 1
                        continue
                else:
                    # Not enough characters for \uXXXX
                    current_value += char
                    i += 1
                    continue
            else:
                # Other escape sequence
                escape_next = True
                current_value += char
                i += 1
                continue
        elif char == "'" and not escape_next:
            in_quotes = not in_quotes
            i += 1
        elif char == ',' and not in_quotes:
            values.append(current_value)
            current_value = ''
            i += 1
        else:
            current_value += char
            i += 1
    
    # Add the last value
    if current_value:
        values.append(current_value)
    
    # Convert NULL strings to None
    values = [None if v.upper() == 'NULL' else v for v in values]
    
    return table_name, values


def create_database(input_file, db_file):
    """
    Create SQLite database from X_TBL_VALUES.sql file.
    """
    # Connect to SQLite database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    line_count = len(lines)
    print(f"Read {line_count} lines from {input_file}")
    
    # Process each line
    table_name = None
    column_count = None
    inserted_count = 0
    error_count = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Parse the INSERT statement
        table, values = parse_insert_statement(line)
        
        if table is None or values is None:
            msg = f"Warning: Could not parse line {i+1}: {line[:100]}..."
            print(msg)
            error_count += 1
            continue
        
        # Set table name if not set yet
        if table_name is None:
            table_name = table
            column_count = len(values)
            print(f"Table name: {table_name}")
            print(f"Number of columns: {column_count}")
            
            # Create table with generic column names
            col_defs = ', '.join([f'col_{j+1} TEXT' 
                                  for j in range(column_count)])
            create_sql = (f'CREATE TABLE IF NOT EXISTS {table_name} '
                          f'({col_defs})')
            
            try:
                cursor.execute(create_sql)
                msg = f"Created table {table_name} with {column_count} columns"
                print(msg)
            except sqlite3.Error as e:
                print(f"Error creating table: {e}")
                error_count += 1
                continue
        
        # Check if column count matches
        if len(values) != column_count:
            msg = (f"Warning: Line {i+1} has {len(values)} values, "
                   f"expected {column_count}")
            print(msg)
            print(f"Line preview: {line[:100]}...")
            error_count += 1
            continue
        
        # Insert the data
        # Type hint: column_count is guaranteed to be int here
        placeholders = ', '.join(['?'] * column_count)  # type: ignore
        insert_sql = f'INSERT INTO {table_name} VALUES ({placeholders})'
        
        try:
            cursor.execute(insert_sql, values)
            inserted_count += 1
            
            # Print progress every 50 rows
            if inserted_count % 50 == 0:
                print(f"Inserted {inserted_count} rows...")
                
        except sqlite3.Error as e:
            print(f"Error inserting row {i+1}: {e}")
            print(f"Values: {values[:5]}...")  # Show first 5 values
            error_count += 1
    
    # Commit changes
    conn.commit()
    
    # Verify the data
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    row_count = cursor.fetchone()[0]
    
    print("\nImport completed:")
    print(f"  Total lines processed: {line_count}")
    print(f"  Successfully inserted: {inserted_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total rows in table: {row_count}")
    
    # Show column information
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    print("\nTable schema:")
    for col in columns:
        col_id, col_name, col_type = col[0], col[1], col[2]
        print(f"  Column {col_id}: {col_name} ({col_type})")
    
    # Show sample data
    cursor.execute(f'SELECT * FROM {table_name} LIMIT 3')
    sample_rows = cursor.fetchall()
    print("\nSample rows (first 3):")
    for j, row in enumerate(sample_rows):
        print(f"  Row {j+1}: {row[:3]}...")  # Show first 3 columns
    
    conn.close()
    print(f"\nDatabase saved to: {db_file}")
    
    return inserted_count, error_count


def main():
    """Main function."""
    if len(sys.argv) != 3:
        print("Usage: python import_x_tbl_values.py <input_file> <db_file>")
        example = ("Example: python import_x_tbl_values.py "
                   "X_TBL_VALUES.sql inventory.db")
        print(example)
        sys.exit(1)
    
    input_file = sys.argv[1]
    db_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    try:
        inserted, errors = create_database(input_file, db_file)
        if errors > 0:
            msg = f"\nWarning: {errors} errors occurred during import"
            print(msg)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
