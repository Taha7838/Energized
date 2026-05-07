import axios from 'axios'

const BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

/**
 * POST /api/v1/query — non-streaming fallback
 */
export async function postQuery(query) {
  const response = await api.post('/query', { query })
  return response.data
}

/**
 * GET /api/v1/history
 */
export async function getHistory() {
  const response = await api.get('/history')
  return response.data.items
}

/**
 * SSE streaming connection for /api/v1/query/stream
 *
 * @param {string} query
 * @param {object} callbacks
 * @param {function} callbacks.onProgress  - called with each progress string
 * @param {function} callbacks.onResult    - called with the final result object
 * @param {function} callbacks.onError     - called with error string
 * @param {function} callbacks.onDone      - called when stream closes
 * @returns {EventSource} - call .close() to abort
 */
export function streamQuery(query, { onProgress, onResult, onError, onDone }) {
  const url = `${BASE_URL}/query/stream?q=${encodeURIComponent(query)}`
  const es = new EventSource(url)

  es.addEventListener('progress', (e) => {
    if (onProgress) onProgress(e.data)
  })

  es.addEventListener('result', (e) => {
    try {
      const data = JSON.parse(e.data)
      if (onResult) onResult(data)
    } catch (_err) {
      if (onError) onError('Failed to parse result from server.')
    }
  })

  es.addEventListener('error', (e) => {
    if (e.data && onError) {
      onError(e.data)
    } else if (onError) {
      onError('Connection to server lost.')
    }
    es.close()
  })

  es.addEventListener('done', () => {
    es.close()
    if (onDone) onDone()
  })

  return es
}
