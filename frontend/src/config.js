// API base URL priority:
//   1. localStorage override 'LILY_API_URL' for an emergency direct tunnel.
//   2. Same-origin /api proxy in production. Browsers never resolve ngrok.
//   3. VITE_API_URL or localhost for local development.
function readOverride() {
  try {
    return window.localStorage.getItem('LILY_API_URL') || null;
  } catch {
    return null;
  }
}

function normalizeBase(value) {
  if (!value || value === '/') return '';
  return value.replace(/\/+$/, '');
}

export function resolveApiBase({ override, isProduction, buildTimeUrl } = {}) {
  if (override) return normalizeBase(override);
  if (isProduction) return '/api';
  return normalizeBase(buildTimeUrl || 'http://localhost:8000');
}

const viteEnv = import.meta.env || {};

export const API_BASE = resolveApiBase({
  override: readOverride(),
  isProduction: Boolean(viteEnv.PROD),
  buildTimeUrl: viteEnv.VITE_API_URL,
});

export function buildApiUrl(base, path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${normalizeBase(base)}${normalizedPath}`;
}

// Vercel forwards this header to ngrok. It is harmless for local development
// and keeps the emergency direct-tunnel override working.
export function apiFetch(path, options = {}) {
  const headers = {
    'ngrok-skip-browser-warning': 'true',
    ...(options.headers || {}),
  };
  return fetch(buildApiUrl(API_BASE, path), { ...options, headers });
}
