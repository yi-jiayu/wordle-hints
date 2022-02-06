from wordle_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run_server('127.0.0.1',
                   use_reloader=True,
                   port=8080,
                   debug=True,
                   dev_tools_hot_reload=True)
