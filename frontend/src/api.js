export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = {
  createPaste: async (content, ttlSeconds, maxViews) => {
    const payload = { content }
    if (ttlSeconds) payload.ttl_seconds = parseInt(ttlSeconds)
    if (maxViews) payload.max_views = parseInt(maxViews)

    const response = await fetch(`${API_URL}/api/pastes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(JSON.stringify(error))
    }

    return response.json()
  },

  fetchPaste: async (pasteId) => {
    const response = await fetch(`${API_URL}/api/pastes/${pasteId}`)

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Paste not found')
    }

    return response.json()
  }
}
