import { useState } from 'react'
import { api } from '../api'

function CreatePaste() {
  const [content, setContent] = useState('')
  const [ttlSeconds, setTtlSeconds] = useState('')
  const [maxViews, setMaxViews] = useState('')
  const [pasteUrl, setPasteUrl] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setPasteUrl('')
    setLoading(true)

    try {
      const data = await api.createPaste(content, ttlSeconds, maxViews)
      setPasteUrl(data.url)
      setContent('')
      setTtlSeconds('')
      setMaxViews('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Pastebin</h1>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="content">Paste Content *</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your text here..."
            rows="10"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="ttl">TTL (seconds)</label>
            <input
              id="ttl"
              type="number"
              value={ttlSeconds}
              onChange={(e) => setTtlSeconds(e.target.value)}
              placeholder="Optional"
              min="1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="maxViews">Max Views</label>
            <input
              id="maxViews"
              type="number"
              value={maxViews}
              onChange={(e) => setMaxViews(e.target.value)}
              placeholder="Optional"
              min="1"
            />
          </div>
        </div>

        <button type="submit" disabled={loading || !content}>
          {loading ? 'Creating...' : 'Create Paste'}
        </button>
      </form>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {pasteUrl && (
        <div className="success">
          <strong>Paste created successfully!</strong>
          <div className="url-box">
            <a href={pasteUrl} target="_blank" rel="noopener noreferrer">
              {pasteUrl}
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

export default CreatePaste
