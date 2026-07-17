// API base URL — priority:
//   1. localStorage override 'LILY_API_URL' (emergency repoint from browser console,
//      e.g. localStorage.setItem('LILY_API_URL','https://xxx.trycloudflare.com'); location.reload())
//   2. VITE_API_URL baked at build time (the permanent ngrok static domain)
//   3. local backend for development
function readOverride() {
  try {
    return window.localStorage.getItem('LILY_API_URL') || null;
  } catch {
    return null;
  }
}

export const API_BASE =
  readOverride() || import.meta.env.VITE_API_URL || 'http://localhost:8000';

// All backend calls go through this wrapper so the ngrok free-tier
// interstitial-bypass header is always sent (harmless on other hosts).
export function apiFetch(path, options = {}) {
  const headers = {
    'ngrok-skip-browser-warning': 'true',
    ...(options.headers || {}),
  };
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}
