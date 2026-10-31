import React, { useState } from 'react';

function UserProfilePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const fetchUserProfile = async () => {
    setLoading(true);
    setError('');
    setResult(null);
    try {
      const response = await fetch('http://127.0.0.1:8010/users/me');
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
      <h2>User Profile</h2>
      <button className="btn" onClick={fetchUserProfile} disabled={loading}>
        {loading ? 'LOADING...' : 'LOAD PROFILE'}
      </button>
      {error && <div className="message error">{error}</div>}
      {result && (
        <div className="message success">
          <div className="result-row"><span>id</span><span>{result.id}</span></div>
          <div className="result-row"><span>email</span><span>{result.email}</span></div>
        </div>
      )}
    </div>
  );
}

export default UserProfilePage;