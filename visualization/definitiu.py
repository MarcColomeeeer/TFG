import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output, ALL, State
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

import plotly.io as pio
pio.templates.default = "plotly"


from info import centroids_and_radii, color_map, df, unique_authors, unique_words, categories_info, subcategories_info, word_paper
from layout import layout
from utils import make_button, format_authors, make_colored_label, make_inline_button_list, build_line_plot, get_panel_style

df_counts = df.groupby(['year', 'category']).size().reset_index(name='count')

app = dash.Dash(__name__)

app.layout = layout

#################################################
# MAIN PLOT
#################################################

@app.callback(
    Output('main-plot', 'figure'),
    [
        Input('year-range-slider', 'value'),
        Input('category-selector', 'value'),
        Input('toggle-centroids-btn', 'value'),
        Input('toggle-points-btn', 'value'),
        Input('author-selector', 'value'),
        Input('highlight-category-checklist', 'value'),
        Input('highlight-subcategory-checklist', 'value'),
        Input('selected-category-store', 'data'),
        Input('selected-subcategory-store', 'data'),
        Input('highlight-paper-checklist', 'value'),
        Input('main-plot', 'clickData'),

    ]
)
def update_plot(selected_range, selected_categories, show_centroids, show_points, selected_author, highlight_category_value, highlight_subcategory_value, category_value, subcategory_value, highlight_paper_value, clickData):

    # Filter by year
    filtered_df = df[
        (df['year'] >= selected_range[0]) & 
        (df['year'] <= selected_range[1])
    ]

    # Filter by selected categories
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    # Determine highlight mode
    highlight_by_paper = 'highlight' in (highlight_paper_value or [])
    highlight_by_category = 'highlight' in (highlight_category_value or [])
    highlight_by_subcategory = 'highlight' in (highlight_subcategory_value or [])

    highlight_category = category_value
    highlight_subcategory = subcategory_value

    highlighted_df = pd.DataFrame(columns=filtered_df.columns)
    dimmed_df = filtered_df  # default everything dimmed

    # Check for paper highlighting first
    if highlight_by_paper and clickData:
        point = clickData['points'][0]
        customdata = point.get('customdata', [])
        arxiv_id = (customdata + ['N/A'] * 6)[3]  # index 3 = arxiv_id
        highlighted_df = filtered_df[filtered_df['arxiv_id'] == arxiv_id]
        dimmed_df = filtered_df[filtered_df['arxiv_id'] != arxiv_id]

    elif highlight_by_subcategory:
        highlighted_df = filtered_df[filtered_df['subcategory'] == highlight_subcategory]
        dimmed_df = filtered_df[filtered_df['subcategory'] != highlight_subcategory]

    elif highlight_by_category:
        highlighted_df = filtered_df[filtered_df['category'] == highlight_category]
        dimmed_df = filtered_df[filtered_df['category'] != highlight_category]

    elif selected_author:
        mask = filtered_df['author'].apply(lambda authors: selected_author in authors)
        highlighted_df = filtered_df[mask]
        dimmed_df = filtered_df[~mask]

    else:
        highlighted_df = filtered_df
        dimmed_df = pd.DataFrame(columns=filtered_df.columns)

    fig = go.Figure()

    def add_scatter_traces(dataframe, opacity, hover_enabled):
        if dataframe.empty:
            return
        if hover_enabled:
            # Use px.scatter for full hover info
            scatter = px.scatter(
                dataframe, x='dim_1', y='dim_2',
                hover_name='title',
                hover_data={k: False for k in ['dim_1', 'dim_2', 'category', 'year', 'author', 'arxiv_id', 'summary', 'subcategory', 'words']},
                custom_data=['category', 'year', 'author', 'arxiv_id', 'summary', 'subcategory', 'words'],
                color='category',
                color_discrete_map=color_map,
                opacity=opacity
            )
            for trace in scatter.data:
                trace.update(marker=dict(size=5))
                fig.add_trace(trace)
        else:
            # Build scatter trace manually for dimmed points with no hover
            fig.add_trace(go.Scatter(
                x=dataframe['dim_1'],
                y=dataframe['dim_2'],
                mode='markers',
                marker=dict(
                    color=[color_map[c] for c in dataframe['category']],
                    size=5,
                    opacity=opacity
                ),
                hoverinfo='skip'
            ))

    # Add scatter points
    if 'show' in show_points:
        add_scatter_traces(dimmed_df, 0.1, False)
        add_scatter_traces(highlighted_df, 1.0, True)

    # Add centroids
    if 'show' in show_centroids and selected_categories:
        for cat in selected_categories:
            if cat not in centroids_and_radii:
                continue
            cx, cy, radius = centroids_and_radii[cat]
            theta = np.linspace(0, 2 * np.pi, 100)
            circle_x = cx + radius * np.cos(theta)
            circle_y = cy + radius * np.sin(theta)

            fig.add_trace(go.Scatter(
                x=circle_x, y=circle_y,
                mode='lines',
                line=dict(color=color_map[cat], width=5),
                fill='toself',
                fillcolor=color_map[cat],
                opacity=0.2,
                showlegend=False,
                hoverinfo='skip'
            ))

            fig.add_trace(go.Scatter(
                x=[cx], y=[cy],
                mode='markers',
                marker=dict(size=20, color=color_map[cat]),
                showlegend=False,
                hoverinfo='text',
                text=[f"{categories_info.get(cat, {}).get('name', cat)} centroid"]
            ))

    # Axis padding
    x_min, x_max = df['dim_1'].min(), df['dim_1'].max()
    y_min, y_max = df['dim_2'].min(), df['dim_2'].max()
    x_pad = (x_max - x_min) * 0.01
    y_pad = (y_max - y_min) * 0.01

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[x_min - x_pad, x_max + x_pad]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[y_min - y_pad, y_max + y_pad]),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig


#################################################
# PAPERS PER CATEGORY PLOT
#################################################
@app.callback(
    Output('papers-per-year-plot', 'figure'),
    [
        Input('year-range-slider', 'value'),
        Input('category-selector', 'value'),
    ]
)
def update_bar_fig(selected_range, selected_categories):
    year_start, year_end = selected_range
    years = list(range(year_start, year_end + 1))

    data = {
        "year": [],
        "category": [],
        "count": []
    }

    for category_key in selected_categories:
        counts = categories_info[category_key]["counts"]
        for year in years:
            count = counts.get(str(year), 0)
            data["year"].append(year)
            data["category"].append(category_key)
            data["count"].append(count)

    df_counts = pd.DataFrame(data)

    fig = px.line(
        df_counts,
        x='year',
        y='count',
        color='category',
        color_discrete_map=color_map,
        labels={'count': 'Number of Papers', 'year': 'Year'},
        height=250,
        line_shape='spline',
        hover_data={'year': True, 'category': False, 'count': True}
    )

    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        legend=dict(visible=False),
        yaxis_title='',
        xaxis=dict(
            title='',
            tickformat='d',
            dtick=5,
            tickangle=-45,
            automargin=True
        )
    )

    fig.update_traces(hovertemplate='%{x} : %{y}<extra></extra>')

    return fig


#################################################
# PAPER PANEL
#################################################

@app.callback(
    Output('highlight-paper-checklist', 'value', allow_duplicate=True),
    Input('close-panel-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_highlight_category_checklist(_):
    return []


@app.callback(
    Output('info-panel', 'style'),
    Output('word-selector-panel', 'style'),
    Output('author-panel', 'style', allow_duplicate=True),  
    Input('main-plot', 'clickData'),
    Input('close-panel-btn', 'n_clicks'),
    Input('title-selector', 'value'),
    prevent_initial_call=True
)
def toggle_panels(clickData, n_close, selected_title):
    triggered_id = ctx.triggered_id

    shared_style = {
        'position': 'fixed',
        'top': '0',
        'right': '0',
        'width': '260px',
        'height': '100vh',
        'padding': '10px',
        'backgroundColor': "#ffffff",
        'overflowY': 'auto',
    }

    if triggered_id == 'close-panel-btn':
        # Closing info-panel: show word selector, hide author panel
        return {**shared_style, 'display': 'none'}, {**shared_style, 'display': 'block'}, {**shared_style, 'display': 'none'}

    elif triggered_id == 'main-plot' and clickData:
        # Clicking point in plot: show info, hide others
        return {**shared_style, 'display': 'block'}, {**shared_style, 'display': 'none'}, {**shared_style, 'display': 'none'}

    elif triggered_id == 'title-selector' and selected_title:
        # Selecting a title: show info, hide others
        return {**shared_style, 'display': 'block'}, {**shared_style, 'display': 'none'}, {**shared_style, 'display': 'none'}

    # Fallback: hide info, show word selector, hide author panel
    return {**shared_style, 'display': 'none'}, {**shared_style, 'display': 'block'}, {**shared_style, 'display': 'none'}


@app.callback(
    Output('panel-content', 'children'),
    Output('info-panel-name', 'children'),
    Output('highlight-paper-checklist', 'value', allow_duplicate=True),
    Input('main-plot', 'clickData'),
    Input('title-selector', 'value'),  # now receiving arxiv_id from dropdown   
    prevent_initial_call='initial_duplicate'
)
def update_panel_content(clickData, selected_arxiv_id):
    triggered_id = ctx.triggered_id

    # Determine source and extract data
    if triggered_id == 'main-plot' and clickData:
        point = clickData['points'][0]
        title = point.get('hovertext', 'N/A')
        customdata = point.get('customdata', [])
        category, year, author_list, arxiv_id, summary, subcategory, words = (customdata + ['N/A'] * 6)[:7]

    elif triggered_id == 'title-selector' and selected_arxiv_id:
        arxiv_id = selected_arxiv_id
        paper = df[df['arxiv_id'] == arxiv_id]
        if paper.empty:
            return "Paper not found.", dash.no_update, []
        paper = paper.iloc[0]

        title = paper.get('title', 'N/A')
        year = paper.get('year', 'N/A')
        summary = paper.get('summary', 'N/A')
        category = paper.get('category', 'N/A')
        subcategory = paper.get('subcategory', 'N/A')
        author_list = paper.get('author', 'N/A')
        words = paper.get('words', 'N/A')

    else:
        return "Click a point or select a paper to see details.", dash.no_update, []

    words = [w[0] for w in words]

    title = dcc.Markdown(
        re.sub(r'\s{2,}', ' ', title),
        mathjax=True,
        style={
            'marginTop': '-6px',
            'marginBottom': '0px',
            'overflowY': 'hidden',
            'maxHeight': '7em',
            'fontSize': '18px'
        }
    )

    return html.Div([
        html.Div([
            html.Span("🔗 arXiv ID: "),
            html.A(arxiv_id, href=f"https://arxiv.org/abs/{arxiv_id}", target="_blank")
        ], style={'marginTop': '-6px'}),
        html.Div(f"📅 Year: {year}"),
        html.Div([
            html.Span("📚 Category: "),
            make_button(categories_info.get(category, {}).get('name', category), 'category-label', category)
        ]),
        html.Div([
            html.Span("🔖 Subcategory: "),
            make_button(subcategory, 'subcategory-click', subcategory)
        ], style={'margin': '4px 0'}),
        html.Hr(style={'margin': '12px 0'}),
        html.Div("Authors:", style={'fontWeight': 'bold'}),
        format_authors(author_list),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("Top Words:", style={'marginTop': '8px'}),
        make_inline_button_list(words, 'word-click'),
        html.Hr(style={'margin': '12px 0'}),
        html.Div("Abstract:", style={'fontWeight': 'bold', 'marginTop': '8px', 'marginBottom': '0px'}),
        dcc.Markdown(
            summary,
            mathjax=True,
            style={'fontSize': '14px', 'marginTop': '-4px'}
        )
    ], style={'lineHeight': '1.6em', 'overflowY': 'auto'}), title, []
        

#################################################
# AUTHOR SELECTOR
#################################################
@app.callback(
    Output('author-selector', 'value'),
    Input({'type': 'author-click', 'index': ALL}, 'n_clicks'),
    State('author-selector', 'value'),
    prevent_initial_call=True
)
def update_author_selector(n_clicks_list, current_value):
    triggered = ctx.triggered_id

    if not isinstance(triggered, dict) or triggered.get('type') != 'author-click':
        raise dash.exceptions.PreventUpdate

    selected_author = triggered['index']
    i = next((i for i, comp in enumerate(ctx.inputs_list[0]) if comp['id'] == triggered), None)

    if i is not None and n_clicks_list[i] > 0 and current_value != selected_author:
        return selected_author

    raise dash.exceptions.PreventUpdate


#################################################
# CATEGORY PANEL CALLBACKS
#################################################

@app.callback(
    Output('category-info-panel', 'style', allow_duplicate=True),
    [Input({'type': 'category-label', 'index': ALL}, 'n_clicks'),
     Input('close-category-panel-btn', 'n_clicks')],
    prevent_initial_call=True
)
def toggle_category_info_panel(category_clicks, close_clicks):
    triggered_id = ctx.triggered_id
    if triggered_id == 'close-category-panel-btn':
        return get_panel_style(visible=False)

    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'category-label':
        component_ids = ctx.inputs_list[0]
        for i, comp in enumerate(component_ids):
            if comp['id'] == triggered_id and category_clicks[i] > 0:
                return get_panel_style(visible=True)

    return get_panel_style(visible=False)


@app.callback(
    Output('selected-category-store', 'data'),
    Input({'type': 'category-label', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def store_selected_category(n_clicks):
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'category-label':
        return triggered_id['index']
    return dash.no_update


@app.callback(
    Output('highlight-category-checklist', 'value', allow_duplicate=True),
    Input('close-category-panel-btn', 'n_clicks'),
    Input({'type': 'subcategory-click', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def reset_highlight_category_checklist(_, subcategory_clicks):
    triggered = ctx.triggered_id

    if triggered == 'close-category-panel-btn':
        return []

    if isinstance(triggered, dict) and triggered.get('type') == 'subcategory-click':
        return []

    return dash.no_update


@app.callback(
    Output('category-panel-content', 'children'),
    Output('category-panel-name', 'children'),
    Output('highlight-category-checklist', 'value', allow_duplicate=True),
    Input({'type': 'category-label', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_category_panel_content(_):
    triggered_id = ctx.triggered_id

    if not (isinstance(triggered_id, dict) and triggered_id.get('type') == 'category-label'):
        return "Click a category to see details.", dash.no_update, []

    category = triggered_id['index']
    info = categories_info.get(category, {})
    total_count = sum(info.get('counts', {}).values())
    subcategories_for_category = [sub for sub, meta in subcategories_info.items() if meta.get('category') == category]

    panel_content = html.Div([
        html.P(f"📄 Total Papers: {total_count}"),
        dcc.Graph(figure=build_line_plot(info.get('counts', {}), category), config={'displayModeBar': False}),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("🔖 Subcategories:", style={'marginTop': '8px'}),
        make_inline_button_list(subcategories_for_category, 'subcategory-click'),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("🧑‍💼 Top Authors:", style={'marginTop': '8px'}),
        html.Ul([
            html.Li([
                make_button(author['name'], 'author-click', author['name']),
                f" ({author['count']})"
            ]) for author in info.get('authors', [])[:10]
        ], style={'marginTop': '-15px'}),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("🔤 Top Words:", style={'marginTop': '8px'}),
        make_inline_button_list(info.get('words', []), 'word-click')
    ])

    label = categories_info.get(category, {}).get('name', category)

    return panel_content, make_colored_label(category, label), []


#################################################
# SUBCATEGORY PANNEL
#################################################

@app.callback(
    Output('selected-subcategory-store', 'data'),
    Input({'type': 'subcategory-click', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def store_selected_subcategory(n_clicks):
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'subcategory-click':
        return triggered_id['index']
    return dash.no_update

@app.callback(
    Output('subcategory-info-panel', 'style'),
    Output('category-info-panel', 'style', allow_duplicate=True), 
    Input({'type': 'subcategory-click', 'index': ALL}, 'n_clicks'),
    Input('close-subcategory-panel-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_subcategory_info_panel(button_clicks, close_click):
    triggered = ctx.triggered_id

    if triggered == 'close-subcategory-panel-btn':
        return get_panel_style(False), dash.no_update 

    if isinstance(triggered, dict) and triggered.get('type') == 'subcategory-click':
        for i, comp in enumerate(ctx.inputs_list[0]):
            if comp['id'] == triggered and button_clicks[i] > 0:
                return get_panel_style(True), get_panel_style(False) 

    return get_panel_style(False), dash.no_update



@app.callback(
    Output('highlight-subcategory-checklist', 'value', allow_duplicate=True),
    Input('close-subcategory-panel-btn', 'n_clicks'),
    prevent_initial_call=True
)
def reset_highlight_category_checklist(_):
    return []


@app.callback(
    Output('subcategory-panel-content', 'children'),
    Output('subcategory-panel-name', 'children'),
    Output('highlight-subcategory-checklist', 'value', allow_duplicate=True),
    Input({'type': 'subcategory-click', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def update_subcategory_panel_content(subcat_button_clicks):
    triggered_id = ctx.triggered_id

    if not (isinstance(triggered_id, dict) and triggered_id.get('type') == 'subcategory-click'):
        return "Click a subcategory to see details.",  dash.no_update, []

    subcategory = triggered_id.get('index')
    info = subcategories_info[subcategory]
    category = info['category']
    total_count = sum(info['counts'].values())
  
    panel_content = html.Div([
        html.Div(f"📝 Name: {info['name']}"),
        html.P(f"📄 Total Papers: {total_count}"),
        dcc.Graph(figure=build_line_plot(info['counts'], category), config={'displayModeBar': False}),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("🧑‍💼 Top Authors:", style={'marginTop': '8px'}),
        html.Ul([
            html.Li([
                make_button(author['name'], 'author-click', author['name']),
                f" ({author['count']})"
            ]) for author in info['authors']
        ], style={'marginTop': '-15px'}),
        html.Hr(style={'margin': '12px 0'}),
        html.H4("🔤 Top Words:", style={'marginTop': '8px'}),
        make_inline_button_list(info['words'], 'word-click')
    ])

    return panel_content,  make_colored_label(category, subcategory), []


#################################################
# WORDS
#################################################


@app.callback(
    Output('papers-with-word', 'children'),
    Input('word-selector', 'value')
)
def update_papers(selected_word):
    if not selected_word:
        return "Select a word to see papers."

    if selected_word not in word_paper:
        return f"No papers found with the word '{selected_word}'."

    # Get top 10 arXiv IDs for the selected word
    top_ids = word_paper[selected_word][:10]

    # Filter df for these arXiv IDs and preserve the order
    sub_df = df[df['arxiv_id'].isin(top_ids)].set_index('arxiv_id')
    top_papers = [(sub_df.loc[arxiv_id]['title'], arxiv_id) for arxiv_id in top_ids]

    return html.Div([
        html.H4("📄 Top Papers:", style={'marginTop': '-10px'}),
        html.Ul([
            html.Li(
                html.Button(
                    dcc.Markdown(
                        re.sub(r'\s{2,}', ' ', title),
                        mathjax=True,
                        style={'marginTop': '-6px', 'marginBottom': '0px', 'textAlign': 'left'}
                    ),
                    id={'type': 'title-click', 'index': arxiv_id},
                    n_clicks=0,
                    style={
                        'background': 'none',
                        'border': 'none',
                        'padding': 0,
                        'margin': 0,
                        'color': '#007BFF',
                        'cursor': 'pointer',
                        'width': '100%',
                        'textAlign': 'left'
                    }
                )
            )
            for title, arxiv_id in top_papers
        ], style={'marginTop': '-15px', 'listStyleType': 'none', 'paddingLeft': '0'})
    ])




@app.callback(
    Output('title-selector', 'value'),
    Input({'type': 'title-click', 'index': ALL}, 'n_clicks'),
    State('title-selector', 'value'),
    prevent_initial_call=True
)
def set_title_from_click(n_clicks_list, current_value):
    triggered = ctx.triggered_id

    if not isinstance(triggered, dict) or triggered.get('type') != 'title-click':
        raise dash.exceptions.PreventUpdate

    arxiv_id = triggered['index']
    i = next((i for i, comp in enumerate(ctx.inputs_list[0]) if comp['id'] == triggered), None)

    if i is not None and n_clicks_list[i] > 0 and current_value != arxiv_id:
        return arxiv_id

    raise dash.exceptions.PreventUpdate



@app.callback(
    Output('word-selector', 'value'),
    Input({'type': 'word-click', 'index': ALL}, 'n_clicks'),
    State('word-selector', 'value'),
    prevent_initial_call=True
)
def update_word_selector(n_clicks_list, current_value):
    triggered = ctx.triggered_id

    if not isinstance(triggered, dict) or triggered.get('type') != 'word-click':
        raise dash.exceptions.PreventUpdate

    selected_word = triggered['index']
    i = next((i for i, comp in enumerate(ctx.inputs_list[0]) if comp['id'] == triggered), None)

    if i is not None and n_clicks_list[i] > 0 and current_value != selected_word:
        return selected_word

    raise dash.exceptions.PreventUpdate


# #################################################
# # AUTHOR PANEL
# #################################################
@app.callback(
    Output('author-panel', 'style', allow_duplicate=True),
    Input('author-selector', 'value'),
    Input('close-author-panel-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_author_panel(selected_author, close_clicks):
    triggered = ctx.triggered_id

    if triggered == 'close-author-panel-btn':
        # Hide panel when close button clicked
        return {'display': 'none'}

    if selected_author:
        # Show panel if author selected
        return {
            'position': 'fixed',
            'top': '0',
            'right': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'backgroundColor': "#ffffff",
            'overflowY': 'auto',
            'display': 'block',  # show panel
        }

    # Default hide panel
    return {'display': 'none'}


@app.callback(
    Output('author-panel-content', 'children'),
    Output('author-panel-name', 'children'),
    Input('author-selector', 'value'),
    prevent_initial_call=True
)
def update_author_panel_content(selected_author):
    if not selected_author:
        return "Click an author to see details.", dash.no_update

    author_papers = df[df['author'].apply(lambda authors: selected_author in authors)]
    # Step 1: Flatten authors from selected author's papers
    all_coauthors = [
        coauthor
        for authors in author_papers['author']
        for coauthor in authors
        if coauthor != selected_author
    ]

    # Step 2: Count collaborators
    collab_counter = Counter(all_coauthors)

    # Step 3: Format collaborators
    collaborators = [{'name': name, 'count': count} for name, count in collab_counter.most_common()]

    return html.Div([
        html.H4("📄 Author Papers:", style={"marginTop": '0px'}),        
        html.Ul([
            html.Li(
                html.Button(
                    dcc.Markdown(
                        re.sub(r'\\s{{2,}}', ' ', row.title),
                        mathjax=True,
                        style={
                            'marginTop': '-6px',
                            'marginBottom': '0px',
                            'textAlign': 'left',
                            'fontSize': '13px'
                        }
                    ),
                    id={'type': 'title-click', 'index': row.arxiv_id},
                    n_clicks=0,
                    style={
                        'background': 'none',
                        'border': 'none',
                        'padding': 0,
                        'margin': 0,
                        'color': '#007BFF',
                        'cursor': 'pointer',
                        'width': '100%',
                        'textAlign': 'left'
                    }
                )
            )
            for row in author_papers.itertuples()
        ],  style={'marginTop': '-15px', 'listStyleType': 'none', 'paddingLeft': '0'}),
        html.Hr(style={'margin': '12px 0'}),
        html.Div("🧑‍💼 Author Collaborators:", style={'fontWeight': 'bold'}),
        html.Ul([
            html.Li([
                make_button(author['name'], 'author-click', author['name']),
                f" ({author['count']})"
            ]) for author in collaborators
        ])
    ]), html.H3(selected_author, style={'marginTop':'-6px'})


if __name__ == '__main__':
    app.run(debug=False)
