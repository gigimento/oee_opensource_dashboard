import sys
import json
import decimal
import argparse
import pyodbc

# ----------------------------
# SQL CONNECTION
# ----------------------------
CONN_STR = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=.\SQLEXPRESS;"
    r"DATABASE=SQUAD;"
    r"Trusted_Connection=yes;"
)

def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def custom_serializer(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    return str(obj)

def test_connection():
    log_info("Testing connection to database SQUAD...")
    try:
        conn = pyodbc.connect(CONN_STR, timeout=5)
        log_info("Connection successful!")
        conn.close()
        return True
    except Exception as e:
        log_error(f"Connection failed: {e}")
        return False

def list_tables():
    log_info("Listing tables in SQUAD database...")
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE='BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
    """
    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        print("\n=== TABLES IN DATABASE ===")
        for idx, r in enumerate(rows, 1):
            print(f"{idx:02d}. {r[0]}.{r[1]}")
        print("==========================\n")
        conn.close()
    except Exception as e:
        log_error(f"Failed to list tables: {e}")

def describe_table(table_name: str):
    log_info(f"Describing table: {table_name}...")
    # Split schema and table if provided (e.g. dbo.ProductionData)
    schema = 'dbo'
    name = table_name
    if '.' in table_name:
        schema, name = table_name.split('.', 1)
        
    query = """
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """
    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        cursor.execute(query, (schema, name))
        rows = cursor.fetchall()
        if not rows:
            log_error(f"Table {schema}.{name} not found or has no columns.")
            conn.close()
            return
            
        print(f"\n=== SCHEMA FOR {schema}.{name} ===")
        print(f"{'Column Name':<30} | {'Data Type':<15} | {'Nullable':<8} | {'Max Len':<8}")
        print("-" * 70)
        for r in rows:
            max_len = r[3] if r[3] is not None else ""
            print(f"{r[0]:<30} | {r[1]:<15} | {r[2]:<8} | {max_len:<8}")
        print("===================================\n")
        conn.close()
    except Exception as e:
        log_error(f"Failed to describe table: {e}")

def run_custom_query(sql: str, limit: int = 100):
    log_info(f"Running query: {sql}")
    # Force WITH (NOLOCK) safety check suggestion if not present for SMT data tables
    if "productiondata" in sql.lower() and "nolock" not in sql.lower():
        log_info("Tip: Consider adding WITH (NOLOCK) to prevent lockups on active SMT tables.")
        
    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
        cursor = conn.cursor()
        cursor.execute(sql)
        
        if cursor.description is None:
            # Query did not return rows
            rows_affected = cursor.rowcount
            conn.commit()
            print(f"\nQuery completed successfully. Rows affected: {rows_affected}\n")
            conn.close()
            return

        columns = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
        
        print(f"\n=== QUERY RESULTS (Total rows returned: {len(rows)}) ===")
        # Print header
        col_widths = {col: max(len(col), 10) for col in columns}
        
        # Calculate widths based on data (first 10 rows)
        for row in rows[:10]:
            for i, val in enumerate(row):
                col_name = columns[i]
                val_str = str(val) if val is not None else "NULL"
                col_widths[col_name] = max(col_widths[col_name], len(val_str))
                
        # Format strings
        header_str = " | ".join(f"{col:<{col_widths[col]}}" for col in columns)
        divider_str = "-+-".join("-" * col_widths[col] for col in columns)
        print(header_str)
        print(divider_str)
        
        # Print rows (limited)
        for row in rows[:limit]:
            row_str = " | ".join(f"{str(val) if val is not None else 'NULL':<{col_widths[columns[i]]}}" for i, val in enumerate(row))
            print(row_str)
            
        if len(rows) > limit:
            print(f"\n... and {len(rows) - limit} more rows (output truncated to {limit} rows).")
        print("====================================================\n")
        conn.close()
    except Exception as e:
        log_error(f"Failed to execute query: {e}")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Database Explorer for SQUAD SQL Server")
    parser.add_argument("--test", action="store_true", help="Test connection to SQUAD database")
    parser.add_argument("--list-tables", action="store_true", help="List all tables in the database")
    parser.add_argument("--describe", type=str, help="Describe columns of a table")
    parser.add_argument("--query", type=str, help="Execute a custom SQL query")
    parser.add_argument("--limit", type=int, default=50, help="Limit number of rows returned")
    
    args = parser.parse_args()
    
    if args.test:
        test_connection()
    elif args.list_tables:
        list_tables()
    elif args.describe:
        describe_table(args.describe)
    elif args.query:
        run_custom_query(args.query, args.limit)
    else:
        # Default behavior: test connection and list tables
        if test_connection():
            list_tables()

if __name__ == "__main__":
    main()
