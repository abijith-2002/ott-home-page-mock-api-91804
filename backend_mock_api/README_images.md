# Static Images - Quick Reference

- Primary static mount: GET /media/{filename}
- Compatibility mount: GET /images/{filename}
- Diagnostics:
  - GET /api/media/exists/{filename}
  - GET /api/media/{filename}

Examples:
- curl -I http://localhost:3001/media/bcs.jpg
- curl -I http://localhost:3001/images/bcs.jpg
- curl -s http://localhost:3001/api/media/exists/bcs.jpg
- curl -I http://localhost:3001/api/media/bcs.jpg

The static directory is resolved to backend_mock_api/images using an absolute path for reliability and is logged on startup.
