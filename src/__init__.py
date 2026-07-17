import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db.main import init_db
from .middleware import register_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server is starting ...")
    await init_db()  # initialize the database connection
    yield
    print("server is stopping")


version = "v1"


def create_app() -> FastAPI:
    from .auth.routes import auth_router
    from .books.routes import book_router
    from src.favorites.routes import favorites_router
    from src.reviews.routes import review_router
    from src.tags.routes import tags_router

    app = FastAPI(
        title="Bookly",
        description="fast api",
        version=version,
        lifespan=lifespan,
    )

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uploads_dir = os.path.join(backend_dir, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    register_middleware(app)

    app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
    app.include_router(auth_router, prefix=f"/api/{version}/auths", tags=["auths"])
    app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["review"])
    app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
    app.include_router(favorites_router, prefix=f"/api/{version}/favorites", tags=["favorites"])

    return app


app = create_app()