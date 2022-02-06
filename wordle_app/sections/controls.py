from string import ascii_uppercase

import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, dcc, html

from data_source import CorpusFactory


def get_layout():
    letter_options = [{'label': '', 'value': ''}, *[{'label': x, 'value': x} for x in ascii_uppercase]]
    factory = CorpusFactory(5)

    return html.Div([
        html.Div([
            dbc.Alert(id="validation-message-alert", color="danger"),
        ], id='validation-message-container', hidden=True),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.InputGroup([
                dbc.InputGroupText("Limit"),
                dbc.Input(id="hint-limit-input", value='')
            ]), width=3),
            dbc.Col(dbc.InputGroup([
                dbc.InputGroupText("Corpus"),
                dbc.Select(id='corpus-select',
                           options=[{'label': x, 'value': x} for x in factory.sources],
                           value='web2'),
            ]), width=3),
            dbc.Col(dbc.Button("Fetch Hints", id="fetch-hints-button", color='secondary', disabled=True))
        ]),
        html.Br(),
        dbc.Card([
            dbc.CardHeader("Confirmed Letters"),
            dbc.CardBody([
                html.P("Letters here are the greens you get on wordle, they must exist at that position. If unknown, leave empty"),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Select(
                                id={'type': 'confirmed', 'index': i},
                                options=letter_options,
                            )
                        )
                        for i in range(1, 6)]
                ),
            ]),
        ]),
        html.Br(),
        dbc.Card([
            dbc.CardHeader("Include Letters"),
            dbc.CardBody([
                html.Div([
                    html.P("Letters here should be here but you're not sure which position they are. These are the yellows you get on wordle"),
                    "Select the letter than indicate the positions which the letter cannot be in. For example, if",
                    html.Code("S"),
                    "cannot be in positions 1 and 4 (yellow on wordle for those positions), put",
                    html.Code("1 4"),
                    "(space separated) in the input"
                ]),
                html.Br(),
                html.Div([
                    dbc.Row([
                        dbc.Col([
                            dbc.Select(id={'type': 'include', 'field': 'letter', 'index': i},
                                       options=letter_options)
                        ], xs=12, sm=12, md=6, lg=4, xl=4),
                        dbc.Col([
                            dcc.Dropdown(id={'type': 'include', 'field': 'exclude-positions', 'index': i},
                                         options=[{'label': j, 'value': j} for j in range(1, 6)],
                                         multi=True,
                                         placeholder="Exclude positions")
                        ], xs=12, sm=12, md=6, lg=4, xl=4),
                    ])
                    for i in range(1, 6)
                ])
            ]),
        ]),
        html.Br(),
        dbc.Card([
            dbc.CardHeader("Exclude Letters"),
            dbc.CardBody([
                html.P("Excludes these letters entirely."),
                dcc.Dropdown(
                    id='exclude-letters-dropdown',
                    options=[{'label': x, 'value': x} for x in ascii_uppercase],
                    multi=True),
            ])
        ]),
    ])


def register_callbacks(app: Dash):
    @app.callback(
        [
            Output('validation-message-container', 'hidden'),
            Output('validation-message-alert', 'children'),
            Output("fetch-hints-button", "disabled"),
            Output("fetch-hints-button", "color"),
        ],
        [
            Input({'type': 'confirmed', 'index': ALL}, 'value'),
            Input({'type': 'include', 'field': 'letter', 'index': ALL}, 'value'),
            Input({'type': 'include', 'field': 'exclude-positions', 'index': ALL}, 'value'),
            Input('exclude-letters-dropdown', 'value'),
            Input('hint-limit-input', 'value'),
        ],
        prevent_initial_call=True)
    def validate_inputs(confirmed_letters: list[str],
                        include_letters: list[str],
                        include_letters_exclude_positions: list[list[str]],
                        exclude_letters: list[str],
                        hint_limit: int | str):
        # prep the data
        confirmed_letters = {x for x in (confirmed_letters or []) if x}
        include_letters_ex_positions_map = {letter: positions or []
                                            for letter, positions in
                                            zip(include_letters, include_letters_exclude_positions)
                                            if letter}
        include_letters = {x for x in (include_letters or []) if x}
        exclude_letters = {x for x in (exclude_letters or []) if x}
        hint_limit = str(hint_limit or '')

        # check for errors
        letter_errors = []
        sets = {
            'confirmed': confirmed_letters,
            'include': include_letters,
            'exclude': exclude_letters,
        }
        for key1, key2 in [
            ('confirmed', 'include'),
            ('confirmed', 'exclude'),
            ('include', 'exclude'),
        ]:
            set1 = sets[key1]
            set2 = sets[key2]

            if len(invalid_letters := set1 & set2) > 0:
                letter_errors.extend([
                    html.H6("Letters in both include and exclude list"),
                    html.Code(", ".join(sorted(invalid_letters)))
                ])
        if len(letter_errors) > 0:
            letter_errors.append(html.Hr())

        include_letter_ex_positions_errors = []
        for letter, positions in include_letters_ex_positions_map.items():
            if letter and not (1 <= (n_positions := len(positions)) <= 4):
                include_letter_ex_positions_errors.extend([
                    html.Code(letter),
                    f"must have between 1 and 4 excluded positions. Got {n_positions} positions",
                    html.Br()
                ])

        if len(include_letter_ex_positions_errors) > 0:
            include_letter_ex_positions_errors.append(html.Hr())

        hint_limit_errors = []
        if hint_limit != '' and (not hint_limit.isnumeric() or not float(hint_limit).is_integer() or int(hint_limit) <= 0):
            hint_limit_errors.append(f"Hint Limit must be a positive integer or empty. Got {hint_limit} instead.")

        errors = [*letter_errors, *include_letter_ex_positions_errors, *hint_limit_errors]
        has_error = len(errors) > 0
        if has_error:
            # add header if has errors
            errors = [
                html.H5("Errors"),
                html.Hr(),
                *errors
            ]

        return [
            not has_error,  # validation message hidden = True (not has_error) and vice versa
            errors,  # error messages
            has_error,  # fetch button is disabled = True when has_error
            "secondary" if has_error else "primary",
        ]
