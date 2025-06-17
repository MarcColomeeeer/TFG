# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd

# # # Define the updated confusion matrix as a pandas DataFrame for easier labeling
# # conf_matrix = pd.DataFrame([
# #     [237, 0,   1,   0,   1,   1,   0,  10,  0,  0,  0],
# #     [1,   218, 1,   0,   0,   0,   0,  27,  2,  0,  1],
# #     [0,   1,   180, 8,   30,  0,   6,  13,  2,  2,  8],
# #     [0,   0,   2,   230, 0,   0,   3,  1,   0, 10, 4],
# #     [0,   0,   5,   0,   243, 0,   0,  1,   1,  0, 0],
# #     [4,   3,   0,   0,   0,   233, 1,  9,   0,  0, 0],
# #     [0,   0,   10,  0,   2,   0,   218, 7,  0,  2, 11],
# #     [8,   27,  5,   2,   7,   12,  3,  169,11, 2,  4],
# #     [0,   1,   7,   1,   3,   0,   3,  5,  225, 0, 5],
# #     [0,   1,   2,   28,  1,   1,   2,  4,  0, 207,4],
# #     [0,   0,   9,   7,   10,  0,   4,  2,  5,  1, 212]
# # ],
# # columns=['astro-ph', 'cond-mat', 'cs', 'econ', 'eess', 'hep', 'math', 'physics', 'q-bio', 'q-fin', 'stat'],
# # index=['astro-ph', 'cond-mat', 'cs', 'econ', 'eess', 'hep', 'math', 'physics', 'q-bio', 'q-fin', 'stat']
# # )

# # # New confusion matrix data
# # conf_matrix = pd.DataFrame([
# #     [187, 8, 30, 7, 6, 2, 2, 8],
# #     [2, 230, 0, 3, 1, 0, 10, 4],
# #     [5, 0, 243, 0, 1, 1, 0, 0],
# #     [10, 0, 2, 219, 4, 2, 2, 11],
# #     [6, 0, 2, 7, 213, 17, 0, 5],
# #     [8, 1, 3, 4, 2, 227, 0, 5],
# #     [2, 28, 1, 2, 4, 0, 209, 4],
# #     [9, 7, 10, 4, 2, 5, 1, 212]
# # ],

# # Updated confusion matrix
# conf_matrix = pd.DataFrame([
#     [187, 8, 29, 6, 8, 2, 2, 8],
#     [2, 230, 0, 3, 1, 0, 11, 3],
#     [4, 1, 243, 0, 1, 1, 0, 0],
#     [9, 0, 3, 219, 4, 2, 2, 11],
#     [5, 0, 3, 7, 214, 16, 0, 5],
#     [7, 1, 3, 2, 2, 229, 0, 6],
#     [2, 29, 1, 2, 4, 0, 208, 4],
#     [9, 7, 10, 4, 2, 4, 1, 213]
# ],

# columns=['cs', 'econ', 'eess', 'math', 'physics', 'q-bio', 'q-fin', 'stat'],
# index=['cs', 'econ', 'eess', 'math', 'physics', 'q-bio', 'q-fin', 'stat'])

# # Plot the confusion matrix
# plt.figure(figsize=(12, 10))
# ax = sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", square=True,
#             xticklabels=conf_matrix.columns, yticklabels=conf_matrix.index,
#             annot_kws={"size": 14})  # <-- Add this line


# # Increase font size for axis labels and ticks
# ax.set_xlabel("Predicted Label", fontsize=16)
# ax.set_ylabel("True Label", fontsize=16)

# ax.tick_params(axis='x', labelrotation=45, labelsize=14)
# # ax.tick_params(axis='y', labelrotation=0, labelsize=14)


# # plt.tight_layout()

# # # Save the figure
# # plt.savefig("confusion_matrix_final.png", dpi=300)
# # plt.close()

# # print("Confusion matrix saved as 'confusion_matrix_8_categories.png'.")

# import pandas as pd
# import plotly.graph_objects as go

# # Load CSV
# df = pd.read_csv("paper_counts.csv")

# # Colors for each field
# color_map = {
#     'econ': '#636EFA',     # Plotly blue
#     'physics': "#7E7E7E",  # Plotly red
#     'q-fin': '#FFA15A',    # Plotly green
#     'cs': '#AB63FA',       # Plotly purple
#     'q-bio': "#00AC7E",    # Plotly orange
#     'stat': '#FF6692',     # Plotly cyan
#     'eess': '#19D3F3',     # Plotly pink
#     'math': '#EF553B'      # Plotly light green
# }

# # Create plotly figure
# fig = go.Figure()

# # Add a line for each column (except 'YEAR')
# for column in df.columns[1:]:
#     fig.add_trace(go.Scatter(
#         x=df['YEAR'],
#         y=df[column],
#         mode='lines',
#         name=column,
#         line=dict(color=color_map.get(column, '#000000'))  # fallback color
#     ))

# # Update layout
# fig.update_layout(
#     title=None,
#     xaxis_title="Year",
#     yaxis_title="Number of Papers Publications",
#     template="plotly_white",
#     width=800,
#     height=500
# )

import plotly.express as px
import pandas as pd

# Direct counts and categories
counts = [341595, 261221, 9522, 605841, 27012, 30707, 6766, 48616]
categories = ['math', 'stat', 'q-fin', 'physics', 'q-bio', 'cs', 'econ', 'eess']

# Create DataFrame and sort ascending by total_count
df = pd.DataFrame({'category': categories, 'total_count': counts})
df = df.sort_values(by='total_count', ascending=True)

# Color map
color_map = {
    'econ': '#636EFA',
    'physics': "#7E7E7E",
    'q-fin': '#FFA15A',
    'cs': '#AB63FA',
    'q-bio': "#00AC7E",
    'stat': '#FF6692',
    'eess': '#19D3F3',
    'math': '#EF553B'
}

# Create vertical bar plot
fig = px.bar(
    df,
    x='category',
    y='total_count',
    color='category',
    color_discrete_map=color_map,
    labels={'total_count': 'Total Papers', 'category': 'Category'},
    height=500,
    width=700
)

fig.update_layout(
    title=None,
    template="plotly_white",
    showlegend=False,  # Hide legend
    xaxis_title='Category',
    yaxis_title='Total Papers'
)

fig.show()



# # Load CSV
# df = pd.read_csv("paper_counts.csv")

# # Define color map
# color_map = {
#     'econ': '#636EFA',     # Plotly blue
#     'physics': "#7E7E7E",  # Plotly red
#     'q-fin': '#FFA15A',    # Plotly green
#     'cs': '#AB63FA',       # Plotly purple
#     'q-bio': "#00AC7E",    # Plotly orange
#     'stat': '#FF6692',     # Plotly cyan
#     'eess': '#19D3F3',     # Plotly pink
#     'math': '#EF553B'      # Plotly light green
# }

# # Compute total papers per category and sort
# totals = df.drop(columns=['YEAR']).sum().sort_values(ascending=True)

# # Create bar chart
# fig = go.Figure()

# for field in totals.index:
#     fig.add_trace(go.Bar(
#         x=[field],
#         y=[totals[field]],
#         name=field,
#         marker_color=color_map.get(field, '#000000')
#     ))

# # Update layout
# fig.update_layout(
#     title=None,
#     xaxis_title="Category",
#     yaxis_title="Total Papers",
#     template="plotly_white",
#     width=700,
#     height=450,
#     showlegend=False
# )

# fig.show()


# import plotly.graph_objects as go

# # Data
# umap_x = [15, 30, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
# umap_y = [0.6615, 0.6671, 0.669, 0.6702, 0.6705, 0.6712, 0.6711, 0.6697, 0.6714, 0.6711, 0.6714, 0.6754, 0.6709, 0.6718]

# tsne_x = [15, 30, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600]
# tsne_y = [0.6443, 0.6488, 0.6519, 0.6618, 0.678, 0.6777, 0.6788, 0.6898, 0.6913, 0.6879,
#           0.6973, 0.6897, 0.6966, 0.6956, 0.7045, 0.6989, 0.7028, 0.6969, 0.693]

# # Create figure
# fig = go.Figure()

# fig.add_trace(go.Scatter(
#     x=umap_x, y=umap_y,
#     mode='lines+markers',
#     name='UMAP',
#     line=dict(color='blue'),
#     marker=dict(size=6)
# ))

# fig.add_trace(go.Scatter(
#     x=tsne_x, y=tsne_y,
#     mode='lines+markers',
#     name='T-SNE',
#     line=dict(color='red'),
#     marker=dict(size=6)
# ))

# # Layout
# fig.update_layout(
#     title=None,
#     xaxis_title="Number of Neighbors / Perplexity",
#     yaxis_title="QNN AUC",
#     legend=dict(title='Method'),
#     template='plotly_white',
#     height=500,
#     width=800
# )

# fig.show()
