import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, State, dash_table, html
from dash.exceptions import PreventUpdate

from data_source import CorpusFactory


def get_layout():
    return html.Div([
        dbc.Modal(
            children=[
                dbc.ModalHeader("Hints"),
                dbc.ModalBody([
                    dash_table.DataTable(
                        id="table-score-output",
                        columns=[{'name': i, 'id': i} for i in ['WORD', 'SCORE']],
                        filter_action="native",
                        sort_action="native",
                        row_selectable=False,
                        page_action="native",
                        page_current=0,
                        page_size=20,
                    ),
                ]),
            ],
            id='hint-modal',
            is_open=False,
            size='xl'),
    ])


def register_callbacks(app: Dash):
    factory = CorpusFactory(word_length=5)

    @app.callback(
        [
            Output('hint-modal', 'is_open'),
            Output('table-score-output', 'data')
        ],
        [
            Input('fetch-hints-button', 'n_clicks'),
        ],
        [
            State('corpus-select', 'value'),
            State({'type': 'confirmed', 'index': ALL}, 'value'),
            State({'type': 'include', 'field': 'letter', 'index': ALL}, 'value'),
            State({'type': 'include', 'field': 'exclude-positions', 'index': ALL}, 'value'),
            State('exclude-letters-dropdown', 'value'),
            State('hint-limit-input', 'value'),
        ],
        prevent_initial_call=True)
    def get_hints(_click: int,
                  corpus_source: str,
                  confirmed_letters: list[str],
                  include_letters: list[str],
                  include_letters_exclude_positions: list[list[str]],
                  exclude_letters: list[str],
                  hint_limit: int | str):
        if not _click:
            raise PreventUpdate

        corpus = factory.get_corpus(source=corpus_source)

        exclusions: list[str | tuple[str, list[int]]] = [x for x in (exclude_letters or []) if x]
        for letter, positions in zip(include_letters, include_letters_exclude_positions):
            if letter and isinstance(positions, list) and len(positions) > 0:
                exclusions.append((letter, [int(x) for x in positions]))

        data = corpus.get_potential_words(
            fixed_letters={pos: letter for pos, letter in enumerate(confirmed_letters, 1) if letter},
            include_letters=[x for x in include_letters if x],
            exclude_letters=exclusions,
        )

        if hint_limit and int(hint_limit) > 0:
            data = data.head(hint_limit)

        return [
            True,
            data.to_dict('records'),
        ]
