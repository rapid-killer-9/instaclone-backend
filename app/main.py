from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.openapi.utils import get_openapi
from app.routes import user_routes, auth_routes, post_routes

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Instagram Clone Backend!"}

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(post_routes.router, prefix="/posts", tags=["Posts"])
# app.include_router(follow_routes.router, prefix="/follow", tags=["Follow"])


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
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi