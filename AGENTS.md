# AGENTS.md

## Cursor Cloud specific instructions

### What this repo is
The primary application is the **WhatsApp MCP Dashboard**: a FastAPI backend in `backend/` and a
React (Create React App) frontend in `frontend/`. The Jupyter notebooks, `labs/`, `docs/`, and
`*.py` scripts at the repo root are unrelated legacy data-science course material and are not part
of the app.

### Running the app (dev)
The update script creates a Python virtualenv at `./venv` (repo root) and installs frontend deps.
Startup commands are documented in the root `package.json` scripts (`start-backend`, `start-frontend`, `dev`):

- Backend: from `backend/`, run `../venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000`
  (serves the API and Swagger docs at `http://localhost:8000/docs`).
- Frontend: from `frontend/`, run `npm start` (dev server on `http://localhost:3000`; it proxies
  `/api` to the backend on `:8000` via the `proxy` field in `frontend/package.json`). In a headless
  VM prefix with `BROWSER=none` so it does not try to open a browser.

### Non-obvious caveats
- `backend/requirements.txt` contains three entries that are never imported and cannot be installed
  as pinned: `sqlite3` (stdlib, not a PyPI package), `whatsapp-api-client-python==0.1.1` (no such
  version), and `mcp==1.0.0` (needs `anyio>=4.6`, conflicting with `fastapi==0.104.1`). The update
  script filters these three out before `pip install`; do not re-add them.
- The backend expects the external WhatsApp MCP Go server at `ws://localhost:8001`. It is **optional**
  for development — the backend logs `Failed to connect to WhatsApp MCP server` on startup and
  continues running normally. No phone/QR pairing is needed to run and test the dashboard.
- `backend/.env` is created from `backend/.env.template`. OpenAI/Anthropic keys are optional; without
  them, message classification falls back to keyword/TextBlob logic. The SQLite DB
  (`backend/whatsapp_mcp.db`) is created automatically on first backend startup.
- Only the `Dashboard` page fetches live backend data; the other frontend pages (Messages,
  Auto-Responses, Broadcast, etc.) are placeholder stubs. To exercise core API functionality
  (e.g. creating auto-response rules, messages, broadcasts), use the Swagger UI at `:8000/docs`.

### Lint / test
- Frontend: `npm test` (CRA/Jest) and eslint runs as part of `npm start`/`npm run build`. There are
  currently only benign unused-import eslint warnings.
- There is no backend test suite in the repo.
