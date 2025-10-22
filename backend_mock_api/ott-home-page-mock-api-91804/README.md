# OTT Home Page Mock API

A FastAPI backend that serves mock endpoints for an OTT application's home page. Poster image URLs are generated dynamically based on the request's domain/host and images are served as static files.

## Run (example)
From the backend root:
- Install deps:
  pip install -r backend_mock_api/requirements.txt
- Start the API (from backend_mock_api directory):
  uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

Docs: http://localhost:3001/docs

## Static Media
- Primary static mount: `/media/{filename}`
- Compatibility static mount: `/images/{filename}`
- Additionally, a passthrough route exists: `GET /images/{filename}` (case-insensitive) to serve via FileResponse with logs.
- The app mounts the local folder: `backend_mock_api/images`
- Static mounts are configured with an absolute path resolved using `Path(__file__).resolve().parents` from `src/api/main.py`, so it works regardless of current working directory.

## Guaranteed Diagnostics Endpoints
These endpoints always return JSON even if static mounts fail:
- GET `/_health/images` — returns resolved `images_dir`, `exists` flag, first 50 entries, and mounted routes.
- GET `/_debug/images` — same as above for debugging.
- Existing diagnostics:
  - GET `/api/media/debug` — returns resolved `images_dir` and list of files.
  - GET `/api/media/exists/{filename}` — returns `{ "exists": true }` if file exists, 404 otherwise.
  - GET `/api/media/{filename}` — direct FileResponse passthrough for debugging.

## Verify Static Files (troubleshooting 404)
1) Diagnostics:
   - curl -s http://localhost:3001/_health/images | jq
   - curl -s http://localhost:3001/_debug/images | jq
2) Verify file existence (case-insensitive supported):
   - curl -s http://localhost:3001/api/media/exists/bcs.jpg
3) Fetch via primary static mount:
   - curl -I http://localhost:3001/media/bcs.jpg
4) Fetch via compatibility static mount:
   - curl -I http://localhost:3001/images/bcs.jpg
5) Fetch via explicit passthrough (bypasses StaticFiles and logs path):
   - curl -I http://localhost:3001/api/media/bcs.jpg
6) Direct passthrough under /images (case-insensitive and logs path):
   - curl -I http://localhost:3001/images/Stranger_Things.jpg

If (2) returns exists=true but (3) returns 404, suspect a proxy/ingress static path mismatch; (4), (5), or (6) should succeed and can be used as a fallback.

## Known Working URLs (examples)
- Stranger Things via /media:
  - http://localhost:3001/media/stranger_things.jpg
- Stranger Things via /images (static mount):
  - http://localhost:3001/images/stranger_things.jpg
- Stranger Things via passthrough (case-insensitive):
  - http://localhost:3001/images/Stranger_Things.jpg
  - http://localhost:3001/api/media/stranger_things.jpg
- Diagnostics:
  - http://localhost:3001/_health/images
  - http://localhost:3001/_debug/images
  - http://localhost:3001/api/media/debug

## Endpoints
- GET `/`                      - Health check
- GET `/api/trending`          - Trending shows
- GET `/api/continue_watching` - Continue watching
- GET `/api/action`            - Action shows
- GET `/api/family`            - Family shows
- GET `/api/comedy`            - Comedy shows
- GET `/api/horror`            - Horror shows
- GET `/api/drama`             - Drama shows

All endpoints return an array of objects:
[
  { "name": "Show Name", "poster": "https://<your-host>/media/<file>.jpg" }
]

## Example curl
curl -s http://localhost:3001/api/trending | jq

## Notes
- CORS is permissive for local testing.
- Poster URLs use the request's scheme and host to avoid hard-coding domains. We strip trailing slash from `request.base_url` to ensure correct concatenation (`https://host/media/file.jpg`).
- The OpenAPI documentation includes tags and response models for clarity.
- Primary route is `/media/{filename}` and images live in `backend_mock_api/images`. For compatibility, `/images/{filename}` (static) and `GET /images/{filename}` (passthrough) are also available.
