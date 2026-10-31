import React, { useState } from 'react';

function PhotoDetailPage({ id }) {
  const [photo, setPhoto] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchPhoto = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`http://127.0.0.1:8010/photos/${id}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed');
      }
      setPhoto(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Photo Detail</h2>
      <button className="btn" onClick={fetchPhoto} disabled={loading}>
        {loading ? 'LOADING...' : 'LOAD PHOTO'}
      </button>
      {error && <div className="message error">{error}</div>}
      {photo && (
        <div className="message success">
          <div className="result-row"><span>id</span><span>{photo.id}</span></div>
          <div className="result-row"><span>owner_id</span><span>{photo.owner_id}</span></div>
          <div className="result-row"><span>filename</span><span>{photo.filename}</span></div>
          <div className="result-row"><span>description</span><span>{photo.description}</span></div>
        </div>
      )}
    </div>
  );
}

export default PhotoDetailPage;