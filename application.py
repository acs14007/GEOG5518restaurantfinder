import pandas as pd
import geopandas as gpd

from dash import Dash, dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import plotly.express as px

# Open Food Data
food_data_path = r'https://raw.githubusercontent.com/acs14007/GEOG5518restaurantfinder/main/Food_full.csv'
food_data = pd.read_csv(food_data_path)
food_data = gpd.GeoDataFrame(food_data, geometry=gpd.points_from_xy(food_data.longitudes, food_data.latitudes))

# Add color column
food_data['price_labels'] = ''
price_labels = food_data.price_labels.copy()
price_labels[food_data.price == '$'] = 'Under $10'
price_labels[food_data.price == '$$'] = '$11-30'
price_labels[food_data.price == '$$$'] = 'Over $31'
price_labels[food_data.price.isna()] = 'Other'
food_data['price_labels'] = price_labels

# Open Mapbox Token
token = open('.mapbox_token').read()

# Define App
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'Restaurant Finder'
# dbc.load_figure_template('LUX')
# Beanstalk looks for application by default, if this isn't set you will get a WSGI error.
application = app.server

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "24rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H2('About:'),
        html.P(
            'This website was created for GEOG 5518 at UConn by Aaron Spaulding. Restaurant data was collected from Yelp by Dr. Xiang \"Peter\" Chen.'),
        html.P('Point color denotes price and size denotes rating.'),
        html.Hr(),
        html.H2('Image:'),
        html.Img(id='image', src='', style={'width': '22rem'}),

    ],
    style=SIDEBAR_STYLE,
)


fig = px.scatter_mapbox(food_data,
                        lat='latitudes',
                        lon='longitudes',
                        color='price_labels',
                        zoom=10,
                        hover_name='full_address',
                        hover_data=['image_url'],
                        category_orders={'price_labels': ['Under $10', '$11-30', 'Over $31', 'Other']},
                        color_discrete_map={'Under $10': 'yellow', '$11-30': 'orange', 'Over $31': 'red',
                                            'Other': 'grey'},
                        size='rating',
                        size_max=10)
fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)

fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor="right", x=1))
fig.update_layout(legend_title_text='Price')

app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col(),
            dbc.Col(html.H1('Restaurants in Hartford Connecticut'), width=9,
                    style={'margin-left': '7px', 'margin-top': '7px'})
        ]),
        dbc.Row([dbc.Col(sidebar),
                 dbc.Col(dcc.Graph(id='graph', figure=fig, style={'height': '90vh'}),
                         width=9,
                         style={'margin-left': '7px', 'margin-top': '7px', 'margin-right': '15px'})
                 ])
    ]
)

# app.layout = html.Div([
#     html.H1(children='Restaurants in Hartford Connecticut',
#             style={'textAlign': 'center', 'color': '#000080'}),
#     html.Hr(),
#     dcc.Graph(id='graph', figure=fig, style={'width': '40vw', 'height': '90vh'}),
#     html.Img(id='image', src='', style={'width': '40vw', 'height': '40vh'}),
# ])


@app.callback(
   Output('image', 'src'),
   Input('graph', 'hoverData'))
def open_url(hover_data):
    if hover_data:
        print(hover_data['points'])
        return hover_data['points'][0]['customdata'][0]
    else:
        raise PreventUpdate


if __name__ == '__main__':
    # Beanstalk expects it to be running on 8080.
    application.run(debug=False, port=8080)
    # app.run_server(debug=True)
