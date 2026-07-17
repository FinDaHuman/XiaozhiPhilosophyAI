// API base URL — set VITE_API_URL on Vercel (e.g. the Cloudflare tunnel URL);
// falls back to the local backend for development.
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
