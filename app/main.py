from fastapi import FastAPI
from app.routes import user_routes, post_routes, auth_routes, follow_routes

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Instagram Clone Backend!"}

app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(post_routes.router, prefix="/posts", tags=["Posts"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(follow_routes.router, prefix="/follow", tags=["Follow"])
