from wordle_app import create_app

app = create_app()
server = app.server  # needed for gunicorn

if __name__ == '__main__':
    app.run_server(use_reloader=True, use_debugger=True, port=8080, debug=True)
