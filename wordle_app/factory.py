from dash import Dash, html
from dash_bootstrap_components import themes

from .sections import controls, hints


def create_app():
    app = Dash(__name__, external_stylesheets=[themes.BOOTSTRAP], title="Wordle Hints")
    app.layout = get_layout()

    controls.register_callbacks(app)
    hints.register_callbacks(app)
    return app


def get_layout():
    return html.Div([
        html.H2("Wordle Hints", style={'marginTop': 16}),
        html.Hr(),
        controls.get_layout(),
        hints.get_layout(),
        html.Br(),
    ], style={
        'padding': '0 16px'
    })
