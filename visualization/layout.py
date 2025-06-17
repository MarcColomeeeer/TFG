from dash import dcc, html
from info import color_map, df, unique_authors, unique_words, categories_info

layout = html.Div([
    
    # -----------------------------
    # Category / Subcategory Stores
    # -----------------------------
    dcc.Store(id='selected-category-store', data=None),
    dcc.Store(id='selected-subcategory-store', data=None),

    # ---------------------
    # MAIN PLOT & SELECTORS
    # ---------------------
    html.Div([

        # ------------
        # Left Sidebar
        # ------------
        html.Div([
            html.Br(),

            # ---------------------
            # Toggle Points Button
            # ---------------------
            dcc.Checklist(
                id='toggle-points-btn',
                options=[{'label': 'Show Papers Coordinates', 'value': 'show'}],
                value=['show'],
                inputStyle={"margin-right": "6px"},
                labelStyle={'display': 'block', 'margin-bottom': '10px', 'fontWeight': 'bold'}
            ),

            # -----------------------
            # Toggle Centroids Button
            # -----------------------
            dcc.Checklist(
                id='toggle-centroids-btn',
                options=[{'label': 'Display Centroids & Areas', 'value': 'show'}],
                value=[],
                inputStyle={"margin-right": "6px"},
                labelStyle={'display': 'block', 'margin-bottom': '10px', 'fontWeight': 'bold'}
            ),

            html.Br(),

            # -----------------
            # Year Range Slider
            # -----------------
            dcc.RangeSlider(
                id='year-range-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                step=1,
                marks=None,
                value=[df['year'].min(), df['year'].max()],
                tooltip={"placement": "top", "always_visible": True}
            ),

            # ------------------------
            # Author Dropdown Selector
            # ------------------------
            dcc.Dropdown(
                id='author-selector',
                options=[{'label': author, 'value': author} for author in unique_authors],
                value=None,
                placeholder="Select an author",
                multi=False
            ),
            
            html.Br(),
            html.Hr(style={'margin': '12px 0'}),

            # ---------------------------
            # Category Checklist Selector
            # ---------------------------
            dcc.Checklist(
                id='category-selector',
                options=[
                    {
                        'label': html.Span([
                            # Colored dot
                            html.Span(style={
                                'display': 'inline-block',
                                'width': '12px',
                                'height': '12px',
                                'backgroundColor': color_map[category],
                                'borderRadius': '50%',
                                'marginRight': '8px',
                                'verticalAlign': 'middle'
                            }),
                            # Clickable category label
                            html.Button(categories_info[category]['name'],
                                id={'type': 'category-label', 'index': category},
                                n_clicks=0,
                                style={
                                    'background': 'none',
                                    'border': 'none',
                                    'padding': 0,
                                    'margin': 0,
                                    'cursor': 'pointer'
                            })
                        ]),
                        'value': category
                    }
                    for category in list(categories_info.keys())
                ],
                value=sorted(df['category'].unique()),
                inputStyle={"margin-right": "6px"},
                labelStyle={'display': 'block', 'margin-bottom': '6px'}
            ),

            # ---------------------------
            # Papers Per Year Lineplot
            # ---------------------------
            html.Div([
                dcc.Graph(
                    id='papers-per-year-plot',
                    config={'displayModeBar': False},
                    style={'height': '270px', 'width': '100%', 'marginLeft': '-10px'}
                )
            ], style={'marginTop': '20px'})
        ], style={
            'height': '100vh',
            'width': '260px',
            'padding': '10px',
            'boxSizing': 'border-box'
        }),

        # -----------------------
        # Main Plot (Scatterplot)
        # -----------------------
        html.Div([
            dcc.Graph(
                id='main-plot',
                style={
                    'position': 'absolute',
                    'top': 0,
                    'bottom': 0,
                    'left': '260px',
                    'right': '280px',
                    'overflow': 'hidden'
                }
            )
        ])
    ], style={
        'height': '100vh',
        'width': '100vw',
        'position': 'relative',
        'overflow': 'hidden'
    }),

    # ----------------
    # PAPER INFO PANEL
    # ----------------
    html.Div(
        id='info-panel',
        children=[

            # ----------------
            # Paper Name Title
            # ----------------
            html.Div(
                id='info-panel-name',
                children="Info Name",
                style={
                    'top': '5px',
                    'left': '10px',
                    'right': '10px',
                    'fontSize': '15px',
                    'fontWeight': 'bold',
                    'marginRight': '25px',
                    'overflowY': 'hidden',
                    'zIndex': '999',
                }
            ),

            # ------------
            # Close Button
            # ------------
            html.Button(
                "×", 
                id='close-panel-btn', n_clicks=0,
                style={
                    'position': 'absolute',
                    'top': '10px',
                    'right': '10px',
                    'border': 'none',
                    'background': 'transparent',
                    'fontSize': '24px',
                    'cursor': 'pointer',
                    'zIndex': '1000',
                    'overflowY': 'hidden'
                }
            ),

            # --------------------------
            # Highlight Checklist Button
            # --------------------------
            dcc.Checklist(
                id='highlight-paper-checklist',
                options=[{'label': 'Highlight Paper', 'value': 'highlight'}],
                value=[],
                inputStyle={'marginRight': '6px'},
                labelStyle={'display': 'block', 'marginBottom': '0'},
                style={
                    'marginTop': '5px',
                    'marginBottom': '20px',
                    'overflow': 'hidden'
                }
            ),

            # -------------------
            # Paper Panel Content
            # -------------------
            html.Div(
                id='panel-content',
                children="Click a point to see paper details here.",
                style={
                    'marginTop': '10px',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 120px)',
                    'paddingRight': '5px'
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': '0',
            'right': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'backgroundColor': "#ffffff",
            'display': 'none',
            'overflowY': 'hidden'
        }
    ),
    
    # -------------------
    # CATEGORY INFO PANEL
    # -------------------
    html.Div(
        id='category-info-panel',
        children=[

            # -------------------
            # Category Name Title
            # -------------------
            html.Div(
                id='category-panel-name',
                children="Category Name",
                style={
                    'position': 'absolute',
                    'top': '20px',
                    'left': '10px',
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'zIndex': '999'
                }
            ),

            # ------------
            # Close Button
            # ------------
            html.Button(
                "×", 
                id='close-category-panel-btn', 
                n_clicks=0,
                style={
                    'position': 'absolute',
                    'top': '10px',
                    'right': '10px',
                    'border': 'none',
                    'background': 'transparent',
                    'fontSize': '24px',
                    'cursor': 'pointer',
                    'zIndex': '1000'
                }
            ),

            # --------------------------
            # Highlight Checklist Button
            # --------------------------
            dcc.Checklist(
                id='highlight-category-checklist',
                options=[{'label': 'Highlight Category Papers', 'value': 'highlight'}],
                value=[],
                inputStyle={'marginRight': '6px'},
                labelStyle={'display': 'block', 'marginBottom': '0'},
                style={'marginTop': '50px'}
            ),

            # ----------------------
            # Category Panel Content
            # ----------------------
            html.Div(
                id='category-panel-content',
                children="Click a category to see details.",
                style={
                    'marginTop': '20px',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 120px)',
                    'paddingRight': '5px'
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'backgroundColor': "#ffffff",
            'display': 'none',
            'overflow': 'hidden'
        }
    ),

    # ----------------------
    # SUBCATEGORY INFO PANEL
    # ----------------------
    html.Div(
        id='subcategory-info-panel',
        children=[

            # ----------------------
            # Subcategory Name Title
            # ----------------------
             html.Div(
                id='subcategory-panel-name',
                children="Subcategory Name",
                style={
                    'position': 'absolute',
                    'top': '20px',
                    'left': '10px',
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'zIndex': '999'
                }
            ),

            # ------------
            # Close Button
            # ------------
            html.Button(
                "×", 
                id='close-subcategory-panel-btn', 
                n_clicks=0,
                style={
                    'position': 'absolute',
                    'top': '10px',
                    'right': '10px',
                    'border': 'none',
                    'background': 'transparent',
                    'fontSize': '24px',
                    'cursor': 'pointer',
                    'zIndex': '1000'
                }
            ),

            # --------------------------
            # Highlight Checklist Button
            # --------------------------
            dcc.Checklist(
                id='highlight-subcategory-checklist',
                options=[{'label': 'Highlight Subcategory Papers', 'value': 'highlight'}],
                value=[],
                inputStyle={'marginRight': '6px'},
                labelStyle={'display': 'block', 'marginBottom': '0'},
                style={'marginTop': '50px'}
            ),

            # -------------------------
            # Subcategory Panel Content
            # -------------------------
            html.Div(
                id='subcategory-panel-content',
                children="Click a subcategory to see details.",
                style={
                    'marginTop': '20px',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 120px)',
                    'paddingRight': '5px'
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'backgroundColor': '#ffffff',
            'display': 'none',
            'overflowY': 'auto'
        }
    ),
    
    # --------------------
    # WORD SELECTOR PANNEL
    # --------------------
    html.Div(
        id='word-selector-panel',
        children=[
            html.Br(),

            # --------------------
            # Paper Title Dropdown
            # --------------------
            dcc.Dropdown(
                id='title-selector',
                options=[
                    {'label': row['title'], 'value': row['arxiv_id']}
                    for _, row in df.iterrows()
                ],
                placeholder='Search a paper',
                style={
                    'marginBottom': '20px', 
                    'white-space':'nowrap'
                }
            ),
            
            html.Hr(style={'margin': '12px 0'}),

            # ----------------------
            # Word Selector Dropdown
            # ----------------------
            dcc.Dropdown(
                id='word-selector',
                options=[
                    {'label': word, 'value': word} 
                    for word in unique_words
                ],
                value=None,
                placeholder="Select a word",
                multi=False
            ),

            # -----------------------
            # Display Matching papers
            # -----------------------
            html.Div(
                id='papers-with-word', 
                style={
                    'marginTop': '20px', 
                    'padding': '10px'
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': '0',
            'right': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'overflowY': 'auto',
        }
    ),

    # -----------------
    # AUTHOR INFO PANNEL
    # ------------------
    html.Div(
        id='author-panel',
        children=[

            # -----------------
            # Author Name Title
            # -----------------
             html.Div(
                id='author-panel-name',
                children="Author Name",
                style={
                    'position': 'absolute',
                    'top': '20px',
                    'left': '10px',
                    'fontSize': '20px',
                    'fontWeight': 'bold',
                    'zIndex': '999'
                }
            ),

            # ------------
            # Close Button
            # ------------
            html.Button(
                "×", 
                id='close-author-panel-btn', 
                n_clicks=0,
                style={
                    'position': 'absolute',
                    'top': '10px',
                    'right': '10px',
                    'border': 'none',
                    'background': 'transparent',
                    'fontSize': '24px',
                    'cursor': 'pointer',
                    'zIndex': '1000'
                }
            ),

            # --------------------
            # Author Panel Content
            # --------------------
            html.Div(
                id='author-panel-content',
                children="Click an author to see author details here.",
                style={
                    'marginTop': '40px',
                    'overflowY': 'auto',
                    'maxHeight': 'calc(100vh - 60px)',
                    'paddingRight': '5px'
                }
            )
        ],
        style={
            'position': 'fixed',
            'top': '0',
            'right': '0',
            'width': '260px',
            'height': '100vh',
            'padding': '10px',
            'backgroundColor': "#ffffff",
            'display': 'none',
            'overflowY': 'auto'
        }
    )
])