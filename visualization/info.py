import pandas as pd
import itertools
import numpy as np
import ast
import heapq
from collections import defaultdict


# Load real data
df = pd.read_parquet("visualization.parquet")
df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(0).astype(int)
df['author'] = df['author'].apply(lambda x: [author.strip() for author in x.split(',')])
df['words'] = df['words'].apply(ast.literal_eval)

df_points = pd.read_parquet("UMAP.parquet")

df['dim_1'] = df_points['dim_1']
df['dim_2'] = df_points['dim_2']


word_heaps = defaultdict(list)
unique_words = set()

for arxiv_id, word_tfidf_list in zip(df['arxiv_id'], df['words']):
    for word, tfidf in word_tfidf_list:
        unique_words.add(word)
        heapq.heappush(word_heaps[word], (tfidf, arxiv_id))
        if len(word_heaps[word]) > 10:
            heapq.heappop(word_heaps[word])

word_paper = {
    word: [arxiv_id for _, arxiv_id in sorted(heap, reverse=True)]
    for word, heap in word_heaps.items()
}

unique_authors = sorted(set(itertools.chain(*df['author'].tolist())))


category_labels = {
    'cs': 'Computer Science',
    'q-bio': 'Quantitative Biology',
    'q-fin': 'Quantitative Finance',
    'stat': 'Statistics',
    'econ': 'Economics',
    'eess': 'Elec. Eng. & Sys. Sci.',
    'math': 'Mathematics',
    'physics': 'Physics'
}

color_map = {
    'econ': '#636EFA',     # Plotly blue
    'physics': "#7E7E7E",  # Plotly red
    'q-fin': '#FFA15A',    # Plotly green
    'cs': '#AB63FA',       # Plotly purple
    'q-bio': "#00AC7E",    # Plotly orange
    'stat': '#FF6692',     # Plotly cyan
    'eess': '#19D3F3',     # Plotly pink
    'math': '#EF553B'      # Plotly light green
}

# color_map = {
#     'econ': '#636EFA',     # Plotly blue
#     'physics': "#949494",  # Plotly red
#     'q-fin': '#FFA15A',    # Plotly green
#     'cs': '#AB63FA',       # Plotly purple
#     'q-bio': '#00CC96',    # Plotly orange
#     'stat': '#FF6692',     # Plotly cyan
#     'eess': '#19D3F3',     # Plotly pink
#     'math': '#EF553B'      # Plotly light green
# }


# PRECOMPUTE centroids and radius per category ONCE at startup
centroids_and_radii = {}
for cat in df['category'].unique():
    cat_df = df[df['category'] == cat]
    if cat_df.empty:
        continue
    centroid_x = cat_df['dim_1'].median()
    centroid_y = cat_df['dim_2'].median()
    distances = np.sqrt((cat_df['dim_1'] - centroid_x)**2 + (cat_df['dim_2'] - centroid_y)**2)
    radius = np.median(distances)

    centroids_and_radii[cat] = (centroid_x, centroid_y, radius)



import json

with open('data/categories.json', 'r') as f:
    categories_info = json.load(f)


with open('data/subcategories.json', 'r') as f:
    subcategories_info = json.load(f)