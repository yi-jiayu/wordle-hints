import os

from wordle_api import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('DEBUG', '0') == '1'
    host = '127.0.0.1' if debug else '0.0.0.0'
    app.run_server(host=host, use_reloader=debug, use_debugger=debug, port=8080, debug=debug)
