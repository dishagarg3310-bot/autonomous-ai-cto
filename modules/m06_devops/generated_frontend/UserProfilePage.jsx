import React, { useState } from 'react';

function UserProfilePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);

  const fetchUser = async () => {
    setLoading(true);
    setError('');
    setUser(null);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://127.0.0.1:8000/users/me', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed');
      }
      setUser(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>User Profile</h2>
      <button className="btn" onClick={fetchUser} disabled={loading}>
        {loading ? 'LOADING...' : 'LOAD PROFILE'}
      </button>
      {error && <div className="message error">{error}</div>}
      {user && (
        <div className="message success">
          <div className="result-row"><span>ID</span><span>{user.id}</span></div>
          <div className="result-row"><span>Email</span><span>{user.email}</span></div>
        </div>
      )}
    </div>
  );
}

export default UserProfilePage;