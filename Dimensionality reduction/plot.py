import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
df = pd.read_parquet("UMAP_ALL.parquet")

categories = pd.read_parquet("points_with_category.parquet")
categories = categories['category']

df = pd.concat([df, categories], axis=1)

# Define custom color map
color_map = {
    'econ': '#636EFA',     # Plotly blue
    'physic': "#7E7E7E",  # Plotly red
    'q-fin': '#FFA15A',    # Plotly green
    'cs': '#AB63FA',       # Plotly purple
    'q-bio': "#00AC7E",    # Plotly orange
    'stat': '#FF6692',     # Plotly cyan
    'eess': '#19D3F3',     # Plotly pink
    'math': '#EF553B'      # Plotly light green
}
fig = px.scatter(
    df,
    x='UMAP1',
    y='UMAP2',
    color='category',
    color_discrete_map=color_map,
    opacity=0.3,
    width=1000,
    height=1000
)

fig.update_traces(marker=dict(size=2.5))

# Update axis labels with larger font and remove title/legend
fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    title=None,
    showlegend=False
)

fig.show()



# # File names mapped to subplot titles
# files_and_titles = [
#     ("UMAP.parquet", "UMAP"),
#     ("PCA.parquet", "PCA"),
#     ("MDS.parquet", "MDS"),
#     ("TSNE.parquet", "t-SNE")
# ]

# # Define custom color map
# color_map = {
#     'econ': '#636EFA',
#     'physics': "#949494",
#     'q-fin': '#FFA15A',
#     'cs': '#AB63FA',
#     'q-bio': "#3BCA7B",
#     'stat': '#FF6692',
#     'eess': '#19D3F3',
#     'math': '#EF553B'
# }

# # Create 2x2 subplot layout
# fig = make_subplots(
#     rows=2,
#     cols=2,
#     subplot_titles=[f"<b>{title}</b>" for _, title in files_and_titles],
#     horizontal_spacing=0.05,  # default is 0.2
#     vertical_spacing=0.07     # default is 0.3
# )

# # Loop through files and add each to a subplot
# for i, (file, title) in enumerate(files_and_titles):
#     df = pd.read_parquet(file)
#     row, col = divmod(i, 2)
#     row += 1
#     col += 1

#     for category in df['category'].unique():
#         df_cat = df[df['category'] == category]
#         fig.add_trace(
#             go.Scattergl(
#                 x=df_cat['dim_1'],
#                 y=df_cat['dim_2'],
#                 mode='markers',
#                 name=category,
#                 marker=dict(color=color_map.get(category, "#CCCCCC"), size=3.5),
#                 showlegend=(i == 0)  # Show legend only once
#             ),
#             row=row,
#             col=col
#         )

# # Update layout
# fig.update_layout(
#     width=1000,
#     height=1000,
#     title_text=None,
#     showlegend=True,
#     font=dict(size=12, family="Arial", color="black"),  # optional styling
#     legend=dict(font=dict(size=14))


# )

# # Remove axis titles and ticks for clarity
# fig.update_xaxes(title_text=None, showticklabels=False)
# fig.update_yaxes(title_text=None, showticklabels=False)

# fig.show()

# opacity_map = {
#     'econ': 0.5,
#     'physic': 0.2,
#     'q-fin': 0.5,
#     'cs': 0.4,
#     'q-bio': 0.5,
#     'stat': 0.5,
#     'eess': 0.5,
#     'math': 0.1
# }

# # Filter valid categories
# df = df[df['category'].isin(color_map.keys())]

# # Create the figure with individual traces per category
# fig = go.Figure()

# for category in color_map:
#     df_cat = df[df['category'] == category]
#     fig.add_trace(go.Scattergl(
#         x=df_cat['UMAP1'],
#         y=df_cat['UMAP2'],
#         mode='markers',
#         name=category,
#         marker=dict(
#             color=color_map[category],
#             size=3,
#             opacity=opacity_map[category]
#         ),
#         showlegend=False  # Optional: suppress legend
#     ))


# # Update axis labels with larger font and remove title/legend
# fig.update_layout(
#     width=1000,
#     height=1000,
#     xaxis_title=None,
#     yaxis_title=None,
#     title=None,
#     showlegend=False
# )

# fig.show()




from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Set common axes range for consistency
x_range = [df['UMAP1'].min(), df['UMAP1'].max()]
y_range = [df['UMAP2'].min(), df['UMAP2'].max()]

# Categories in fixed order
categories = list(color_map.keys())

# Create 2x4 subplot grid with tighter spacing
fig = make_subplots(
    rows=2, cols=4,
    subplot_titles=categories,
    horizontal_spacing=0.03,  # tighter horizontal spacing
    vertical_spacing=0.08     # tighter vertical spacing
)

for idx, category in enumerate(categories):
    row = idx // 4 + 1
    col = idx % 4 + 1
    sub_df = df[df['category'] == category]

    fig.add_trace(
        go.Scattergl(
            x=sub_df['UMAP1'],
            y=sub_df['UMAP2'],
            mode='markers',
            marker=dict(color=color_map[category], size=2.5, opacity=0.3),
            name=category,
            showlegend=False
        ),
        row=row, col=col
    )

    fig.update_xaxes(range=x_range, row=row, col=col)
    fig.update_yaxes(range=y_range, row=row, col=col)

# Larger overall figure and tighter margins
fig.update_layout(
    height=900,
    width=1600,
    title_text=None,
    margin=dict(t=40, l=20, r=20, b=20)
)



# Update subplot titles font style (bold and bigger)
for annotation in fig['layout']['annotations']:
    annotation['font'] = dict(size=18, family='Arial, sans-serif', color='black', weight='bold')
    annotation['font']['family'] = 'Arial Black, Arial, sans-serif'
    annotation['text'] = f"<b>{annotation['text']}</b>"  # Optional: force bold with HTML

fig.show()


