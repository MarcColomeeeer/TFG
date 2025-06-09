from preprocessing_utils import extract_token_frequencies

def populate_categories(conn, df):
    """
    Populate the 'category' table in the database using values from a DataFrame.
    Columns expected: id, name.
    """
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO category (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (row['id'], row['name']))
    
    conn.commit()
    cur.close()


def populate_subcategories(conn, df):
    """
    Populate the 'subcategory' table, linking to existing 'category' rows.
    Columns expected: id, name, category_id.
    """
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO subcategory (id, name, category)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (row['id'], row['name'], row['category_id']))
    
    conn.commit()
    cur.close()


def populate_papers(df, conn):
    """
    Populate the 'paper' table with metadata from arXiv.
    Columns expected: arxiv_id, title, year, summary, dim1, dim2, category.
    """
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO paper (ID, title, published_year, summary, dim1, dim2, subcategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT (ID) DO NOTHING
        """, (row["arxiv_id"], row["title"], row["year"], row["summary"], row['dim1'], row['dim2'], row["category"]))

    conn.commit()
    cur.close()


def populate_authors(df, conn):
    """
    Populate the 'author' table and create links in 'paper_author'.
    Columns expected: arxiv_id, authors.
    """
    cur = conn.cursor()

    cur.execute("SELECT ID, name FROM author;")
    rows = cur.fetchall()
    
    existing_authors = {name: id_ for id_, name in rows}
    max_id = max(existing_authors.values()) if existing_authors else 0
    next_id = max_id + 1

    paper_author_links = []
    new_authors = []

    for _, row in df.iterrows():
        paper_id = row["arxiv_id"]
        for name in row["authors"].split(','):
            name = name.strip()
            if name not in existing_authors:
                existing_authors[name] = next_id
                new_authors.append((next_id, name))
                next_id += 1
            paper_author_links.append((paper_id, existing_authors[name]))

    cur.executemany("INSERT INTO author (id, name) VALUES (%s, %s) ON CONFLICT DO NOTHING;", new_authors)
    cur.executemany("INSERT INTO paper_author (paper_id, author_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;", paper_author_links)
    
    conn.commit()
    cur.close()


def populate_words(df, conn):
    """
    Populate the 'word' table and link words to papers using token frequencies.
    Assumes all rows in the dataframe belong to the same top-level category.
    """
    cur = conn.cursor()
    
    cur.execute("SELECT id, word FROM word;")
    rows = cur.fetchall()

    existing_words = {word: id_ for id_, word in rows}
    max_id = max(existing_words.values()) if existing_words else 0
    next_id = max_id + 1

    new_words = []
    paper_word_links = []

    for _, row in df.iterrows():
        paper_id = row["arxiv_id"]
        token_freqs = extract_token_frequencies(row["pdf_content"])

        for word, count in token_freqs.items():
            if word not in existing_words:
                existing_words[word] = next_id
                new_words.append((next_id, word))
                next_id += 1
            paper_word_links.append((paper_id, existing_words[word], int(count), None))  # tf_idf is None

    cur.executemany("INSERT INTO word (id, word) VALUES (%s, %s) ON CONFLICT DO NOTHING;", new_words)

    cur.executemany(
        f"""
        INSERT INTO paper_word (paper_id, word_id, count, tf_idf)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        paper_word_links
    )

    conn.commit()
    cur.close()


def populate_all_tables(conn, df):
    """
    Populates all core content tables in the database using a single DataFrame.

    This function inserts data into the following tables:
    - paper
    - author (and paper_author relationship table)
    - word (and paper_word relationship table)

    Columns expected: arxiv_id, title, authors, year, category, summary, pdf_content, dim1, dim2.
    """
    print("Populating papers...")
    populate_papers(df, conn)
    print("Papers Populated.")
    
    print("Populating authors...")
    populate_authors(df, conn)
    print("Authors Populated.")
    
    print("Populating words...")
    populate_words(df, conn)
    print("Words Populated.")
