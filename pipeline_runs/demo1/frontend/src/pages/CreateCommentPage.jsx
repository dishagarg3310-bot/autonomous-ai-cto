import React, { useState } from 'react';

function CreateCommentPage({ photoId, ownerId }) {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch(`http://127.0.0.1:8010/photos/${photoId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ photo_id: photoId, owner_id: ownerId, text }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed');
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Create Comment</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>COMMENT</label>
          <input value={text} onChange={(e) => setText(e.target.value)} required />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'SAVING...' : 'SAVE'}
        </button>
      </form>
      {error && <div className="message error">{error}</div>}
      {result && (
        <div className="message success">
          <div className="result-row"><span>id</span><span>{result.id}</span></div>
          <div className="result-row"><span>photo_id</span><span>{result.photo_id}</span></div>
          <div className="result-row"><span>owner_id</span><span>{result.owner_id}</span></div>
          <div className="result-row"><span>text</span><span>{result.text}</span></div>
        </div>
      )}
    </div>
  );
}

export default CreateCommentPage;