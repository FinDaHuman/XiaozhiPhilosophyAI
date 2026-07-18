# Lily Web Frontend

React/Vite single-page application for Lily's two-subject learning experience:
landing page, lessons, quizzes, and RAG chat with cited slide previews.

## Run locally

```powershell
npm install
npm run dev
```

The development URL is normally `http://localhost:5173`. Start the FastAPI
backend from the repository root with `venv\Scripts\python main.py api`.

## Backend URL resolution

`src/config.js` resolves the API base in this order:

1. `localStorage.LILY_API_URL` for an emergency browser-side override;
2. build-time `VITE_API_URL`;
3. `http://localhost:8000`.

Example local build:

```powershell
$env:VITE_API_URL='https://your-static-domain.ngrok-free.dev'
npm run build
```

`VITE_API_URL` is baked into the bundle. Verify the built assets before a
production deploy. Full ngrok/Vercel instructions are in
`../GUIDE_KHOI_DONG.md`.

## Project data

`src/data/subjects.js` is the frontend source of truth for subject metadata,
lessons, slide directories, and quiz groupings. Quiz content lives in
`src/data/quiz.json` (MLN111) and `src/data/quiz_ktct.json` (KTCT). Slide images
are served from `public/slides/` and `public/slides_ktct/`.

## Checks

```powershell
npm run lint
npm run build
```

See the root `README.md` for product architecture and `API_INTEGRATION.md` for
the chat and streaming contracts.
