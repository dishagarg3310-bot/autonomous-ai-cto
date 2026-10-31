import React, { useState } from 'react';

function NoteDetailPage() {
  const [id, setId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch(`http://127.0.0.1:9100/notes/${id}`, {
        method: 'GET',
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed');
      }
      setTitle(data.title);
      setContent(data.content);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Note Detail</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'LOADING...' : 'LOAD'}
        </button>
      </form>
      {error && <div className="message error">{error}</div>}
      {result && (
        <div className="message success">
          <div className="result-row"><span>Title</span><span>{result.title}</span></div>
          <div className="result-row"><span>Content</span><span>{result.content}</span></div>
        </div>
      )}
    </div>
  );
}

export default NoteDetailPage;