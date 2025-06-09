import psycopg2

def get_connection():
    return psycopg2.connect(
        database="documents",
        user="postgres",
        password="255825",
        host="localhost",
        port="5432"
    )
