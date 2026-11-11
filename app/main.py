from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.routes import auth_routes, user_routes, post_routes
from app.utils.db import init_db, close_db
from app.utils.rate_limit import limiter
from app.config.settings import DATABASE_URL

_PUBLIC_ROUTES = {
    ("get", "/"),
    ("post", "/auth/create"),
    ("post", "/auth/login"),
    ("post", "/auth/verify-token"),
    ("get", "/posts/"),
    ("get", "/posts/{post_id}"),
    ("get", "/users/profile/{username}"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(DATABASE_URL)
    yield
    close_db()


app = FastAPI(lifespan=lifespan, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(post_routes.router, prefix="/posts", tags=["Posts"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Instagram Clone Backend!"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="InstaClone API",
        version="1.0.0",
        description="API documentation for InstaClone",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path, path_item in openapi_schema["paths"].items():
        for method, operation in path_item.items():
            if (method.lower(), path) not in _PUBLIC_ROUTES:
                operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
