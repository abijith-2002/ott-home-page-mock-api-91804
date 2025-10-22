from typing import List, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    - Mounts the static images directory under /media.
    - Adds permissive CORS for local testing.
    - Registers API routes under / and /api/*.
    - Provides OpenAPI docs metadata and tags.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    app = FastAPI(
        title="OTT Home Page Mock API",
        description="Mock API server that simulates an OTT application's homepage data with dynamic image URLs bound to the request domain.",
        version="1.0.0",
        openapi_tags=[
            {"name": "Health", "description": "Service status and metadata."},
            {"name": "Media", "description": "Static media files."},
            {"name": "Catalog", "description": "Mock endpoints for various content categories."},
        ],
    )

    # Mount static images directory
    # The images directory exists at backend_mock_api/images relative to project root.
    # At runtime, CWD is typically backend_mock_api, so "images" resolves correctly.
    app.mount("/media", StaticFiles(directory="images"), name="media")

    # Permissive CORS for local testing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)
    return app


class ShowItem(BaseModel):
    """Pydantic model representing a show item with a name and poster URL."""
    name: str = Field(..., description="Display name of the show or movie.")
    poster: str = Field(..., description="Fully-qualified URL to the poster image.")


def _build_base_url(request: Request) -> str:
    """
    Build a base URL based on the incoming request, ensuring it matches the current host and scheme.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: Base URL like 'https://domain.tld'
    """
    # request.base_url includes trailing slash; remove it for clean concatenation
    return str(request.base_url).rstrip("/")


def _build_items(files: List[tuple], request: Request) -> List[ShowItem]:
    """
    Helper to construct ShowItem list from (name, filename) tuples.

    Args:
        files (List[tuple]): List of tuples (name, filename.jpg).
        request (Request): Current request to derive dynamic base URL.

    Returns:
        List[ShowItem]: Items with fully qualified poster URLs.
    """
    base = _build_base_url(request)
    return [ShowItem(name=name, poster=f"{base}/media/{fname}") for name, fname in files]


# Source data based on the attached API doc
DATA: Dict[str, List[tuple]] = {
    "trending": [
        ("Better Call Saul", "bcs.jpg"),
        ("Breaking Bad", "br_ba.jpg"),
        ("Dexter", "dexter.jpg"),
        ("The Witcher", "the_witcher.jpg"),
        ("True Detective", "true_detective.jpg"),
        ("You", "you.jpg"),
        ("The Walking Dead", "the_walking_dead.jpg"),
        ("The Last of Us", "the_last_of_us.jpg"),
        ("Dark", "dark.jpg"),
        ("Stranger Things", "stranger_things.jpg"),
    ],
    "continue_watching": [
        ("The Boys", "the_boys.jpg"),
        ("Money Heist", "money_heist.jpg"),
        ("Avatar", "avatar.jpg"),
        ("The Last of Us", "the_last_of_us.jpg"),
    ],
    "action": [
        ("The Witcher", "the_witcher.jpg"),
        ("The Boys", "the_boys.jpg"),
        ("The Last of Us", "the_last_of_us.jpg"),
        ("Prison Break", "prison_break.jpg"),
        ("Fallout", "fallout.jpg"),
        ("Avatar", "avatar.jpg"),
    ],
    "family": [
        ("Avatar", "avatar.jpg"),
        ("Pokemon", "pokemon.jpg"),
        ("Bluey", "bluey.jpg"),
        ("Phineas and Ferb", "phineas_and_ferb.jpg"),
        ("Sonic Prime", "sonic_prime.jpg"),
        ("The Big Show Show", "the_big_show.jpg"),
    ],
    "comedy": [
        ("The Office", "the_office.jpg"),
        ("The Boys", "the_boys.jpg"),
        ("Friends", "friends.jpg"),
        ("Modern Family", "modern_family.jpg"),
        ("Seinfeld", "seinfeld.jpg"),
        ("Wednesday", "wednesday.jpg"),
    ],
    "horror": [
        ("Stranger Things", "stranger_things.jpg"),
        ("The Last of Us", "the_last_of_us.jpg"),
        ("The Sandman", "the_sandman.jpg"),
        ("The Walking Dead", "the_walking_dead.jpg"),
        ("Wednesday", "wednesday.jpg"),
    ],
    "drama": [
        ("The Witcher", "the_witcher.jpg"),
        ("The Last of Us", "the_last_of_us.jpg"),
        ("Dark", "dark.jpg"),
        ("Stranger Things", "stranger_things.jpg"),
        ("The Sandman", "the_sandman.jpg"),
        ("Money Heist", "money_heist.jpg"),
    ],
}


def register_routes(app: FastAPI) -> None:
    """
    Register all routes on the provided FastAPI app.

    Args:
        app (FastAPI): The application to register routes on.
    """

    # PUBLIC_INTERFACE
    @app.get("/", tags=["Health"], summary="Health Check")
    def health_check() -> Dict[str, str]:
        """
        Health check endpoint.

        Returns:
            dict: A simple healthy message.
        """
        return {"message": "Healthy"}

    # PUBLIC_INTERFACE
    @app.get(
        "/api/trending",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Trending Shows",
        description="Returns a list of trending TV shows with poster URLs built dynamically from the request domain.",
        responses={200: {"description": "List of trending show items."}},
    )
    def get_trending(request: Request) -> List[ShowItem]:
        return _build_items(DATA["trending"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/continue_watching",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Continue Watching",
        description="Returns a list of shows the user is continuing to watch (mock data).",
        responses={200: {"description": "List of continue watching items."}},
    )
    def get_continue_watching(request: Request) -> List[ShowItem]:
        return _build_items(DATA["continue_watching"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/action",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Action Shows",
        description="Returns a list of action category shows (mock data).",
        responses={200: {"description": "List of action show items."}},
    )
    def get_action(request: Request) -> List[ShowItem]:
        return _build_items(DATA["action"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/family",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Family Shows",
        description="Returns a list of family category shows (mock data).",
        responses={200: {"description": "List of family show items."}},
    )
    def get_family(request: Request) -> List[ShowItem]:
        return _build_items(DATA["family"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/comedy",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Comedy Shows",
        description="Returns a list of comedy category shows (mock data).",
        responses={200: {"description": "List of comedy show items."}},
    )
    def get_comedy(request: Request) -> List[ShowItem]:
        return _build_items(DATA["comedy"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/horror",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Horror Shows",
        description="Returns a list of horror category shows (mock data).",
        responses={200: {"description": "List of horror show items."}},
    )
    def get_horror(request: Request) -> List[ShowItem]:
        return _build_items(DATA["horror"], request)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/drama",
        response_model=List[ShowItem],
        tags=["Catalog"],
        summary="Get Drama Shows",
        description="Returns a list of drama category shows (mock data).",
        responses={200: {"description": "List of drama show items."}},
    )
    def get_drama(request: Request) -> List[ShowItem]:
        return _build_items(DATA["drama"], request)


# Create global app entrypoint for ASGI servers like uvicorn
app = create_app()
