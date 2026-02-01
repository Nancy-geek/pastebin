import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'

function ViewPaste() {
  const { pasteId } = useParams()
  const [paste, setPaste] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchPaste = async () => {
      try {
        const data = await api.fetchPaste(pasteId)
        setPaste(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchPaste()
  }, [pasteId])

  if (loading) {
    return <div className="container"><p>Loading...</p></div>
  }

  if (error) {
    return (
      <div className="container">
        <h1>Error</h1>
        <p className="error">{error}</p>
        <Link to="/">Create New Paste</Link>
      </div>
    )
  }

  return (
    <div className="container">
      <h1>Paste</h1>
      
      <div className="paste-content">
        {paste.content}
      </div>

      <div className="paste-meta">
        {paste.remaining_views !== null && (
          <p>Remaining Views: {paste.remaining_views}</p>
        )}
        {paste.expires_at && (
          <p>Expires: {new Date(paste.expires_at).toLocaleString()}</p>
        )}
      </div>

      <Link to="/">Create New Paste</Link>
    </div>
  )
}

export default ViewPaste
