# AI Virtual Jewellery Try-On

A full-stack application that lets a user upload a photo, choose a piece of
jewellery (from a built-in catalogue or their own upload), and generate a
photorealistic try-on image with Google Gemini. The generated image can then be
animated into a short preview video with Kling.

The codebase is built around clean architecture: typed configuration, provider
abstractions with swappable real/fake implementations, dependency injection, a
storage abstraction, and a consistent response/error envelope.

---

## Overview

```
Upload face / hand photo
        +
Catalogue item or uploaded jewellery
        ↓
POST /api/v1/uploads    validate + store both images
        ↓
POST /api/v1/try-on     Gemini edits the photo to wear the jewellery
        ↓
Result image shown + downloadable
        ↓
POST /api/v1/videos     (optional) Kling animates the image into a short clip
        ↓
Result video shown + downloadable
```

The frontend automatically routes the correct photo to Gemini based on the
selected category: the **face** photo for necklaces, earrings, and glasses; the
**hand** photo for rings, bracelets, and watches.

## Features

- Face and hand photo uploads with instant previews.
- Built-in jewellery catalogue plus custom jewellery upload — both flow through
  the same upload pipeline.
- Robust image validation (magic-number sniffing, size, dimensions,
  decompression-bomb protection).
- Gemini-powered, category-specific, versioned prompts for identity-preserving
  try-on.
- Optional Kling image-to-video generation with server-side polling.
- Download of both the generated image and video.
- Consistent JSON response envelope, request-id correlation, and typed errors.
- Deterministic, offline test suite via fake providers.

## Architecture

Layered, dependency-injected FastAPI backend:

- **Routes** (`app/api/routes`) — thin HTTP handlers; parse request, call a
  service, shape the envelope response.
- **Services** (`app/services`) — domain logic: validation, storage,
  preprocessing, Gemini try-on, Kling video.
- **Providers** — vendor integrations behind abstractions
  (`GeminiProvider` → `GoogleGeminiProvider` / `FakeGeminiProvider`;
  `VideoProvider` → `KlingVideoProvider` / `FakeVideoProvider`;
  `StorageProvider` → `LocalStorageProvider`). Selected by config via DI, so the
  app is testable offline and swappable without touching callers.
- **Models / Schemas** — internal domain dataclasses vs. Pydantic request/response
  contracts.
- **Core** — typed `Settings` (env-driven), exception hierarchy, request-id
  middleware.

The React frontend is a single screen with local state, a shared
`useImageUpload` hook, and a typed Axios client. A Vite dev proxy forwards
`/api` and `/health` to the backend, so no CORS configuration is needed in
development.

## Folder structure

```
backend/
  app/
    api/
      routes/       health, uploads, tryon, videos, results
      dependencies.py   DI providers/factories
      errors.py         exception handlers → error envelope
      middleware.py     request-id middleware
    core/           config (Settings), exceptions
    models/         internal domain objects (ValidatedImage, StoredObject, ...)
    schemas/        Pydantic request/response contracts + envelope
    services/       validation, storage, preprocessing, gemini, video
    prompts/        versioned try-on prompt fragments
    utils/          identifiers, image inspection, signatures
  tests/            pytest suite (deterministic, fake providers)
  requirements.txt / requirements-dev.txt / .env.example
frontend/
  src/
    api/            typed Axios client + types
    components/     UploadCard, CatalogueGrid, ResultView, ...
    hooks/          useImageUpload
    data/           jewellery catalogue
  public/jewellery/ catalogue images
```

## Tech stack

- **Backend:** Python 3.11+ (developed on 3.14), FastAPI, Pydantic v2 /
  pydantic-settings, Pillow, google-genai, httpx, anyio.
- **Frontend:** React 18, Vite, TypeScript (strict), Tailwind CSS, Axios.
- **AI:** Google Gemini (image generation), Kling (image-to-video).

## Installation

Prerequisites: Python 3.11+, Node.js 18+, and (for real generation) a Google
Gemini API key and a Kling API key.

### Backend setup

```bash
cd backend
python -m venv .venv
# Windows PowerShell:  .venv\Scripts\Activate.ps1
# macOS/Linux:         source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API at `http://127.0.0.1:8000`; interactive docs at `/docs`.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App at `http://localhost:5173` (proxies `/api` and `/health` to the backend).

## Environment variables

All configuration is environment-driven (`backend/.env`); no secrets are
hardcoded. See `backend/.env.example` for the full list.

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_PROVIDER` | `fake` (offline) or `google` (real API) | `fake` |
| `GEMINI_API_KEY` | Google AI Studio key (required for `google`) | — |
| `GEMINI_MODEL` | Image-capable Gemini model id | `gemini-2.5-flash-image` |
| `GEMINI_TEMPERATURE` / `GEMINI_TOP_P` / `GEMINI_CANDIDATE_COUNT` | Generation params | `0.2` / `0.95` / `1` |
| `VIDEO_PROVIDER` | `fake` (offline) or `kling` (real API) | `fake` |
| `KLING_API_KEY` | Kling API key (required for `kling`) | — |
| `KLING_BASE_URL` / `KLING_MODEL` | Kling endpoint + model | `https://api-singapore.klingai.com` / `kling-v1` |
| `KLING_POLL_INTERVAL_SECONDS` / `KLING_POLL_TIMEOUT_SECONDS` | Polling cadence/limit | `5` / `300` |
| `STORAGE_DIR` | Root folder for uploads and generated output | `storage` |
| `MAX_UPLOAD_SIZE_BYTES` / `MAX_IMAGE_DIMENSION` / `MAX_IMAGE_PIXELS` | Upload validation limits | — |
| `PREPROCESS_MAX_DIMENSION` | Max side sent to the model | `1536` |

### Gemini setup

1. Create an API key in Google AI Studio.
2. Set `GEMINI_PROVIDER=google` and `GEMINI_API_KEY=<key>` in `backend/.env`.
3. Keep `GEMINI_MODEL=gemini-2.5-flash-image` (an AI-Studio-compatible image
   model). Note: image generation is a **billed** feature with no free tier.

### Kling setup

1. Obtain a Kling API key.
2. Set `VIDEO_PROVIDER=kling` and `KLING_API_KEY=<key>` in `backend/.env`.
3. The provider authenticates with `Authorization: Bearer <KLING_API_KEY>`,
   submits the try-on image to the image-to-video endpoint, polls until the task
   completes, then stores the resulting MP4.

With `GEMINI_PROVIDER=fake` / `VIDEO_PROVIDER=fake` (defaults), the full flow runs
offline and deterministically — ideal for development and the test suite.

## Running locally

Run the backend and frontend in two terminals (see setup above), then open the
Vite URL. The header shows a live "Backend: online" badge when connectivity is
working.

### Tests

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest -q
```

Tests override the Gemini and Video providers with fakes, so they never call
external APIs and are fully deterministic.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness/readiness (unversioned) |
| POST | `/api/v1/uploads` | Validate + store an image (`file`, optional `kind`) → `201` |
| POST | `/api/v1/try-on` | Generate try-on image (`person_upload_id`, `jewellery_upload_id`, `category`) → `201` |
| POST | `/api/v1/videos` | Generate video from a result (`image_result_id`) → `201` |
| GET | `/api/v1/results/{result_id}` | Stream the generated image |
| GET | `/api/v1/videos/{video_id}/content` | Stream the generated video |

Success envelope:

```json
{ "data": { "...": "..." }, "meta": { "request_id": "req_..." } }
```

## Error handling

Every response carries an `X-Request-ID` header. Errors use one consistent shape:

```json
{
  "error": {
    "code": "UNSUPPORTED_MEDIA_TYPE",
    "message": "Unsupported file type. Allowed types: image/jpeg, image/png, image/webp.",
    "request_id": "req_...",
    "details": []
  }
}
```

Stable codes map to correct HTTP status codes: `400` (bad request / empty),
`404` (not found), `413` (too large / oversized), `415` (unsupported type),
`422` (corrupt / validation / safety refusal), `429` (rate limited), `502/504`
(upstream errors/timeouts). Video generation is isolated: if Kling fails, the
image generation still succeeds and remains downloadable — the failure surfaces
as a friendly message and never crashes the app.

## Screenshots

_Add screenshots here._

- `docs/screenshot-home.png` — upload + catalogue screen
- `docs/screenshot-result.png` — generated image + video result screen
- `docs/demo.mp4` — short end-to-end demo recording

## Known limitations

- **Kling account balance:** the Kling integration is complete and working
  end-to-end, but the current account returns
  `{"code":1102,"message":"Account balance not enough"}`, so live video
  generation cannot be demonstrated until the account is funded. The `fake`
  video provider exercises the full pipeline offline in the meantime.
- **Gemini billing:** image generation has no free tier; a depleted-credit key
  returns `429 RESOURCE_EXHAUSTED`. Use a funded key or the `fake` provider.
- **Synchronous video generation:** the `/videos` request blocks while the
  backend polls Kling. This is intentional for a demo; a production system would
  model it as an async job with client polling/webhooks.
- **Local storage only:** artifacts live on the local filesystem behind
  `StorageProvider`, swappable for cloud storage without touching callers.
- **No authentication:** the API is open, appropriate for a local demo.

## Future improvements

- Async job model for video generation (task id + polling/SSE).
- Cloud storage provider (S3/GCS) implementing `StorageProvider`.
- Result-retrieval metadata endpoints and persistence (currently file-backed).
- Authentication, rate limiting, and per-user history.
- Frontend tests and CI (lint + type-check + pytest).
