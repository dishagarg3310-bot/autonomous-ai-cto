import React, { useState } from 'react';

function CreatePhotoPage() {
  const [ownerId, setOwnerId] = useState('');
  const [filename, setFilename] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch('http://127.0.0.1:8010/photos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner_id: ownerId, filename, description }),
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
      <h2>Create photo</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>OWNER ID</label>
          <input value={ownerId} onChange={(e) => setOwnerId(e.target.value)} required />
        </div>
        <div className="field">
          <label>FILENAME</label>
          <input value={filename} onChange={(e) => setFilename(e.target.value)} required />
        </div>
        <div className="field">
          <label>DESCRIPTION</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'SAVING...' : 'SAVE'}
        </button>
      </form>
      {error && <div className="message error">{error}</div>}
      {result && (
        <div className="message success">
          <div className="result-row"><span>id</span><span>{result.id}</span></div>
          <div className="result-row"><span>owner_id</span><span>{result.owner_id}</span></div>
          <div className="result-row"><span>filename</span><span>{result.filename}</span></div>
          <div className="result-row"><span>description</span><span>{result.description}</span></div>
        </div>
      )}
    </div>
  );
}

export default CreatePhotoPage;