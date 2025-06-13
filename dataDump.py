import psycopg2
import data_cleaning
import json

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


def schema_creation(conn, curr):
    curr.execute(""" 
        CREATE TABLE IF NOT EXISTS stores (
        store_id UUID PRIMARY KEY
        )             
    """)

    curr.execute("""
        CREATE TABLE IF NOT EXISTS timezones (
        store_id UUID PRIMARY KEY,
        schedule JSONB,
        FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE
        )
    """)

    curr.execute("""
        CREATE TABLE IF NOT EXISTS menu_hours (
        store_id UUID PRIMARY KEY,
        schedule JSONB,
        FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE
        )
    """)

    curr.execute("""
        CREATE TABLE IF NOT EXISTS store_status (
        store_id UUID PRIMARY KEY,
        schedule JSONB,
        FOREIGN KEY (store_id) REFERENCES stores(store_id) ON DELETE CASCADE
        )
    """)

    conn.commit() 

def data_send(conn,curr,map,table_name):

    for store_id in map:
        curr.execute("""
            INSERT INTO stores (store_id)
            VALUES (%s)
            ON CONFLICT DO NOTHING
    """, (store_id,))

    for store_id, schedule in map.items():
        curr.execute(f"""
            INSERT INTO {table_name} (store_id, schedule)
            VALUES (%s, %s)
            ON CONFLICT (store_id)
            DO UPDATE SET schedule = EXCLUDED.schedule
        """, (store_id, json.dumps(schedule)))
    
    conn.commit()


def data_dump(timezones,menu_hours,store_status):
    conn = get_connection()
    curr = conn.cursor()
    schema_creation(conn,curr)
    data_send(conn,curr,timezones,table_name="timezones")
    data_send(conn,curr,menu_hours,table_name="menu_hours")
    data_send(conn,curr,store_status,table_name="store_status")
    conn.commit()
    curr.close()
    conn.close()

    
    
timezones,menu_hours,store_status = data_cleaning.data_cleaning()
print(len(timezones))
print(len(menu_hours))
print(len(store_status))
data_dump(timezones,menu_hours,store_status)