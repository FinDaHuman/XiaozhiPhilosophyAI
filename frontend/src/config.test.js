import assert from 'node:assert/strict'
import test from 'node:test'

import { buildApiUrl, resolveApiBase } from './config.js'

test('production uses the same-origin proxy instead of a baked tunnel URL', () => {
  assert.equal(
    resolveApiBase({
      isProduction: true,
      buildTimeUrl: 'https://stale-tunnel.example',
    }),
    '/api',
  )
})

test('an emergency browser override still takes priority', () => {
  assert.equal(
    resolveApiBase({
      override: 'https://temporary.trycloudflare.com/',
      isProduction: true,
    }),
    'https://temporary.trycloudflare.com',
  )
})

test('local development keeps the configured backend fallback', () => {
  assert.equal(
    resolveApiBase({
      isProduction: false,
      buildTimeUrl: 'http://127.0.0.1:9000/',
    }),
    'http://127.0.0.1:9000',
  )
})

test('API paths join without duplicate or missing slashes', () => {
  assert.equal(buildApiUrl('/api/', '/chat'), '/api/chat')
  assert.equal(buildApiUrl('/api', 'chat/stream'), '/api/chat/stream')
})
