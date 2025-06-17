import pandas as pd
import json
import os

from utils.connections_utils import get_connection


def export_enriched_subcategories(output_path="subcategory.json"):
    """
    Export enriched subcategory data to a nested JSON format
    """
    conn = get_connection()

    try:
        # Load subcategory table
        subcategory_df = pd.read_sql("SELECT * FROM subcategory;", conn)

        # --- Top Authors ---
        query = """
            SELECT 
                s.id AS subcategory_id,
                a.name AS author_name,
                COUNT(*) AS paper_count
            FROM paper_author pa
            JOIN paper p ON pa.paper_id = p.id
            JOIN subcategory s ON p.subcategory = s.id
            JOIN author a ON pa.author_id = a.id
            GROUP BY s.id, a.name
        """

        df = pd.read_sql(query, conn)

        # Get top-10 authors per subcategory
        top_authors_df = (
            df.sort_values(['subcategory_id', 'paper_count'], ascending=[True, False])
            .groupby('subcategory_id')
            .apply(lambda x: [{'name': name, 'count': int(count)} 
                            for name, count in zip(x['author_name'], x['paper_count'])][:10])
            .reset_index(name='top_authors')
        )


        # --- Top Words ---
        word_query = """
            SELECT s.id AS subcategory_id, w.word,
                   COUNT(DISTINCT pw.paper_id) AS doc_count,
                   SUM(pw.tf_idf) AS tfidf_sum
            FROM paper p
            JOIN subcategory s ON p.subcategory = s.id
            JOIN paper_word_final pw ON p.id = pw.paper_id
            JOIN word w ON pw.word_id = w.id
            JOIN doc_freq df ON w.id = df.word_id
            WHERE df.df <= 100000
            GROUP BY s.id, w.word
        """
        word_df = pd.read_sql(word_query, conn)
        word_df["importance"] = word_df["doc_count"] * word_df["tfidf_sum"]

        top_words_df = (
            word_df
            .sort_values(['subcategory_id', 'importance'], ascending=[True, False])
            .groupby('subcategory_id')
            .apply(lambda group: group['word'].head(10).tolist())
            .reset_index(name="top_words")
        )

    finally:
        conn.close()

    # --- Merge DataFrames ---
    enriched_df = (
        subcategory_df
        .merge(top_authors_df, how="left", left_on="id", right_on="subcategory_id")
        .merge(top_words_df, how="left", left_on="id", right_on="subcategory_id")
        .drop(columns=["subcategory_id"], errors="ignore")
    )

    # --- Convert to Nested Dict Format ---
    enriched_dict = {
        row["id"]: {
            **{k: row[k] for k in subcategory_df.columns if k != "id"},
            "top_authors": row.get("top_authors", []),
            "top_words": row.get("top_words", [])
        }
        for _, row in enriched_df.iterrows()
    }

    # --- Export to JSON ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported enriched subcategory data to '{output_path}'")


def export_enriched_categories(output_path="category.json"):
    """
    Export enriched category data to a nested JSON format.
    """
    conn = get_connection()

    try:
        # Load base category table
        category_df = pd.read_sql("SELECT * FROM category;", conn)

        # --- Top Authors ---
        query = """
            SELECT 
                c.id AS category_id,
                a.name AS author_name,
                COUNT(*) AS paper_count
            FROM paper_author pa
            JOIN paper p ON pa.paper_id = p.id
            JOIN subcategory s ON p.subcategory = s.id
            JOIN category c ON s.category = c.id
            JOIN author a ON pa.author_id = a.id
            GROUP BY c.id, a.name
        """

        df = pd.read_sql(query, conn)

        # Get top-10 authors per category as list of dicts
        top_authors_df = (
            df.sort_values(['category_id', 'paper_count'], ascending=[True, False])
            .groupby('category_id')
            .apply(lambda x: [{'name': name, 'count': int(count)} 
                            for name, count in zip(x['author_name'], x['paper_count'])][:10])
            .reset_index(name='top_authors')
        )


        # --- Top Words ---
        word_query = """
            SELECT c.id AS category_id, w.word,
                   COUNT(DISTINCT pw.paper_id) AS doc_count,
                   SUM(pw.tf_idf) AS tfidf_sum
            FROM paper p
            JOIN subcategory s ON p.subcategory = s.id
            JOIN category c ON s.category = c.id
            JOIN paper_word_final pw ON p.id = pw.paper_id
            JOIN word w ON pw.word_id = w.id
            JOIN doc_freq df ON w.id = df.word_id
            WHERE df.df <= 100000
            GROUP BY c.id, w.word
        """
        word_df = pd.read_sql(word_query, conn)
        word_df["importance"] = word_df["doc_count"] * word_df["tfidf_sum"]

        top_words_df = (
            word_df
            .sort_values(['category_id', 'importance'], ascending=[True, False])
            .groupby('category_id')
            .apply(lambda group: group['word'].head(10).tolist())
            .reset_index(name="top_words")
        )

    finally:
        conn.close()

    # --- Merge Enriched Data ---
    enriched_df = (
        category_df
        .merge(top_authors_df, how="left", left_on="id", right_on="category_id")
        .merge(top_words_df, how="left", left_on="id", right_on="category_id")
        .drop(columns=["category_id"], errors="ignore")
    )

    # --- Convert to Nested Dict ---
    enriched_dict = {
        row["id"]: {
            **{k: row[k] for k in category_df.columns if k != "id"},
            "top_authors": row.get("top_authors", []),
            "top_words": row.get("top_words", [])
        }
        for _, row in enriched_df.iterrows()
    }

    # --- Save to JSON ---
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported enriched category data to '{output_path}'")


def save_dataframe_in_chunks(df, output_dir="output_chunks", chunk_size=250_000):
    os.makedirs(output_dir, exist_ok=True)

    total_rows = len(df)
    num_chunks = (total_rows + chunk_size - 1) // chunk_size  # Ceiling division

    for i in range(num_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, total_rows)
        chunk_df = df.iloc[start:end]

        chunk_filename = os.path.join(output_dir, f"chunk_{i + 1}.parquet")
        chunk_df.to_parquet(chunk_filename, index=False, compression="snappy")
        print(f"✅ Saved rows {start} to {end - 1} into {chunk_filename}")


def export_full_paper_dataset(output_dir="papers", chunk_size=250_000):
    conn = get_connection()

    try:
        # Fetch basic paper info + subcategory/category
        paper_query = """
            SELECT p.id, p.title, p.published_year AS year, p.dim1, p.dim2,
                   p.summary, p.subcategory, sc.category
            FROM paper p
            JOIN subcategory sc ON p.subcategory = sc.id
            JOIN category c ON sc.category = c.id;
        """
        paper_df = pd.read_sql(paper_query, conn)

        # Fetch authors per paper
        author_query = """
            SELECT pa.paper_id, a.name AS author
            FROM paper_author pa
            JOIN author a ON pa.author_id = a.id;
        """
        author_df = pd.read_sql(author_query, conn)
        authors_grouped = (
            author_df.groupby('paper_id')['author']
            .apply(list)
            .reset_index(name='authors')
        )

        # Fetch top 10 words per paper based on tf-idf (already ordered)
        word_query = """
            SELECT pwr.paper_id, w.word, pwr.tf_idf
            FROM paper_word_final pwr
            JOIN word w ON pwr.word_id = w.id
            ORDER BY pwr.paper_id, pwr.tf_idf DESC;
        """
        word_df = pd.read_sql(word_query, conn)

        # Limit to top 10 words per paper
        word_df['rank'] = word_df.groupby('paper_id').cumcount()
        top_words_df = (
            word_df[word_df['rank'] < 10]
            .groupby('paper_id')['word']
            .apply(list)
            .reset_index(name='words')
        )

    finally:
        conn.close()

    # Merge all together
    merged_df = (
        paper_df
        .merge(authors_grouped, left_on='id', right_on='paper_id', how='left')
        .merge(top_words_df, left_on='id', right_on='paper_id', how='left')
        .drop(columns=['paper_id_x', 'paper_id_y'], errors='ignore')
    )
    print(f"ℹ️ Merged dataset with {len(merged_df)} rows. Saving in chunks of {chunk_size}...")

    # Save in chunks
    save_dataframe_in_chunks(merged_df, output_dir=output_dir, chunk_size=chunk_size)
    print(f"✅ Done! {len(merged_df)} papers saved to '{output_dir}' in .parquet chunks.")

# export_enriched_categories()
# export_enriched_subcategories()
# export_full_paper_dataset()

def export_top_words_flat(output_path="words_flat.parquet"):
    conn = get_connection()

    try:
        query = """
            SELECT paper_id, word, tf_idf
            FROM (
                SELECT 
                    pw.paper_id,
                    w.word,
                    pw.tf_idf,
                    ROW_NUMBER() OVER (PARTITION BY pw.paper_id ORDER BY pw.tf_idf DESC) AS rank
                FROM paper_word_final pw
                JOIN word w ON pw.word_id = w.id
            ) AS ranked
            WHERE rank <= 10
        """
        df = pd.read_sql(query, conn)

    finally:
        conn.close()

    # Save in flat table format
    df.to_parquet(output_path, index=False, compression="snappy")
    print(f"✅ Exported flat top-10 words per paper to '{output_path}'")

if __name__ == "__main__":
    export_top_words_flat()
