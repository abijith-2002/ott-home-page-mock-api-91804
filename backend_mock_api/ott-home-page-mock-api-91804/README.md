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
- Images are served from: /media/{filename}
- The app mounts the local folder: backend_mock_api/images

## Endpoints
- GET /                      - Health check
- GET /api/trending          - Trending shows
- GET /api/continue_watching - Continue watching
- GET /api/action            - Action shows
- GET /api/family            - Family shows
- GET /api/comedy            - Comedy shows
- GET /api/horror            - Horror shows
- GET /api/drama             - Drama shows

All endpoints return an array of objects:
[
  { "name": "Show Name", "poster": "https://<your-host>/media/<file>.jpg" }
]

## Example curl
curl -s http://localhost:3001/api/trending | jq

## Notes
- CORS is permissive for local testing.
- Poster URLs use the request's scheme and host to avoid hard-coding domains.
- The OpenAPI documentation includes tags and response models for clarity.
