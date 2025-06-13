import psycopg2

def get_connection():
    try:
        return psycopg2.connect(
            database="loopAI",
            user="postgres",
            password="prakhar",
            host="127.0.0.1",
            port=5432,
        )
    except:
        return False
    
def report_schema(conn,curr):
    conn = get_connection()
    curr = conn.cursor()

    curr.execute(""" 
        CREATE TABLE IF NOT EXISTS reports (
        report_id UUID PRIMARY KEY,
        available BOOLEAN NOT NULL
        )             
    """)

    curr.execute("""
        CREATE TABLE IF NOT EXISTS report_data (
        report_id UUID PRIMARY KEY,
        schedule JSONB,
        FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
        )
    """)

    conn.commit()

conn = get_connection()
curr = conn.cursor()
report_schema(conn,curr)

curr.close()
conn.close()