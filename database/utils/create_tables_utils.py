def create_category_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id VARCHAR PRIMARY KEY,
            name VARCHAR
        );
    """)
    conn.commit()
    cur.close()


def create_subcategory_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subcategory (
            id VARCHAR PRIMARY KEY,
            name VARCHAR,
            category VARCHAR NOT NULL,
            FOREIGN KEY (category) REFERENCES category(id)
        );
    """)
    conn.commit()
    cur.close()


def create_paper_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paper (
            id VARCHAR PRIMARY KEY,
            title VARCHAR,
            published_year INTEGER,
            summary TEXT,
            dim1 FLOAT,
            dim2 FLOAT,
            subcategory VARCHAR NOT NULL,
            FOREIGN KEY (subcategory) REFERENCES subcategory(id)
        );
    """)
    conn.commit()
    cur.close()


def create_author_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY,
            name VARCHAR
        );
    """)
    conn.commit()
    cur.close()


def create_word_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS word (
            id INTEGER PRIMARY KEY,
            word VARCHAR
        );
    """)
    conn.commit()
    cur.close()


def create_paper_author_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paper_author (
            paper_id VARCHAR,
            author_id INTEGER,
            PRIMARY KEY (paper_id, author_id),
            FOREIGN KEY (paper_id) REFERENCES paper(id),
            FOREIGN KEY (author_id) REFERENCES author(id)
        );
    """)
    conn.commit()
    cur.close()


def create_paper_word_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paper_word (
            paper_id VARCHAR,
            word_id INTEGER,
            tf_idf FLOAT,
            PRIMARY KEY (paper_id, word_id),
            FOREIGN KEY (paper_id) REFERENCES paper(id),
            FOREIGN KEY (word_id) REFERENCES word(id)
        );
    """)
    conn.commit()
    cur.close()


def create_document_frequency_table(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS document_frequency (
            word_id INTEGER PRIMARY KEY,
            df INTEGER,
            FOREIGN KEY (word_id) REFERENCES word(id)
        );
    """)
    conn.commit()
    cur.close()


def create_all_tables(conn):
    """
    Calls all table creation functions to create the necessary tables in the database.
    """
    create_category_table(conn)
    create_subcategory_table(conn)
    create_paper_table(conn)
    create_author_table(conn)
    create_word_table(conn)
    create_paper_author_table(conn)
    create_paper_word_table(conn)
    create_document_frequency_table(conn)
