import os

import uvicorn

from server import create_app

app = create_app()

if __name__ == '__main__':
    use_reload = os.getenv('DEBUG', '0') == '1'

    uvicorn.run('api_server:app', host='0.0.0.0', port=8080, reload=use_reload)
