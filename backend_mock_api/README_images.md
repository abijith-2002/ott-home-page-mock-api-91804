# Static Images - Quick Reference

- Primary static mount: GET /media/{filename}
- Compatibility mount: GET /images/{filename}
- Diagnostics:
  - GET /api/media/exists/{filename}
  - GET /api/media/{filename}
  - GET /api/media/debug           ← shows resolved images_dir and lists files

Examples:
- curl -I http://localhost:3001/media/bcs.jpg
- curl -I http://localhost:3001/images/bcs.jpg
- curl -s http://localhost:3001/api/media/exists/bcs.jpg
- curl -I http://localhost:3001/api/media/bcs.jpg
- curl -s http://localhost:3001/api/media/debug | jq

Working URL base:
- Posters are generated as {request.base_url}/media/{filename}
- Example for Stranger Things:
  - http://localhost:3001/media/stranger_things.jpg

The static directory is resolved to backend_mock_api/images using an absolute path for reliability and is logged on startup. If you see 404s:
1) Check diagnostics: GET /api/media/debug
2) Verify file exists (case-insensitive check is supported): GET /api/media/exists/Stranger_Things.jpg
3) Try direct passthrough: GET /api/media/stranger_things.jpg
4) If behind a reverse proxy, ensure it forwards the correct host/scheme so request.base_url is accurate.
