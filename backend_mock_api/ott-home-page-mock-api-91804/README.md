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
- Compatibility mount: `/images/{filename}` (added to support clients requesting `/images/*`)
- The app mounts the local folder: `backend_mock_api/images`
- Static mount is configured with an absolute path resolved from `src/api/main.py`, so it works regardless of current working directory.

## Diagnostic Media Endpoints
- GET `/api/media/exists/{filename}` — returns `{ "exists": true }` if file exists, 404 otherwise.
- GET `/api/media/{filename}` — direct FileResponse passthrough for debugging (normal usage should prefer `/media/{filename}` served via StaticFiles).
- GET `/images/{filename}` — fallback FileResponse route for `/images/*` if StaticFiles is mis-resolved by runtime/proxy.

## Verify Static Files (troubleshooting 404)
1) Check OpenAPI and sample list:
   - Open logs: the app logs the resolved images directory path and lists a few sample files on startup.
2) Verify file existence:
   - curl -s http://localhost:3001/api/media/exists/bcs.jpg
3) Fetch via primary static mount:
   - curl -I http://localhost:3001/media/bcs.jpg
4) Fetch via compatibility mount:
   - curl -I http://localhost:3001/images/bcs.jpg
5) Fetch via explicit passthrough (bypasses StaticFiles):
   - curl -I http://localhost:3001/api/media/bcs.jpg

If (2) returns exists=true but (3) returns 404, suspect a proxy/ingress static path mismatch; (4) or (5) should succeed and can be used as a fallback.

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
- If you previously used a different static path, note: primary route is `/media/{filename}` and images live in `backend_mock_api/images`. For compatibility, `/images/{filename}` is also available.
