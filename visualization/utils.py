from dash import html
import plotly.graph_objects as go

from info import color_map

def make_button(label, id_type, index):
    return html.Button(
        label,
        id={'type': id_type, 'index': index},
        n_clicks=0,
        style={
            'background': 'none',
            'border': 'none',
            'padding': 0,
            'margin': 0,
            'color': '#007BFF',
            'cursor': 'pointer'
        }
    )


def format_authors(authors):
    # Join author buttons with commas, no trailing comma after last author
    buttons = []
    for i, author in enumerate(authors):
        buttons.append(make_button(author, 'author-click', author))
        if i < len(authors) - 1:
            buttons.append(", ")
    return html.Div(buttons, style={'display': 'inline', 'lineHeight': '1.6em'})


def get_panel_style(visible):
    return {
        'position': 'fixed',
        'top': '0',
        'left': '0',
        'width': '260px',
        'height': '100vh',
        'padding': '10px',
        'backgroundColor': "#ffffff",
        'display': 'block' if visible else 'none'
    }


def make_colored_label(category, text):
    return html.Span([
        html.Span(style={
            'display': 'inline-block',
            'width': '18px',
            'height': '18px',
            'backgroundColor': color_map[category],
            'borderRadius': '50%',
            'marginRight': '8px',
            'verticalAlign': 'middle'
        }),
        text
    ])


def build_line_plot(year_counts, category):
    
    # Convert to sorted lists
    years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in years]

    # Create the plot
    fig = go.Figure(go.Scatter(
        x=years,
        y=counts,
        mode='lines',
        name='Category publications',
        line_shape='spline',
        line=dict(color=color_map.get(category, 'blue'))
    ))

    fig.update_layout(
        margin=dict(t=0, r=0, l=0, b=0),
        height=250,
        legend=dict(orientation='h', yanchor='bottom', y=-0.7, xanchor='right', x=1),
        xaxis=dict(tickangle=-45)
    )
    fig.data[0].hovertemplate = "%{y}<extra></extra>"
    return fig


def make_inline_button_list(items, id_type):
    return html.Div([
        html.Span([
            make_button(item, id_type, item),
            ", " if i < len(items) - 1 else ""
        ]) for i, item in enumerate(items)
    ], style={'marginTop': '-15px'})