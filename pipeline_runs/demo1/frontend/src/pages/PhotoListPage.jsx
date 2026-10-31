import React, { useState } from 'react';

function PhotoListPage() {
  const [photos, setPhotos] = useState([]);
  const [limit] = useState(10);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchPhotos = async (newOffset) => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      params.append('limit', limit);
      params.append('offset', newOffset);
      const response = await fetch('http://127.0.0.1:8010/photos?' + params.toString());
      if (!response.ok) throw new Error('Could not load photos');
      const data = await response.json();
      setPhotos(data);
      setOffset(newOffset);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Photos</h2>
      <button className="btn" onClick={() => fetchPhotos(0)} disabled={loading}>
        {loading ? 'LOADING...' : 'FETCH PHOTOS'}
      </button>
      {error && <div className="message error">{error}</div>}
      {photos.map((photo) => (
        <div className="message success" key={photo.id}>
          <div className="result-row"><span>id</span><span>{photo.id}</span></div>
          <div className="result-row"><span>owner_id</span><span>{photo.owner_id}</span></div>
          <div className="result-row"><span>filename</span><span>{photo.filename}</span></div>
          <div className="result-row"><span>description</span><span>{photo.description}</span></div>
        </div>
      ))}
      <button className="btn" onClick={() => fetchPhotos(Math.max(0, offset - limit))} disabled={offset === 0}>
        PREVIOUS
      </button>
      <button className="btn" onClick={() => fetchPhotos(offset + limit)}>
        NEXT
      </button>
    </div>
  );
}

export default PhotoListPage;