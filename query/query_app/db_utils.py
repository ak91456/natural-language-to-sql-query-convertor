import psycopg2


def _connect(creds):
    return psycopg2.connect(
        dbname=creds["db_name"],
        user=creds["db_user"],
        password=creds["db_password"],
        host=creds["db_host"],
        port=str(creds["db_port"]),
    )


def test_connection(creds):
    try:
        conn = _connect(creds)
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)


def get_schema(creds):
    """Return {table_name: [(col_name, data_type), ...]} for all public tables."""
    conn = _connect(creds)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]

        schema = {}
        for table in tables:
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table,))
            schema[table] = cur.fetchall()

        cur.close()
        return schema
    finally:
        conn.close()


def execute_query(creds, sql):
    """Execute a SQL query and return (columns, rows). Capped at 500 rows."""
    conn = _connect(creds)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchmany(500)
        cur.close()
        return columns, rows
    finally:
        conn.close()
