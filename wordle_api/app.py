from importlib import import_module
from pathlib import Path
from pkgutil import iter_modules

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .utils import project_root


def create_app():
    return (AppBuilder()
            .add_api_routes()
            .add_error_handlers()
            .add_events()
            .add_healthcheck()
            .add_middleware()
            .create_app())


class AppBuilder:
    def __init__(self):
        self._app = FastAPI(title="Wordle Hints",
                            description="Finding the right words",
                            docs_url=None,
                            redoc_url="/docs")

    def add_api_routes(self):
        root_dir = project_root()
        router_dir = Path(__file__).parent / "routers"

        for submodule in iter_modules([router_dir.as_posix()]):
            if submodule.ispkg and (router_file := router_dir / submodule.name / "router.py").exists():
                module = import_module('.'.join(router_file.relative_to(root_dir).parts).replace('.py', ''))
                if hasattr(module, 'router'):
                    self._app.include_router(module.router, prefix=f"/api/{submodule.name.replace('_', '-')}")

        return self

    def add_error_handlers(self):
        # @self._app.exception_handler(PostgresError)
        # async def catch_all_handler(_: Request, exc: PostgresError):
        #     return JSONResponse(status_code=400, content={"error": exc.message, "detail": exc.detail})

        return self

    def add_events(self):
        @self._app.on_event("startup")
        async def startup():
            pass

        @self._app.on_event("shutdown")
        async def shutdown():
            pass

        return self

    def add_healthcheck(self):
        @self._app.get("/_healthcheck")
        def healthcheck():
            return JSONResponse({"status": "Okay"})

        return self

    def add_middleware(self):
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return self

    def create_app(self):
        return self._app
