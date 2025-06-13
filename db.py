import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        return psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
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