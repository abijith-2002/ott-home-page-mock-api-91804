from typing import List, Dict
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Setup module logger
logger = logging.getLogger("uvicorn.error")

# Determine absolute path to images to avoid CWD-related issues
# Resolve using pathlib and parents to be robust across environments.
_THIS_FILE = Path(__file__).resolve()
_THIS_DIR = _THIS_FILE.parent
# src/api -> backend root is two levels up from this file: src/api -> src -> backend root
_BACKEND_ROOT = _THIS_DIR.parents[1]
_IMAGES_DIR_PATH = _BACKEND_ROOT / "images"
_IMAGES_DIR = str(_IMAGES_DIR_PATH)


def _safe_listdir(path: str) -> list:
    """Utility to list a directory safely, returning [] on error and logging issues."""
    try:
        return sorted(os.listdir(path))
    except Exception as e:
        logger.warning(f"[Static] Could not list dir {path}: {e}")
        return []


def _find_case_insensitive(root: str, filename: str) -> str | None:
    """
    Resolve a filename under root in a case-insensitive manner.
    If an exact match exists, return it. Otherwise try to match ignoring case.

    Args:
        root (str): Root directory
        filename (str): Requested filename

    Returns:
        str | None: Absolute path if found, else None
    """
    exact_path = os.path.join(root, filename)
    if os.path.isfile(exact_path):
        return exact_path
    # Fallback: case-insensitive search over first 1000 entries to avoid excessive iteration
    lower = filename.lower()
    for name in _safe_listdir(root)[:1000]:
        if name.lower() == lower:
            cand = os.path.join(root, name)
            if os.path.isfile(cand):
                return cand
    return None


# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    - Mounts the static images directory under /media (primary).
    - Adds a compatibility mount under /images to address clients using /images.
    - Adds permissive CORS for local testing.
    - Registers API routes under / and /api/*.
    - Provides OpenAPI docs metadata and tags.
    - Emits debug logging about the resolved static directory and sample file existence.
    - Exposes diagnostics endpoint to show resolved images_dir and files list.
    - Adds guaranteed diagnostics at /_health/images and /_debug/images.
    - Adds passthrough GET /images/{filename:path} with case-insensitive lookup and logging.

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
            {"name": "Diagnostics", "description": "Runtime diagnostics and environment info."},
        ],
    )

    # Diagnostics: log resolved paths
    logger.info(f"[Static] _THIS_DIR={_THIS_DIR}")
    logger.info(f"[Static] _BACKEND_ROOT={_BACKEND_ROOT}")
    logger.info(f"[Static] _IMAGES_DIR={_IMAGES_DIR}")
    logger.info(f"[Static] images dir exists? {os.path.isdir(_IMAGES_DIR)}")
    sample_list = _safe_listdir(_IMAGES_DIR)[:5] if os.path.isdir(_IMAGES_DIR) else []
    logger.info(f"[Static] sample files: {sample_list}")

    # Mount static images directory using an absolute path for reliability
    # Mount at both /media and /images for maximum compatibility with frontends.
    # Using absolute path ensures consistency across different working directories / process managers.
    app.mount("/media", StaticFiles(directory=_IMAGES_DIR), name="media")
    app.mount("/images", StaticFiles(directory=_IMAGES_DIR), name="images")

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

    We avoid forcing any host rewriting (e.g., with X-Forwarded-*), letting the ASGI server / proxy provide
    the correct base_url. Trailing slash is stripped for clean concatenation.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        str: Base URL like 'https://domain.tld'
    """
    # request.base_url includes trailing slash; remove it for clean concatenation
    base = str(request.base_url).rstrip("/")
    # Debug log: incoming base url and path
    try:
        logger.debug(f"[Request] base_url={base}, url.path={request.url.path}")
    except Exception:
        pass
    return base


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

    # PUBLIC_INTERFACE
    @app.get(
        "/api/media/exists/{filename}",
        tags=["Media"],
        summary="Check if media file exists",
        description="Returns 200 if the requested media file exists in the images directory, 404 otherwise.",
        responses={
            200: {"description": "File exists"},
            404: {"description": "File not found"},
        },
    )
    def media_exists(filename: str):
        """
        Health check for media files existence.

        Args:
            filename (str): Image filename to check (e.g., 'bcs.jpg').

        Returns:
            dict: {'exists': True} if found, otherwise 404.
        """
        path = _find_case_insensitive(_IMAGES_DIR, filename)
        if path:
            return {"exists": True, "resolved": os.path.basename(path)}
        raise HTTPException(status_code=404, detail="File not found")

    # PUBLIC_INTERFACE
    @app.get(
        "/api/media/{filename}",
        tags=["Media"],
        summary="Serve media file (explicit passthrough)",
        description="Explicit passthrough route to serve a media file. Normally, static files are served from /media/{filename}. This route is for diagnostics.",
        responses={
            200: {"description": "The media file will be returned"},
            404: {"description": "File not found"},
        },
    )
    def media_passthrough(filename: str):
        """
        Serve a media file directly via FileResponse for debugging.

        Args:
            filename (str): Image filename to serve.

        Returns:
            FileResponse: The requested image file or 404.
        """
        path = _find_case_insensitive(_IMAGES_DIR, filename)
        logger.info(f"[MediaPassthrough] request filename={filename} -> resolved={path}")
        if not path:
            logger.warning(f"[MediaPassthrough] File not found: {os.path.join(_IMAGES_DIR, filename)}")
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path)

    # PUBLIC_INTERFACE
    @app.get(
        "/images/{filename:path}",
        tags=["Media"],
        summary="Compatibility: Serve image under /images (case-insensitive)",
        description="Passthrough route to serve images via FileResponse with case-insensitive lookup. Useful if StaticFiles path mismatch is suspected or clients use /images.",
        responses={
            200: {"description": "The image file will be returned"},
            404: {"description": "File not found"},
        },
    )
    def images_passthrough(filename: str):
        """
        Passthrough FileResponse server for /images/{filename} with case-insensitive lookup.

        Args:
            filename (str): Image filename to serve.

        Returns:
            FileResponse: The requested image file, or 404 if missing.
        """
        path = _find_case_insensitive(_IMAGES_DIR, filename)
        logger.info(f"[ImagesPassthrough] request filename={filename} -> resolved={path}")
        if not path:
            logger.warning(f"[ImagesPassthrough] File not found: {os.path.join(_IMAGES_DIR, filename)}")
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path)

    # PUBLIC_INTERFACE
    @app.get(
        "/api/media/debug",
        tags=["Diagnostics"],
        summary="Media directory diagnostics",
        description="Returns the resolved absolute images directory path and lists available files.",
        responses={200: {"description": "Diagnostics returned"}},
    )
    def media_debug(request: Request):
        """
        Expose diagnostics for the resolved images directory and available files.

        Returns:
            dict: path info and filenames
        """
        base = _build_base_url(request)
        exists = os.path.isdir(_IMAGES_DIR)
        files = _safe_listdir(_IMAGES_DIR) if exists else []
        sample_url = None
        if files:
            sample_url = f"{base}/media/{files[0]}"
        payload = {
            "this_dir": str(_THIS_DIR),
            "backend_root": str(_BACKEND_ROOT),
            "images_dir": _IMAGES_DIR,
            "images_dir_exists": exists,
            "files_count": len(files),
            "files": files[:50],
            "sample_media_url": sample_url,
            "notes": "Static mounts are available at /media and /images.",
        }
        return JSONResponse(payload)

    # PUBLIC_INTERFACE
    @app.get(
        "/_health/images",
        tags=["Diagnostics"],
        summary="Health: Images directory",
        description="Guaranteed diagnostics endpoint. Returns absolute images_dir path, exists flag, first 50 entries, and mounted routes.",
        responses={200: {"description": "Diagnostics returned"}},
    )
    def health_images():
        """
        Health endpoint for images directory and routing information.

        Returns:
            dict: includes resolved images_dir, exists check, listing, and mounted routes.
        """
        exists = os.path.isdir(_IMAGES_DIR)
        files = _safe_listdir(_IMAGES_DIR) if exists else []
        routes = []
        # Collect mounted routes info
        for r in app.router.routes:
            try:
                routes.append(getattr(r, "path", str(r)))
            except Exception:
                routes.append(str(r))
        return JSONResponse({
            "images_dir": _IMAGES_DIR,
            "images_dir_exists": exists,
            "list_first_50": files[:50],
            "mounted_routes": routes,
        })

    # PUBLIC_INTERFACE
    @app.get(
        "/_debug/images",
        tags=["Diagnostics"],
        summary="Debug: Images directory",
        description="Guaranteed diagnostics endpoint. Same as /_health/images for debugging purposes.",
        responses={200: {"description": "Diagnostics returned"}},
    )
    def debug_images():
        """
        Debug endpoint for images directory and routing information.

        Returns:
            dict: includes resolved images_dir, exists check, listing, and mounted routes.
        """
        exists = os.path.isdir(_IMAGES_DIR)
        files = _safe_listdir(_IMAGES_DIR) if exists else []
        routes = []
        for r in app.router.routes:
            try:
                routes.append(getattr(r, "path", str(r)))
            except Exception:
                routes.append(str(r))
        return JSONResponse({
            "images_dir": _IMAGES_DIR,
            "images_dir_exists": exists,
            "list_first_50": files[:50],
            "mounted_routes": routes,
        })


# Create global app entrypoint for ASGI servers like uvicorn
app = create_app()
