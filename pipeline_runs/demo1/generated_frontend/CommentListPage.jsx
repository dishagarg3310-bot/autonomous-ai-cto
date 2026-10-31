import React, { useState } from 'react';

function CommentListPage() {
  const [comments, setComments] = useState([]);
  const [photoId, setPhotoId] = useState('');
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchComments = async (newOffset) => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      params.append('limit', limit);
      params.append('offset', newOffset);
      const response = await fetch(`http://127.0.0.1:8010/photos/${photoId}/comments?${params.toString()}`);
      if (!response.ok) throw new Error('Could not load comments');
      const data = await response.json();
      setComments(data);
      setOffset(newOffset);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Comments</h2>
      <div className="field">
        <label>PHOTO ID</label>
        <input value={photoId} onChange={(e) => setPhotoId(e.target.value)} />
      </div>
      <button className="btn" onClick={() => fetchComments(0)} disabled={loading}>
        {loading ? 'LOADING...' : 'FETCH'}
      </button>
      {error && <div className="message error">{error}</div>}
      {comments.map((comment) => (
        <div className="message success" key={comment.id}>
          <div className="result-row"><span>ID</span><span>{comment.id}</span></div>
          <div className="result-row"><span>PHOTO ID</span><span>{comment.photo_id}</span></div>
          <div className="result-row"><span>OWNER ID</span><span>{comment.owner_id}</span></div>
          <div className="result-row"><span>TEXT</span><span>{comment.text}</span></div>
        </div>
      ))}
      <button className="btn" onClick={() => fetchComments(Math.max(0, offset - limit))} disabled={offset === 0}>
        PREVIOUS
      </button>
      <button className="btn" onClick={() => fetchComments(offset + limit)}>
        NEXT
      </button>
    </div>
  );
}

export default CommentListPage;