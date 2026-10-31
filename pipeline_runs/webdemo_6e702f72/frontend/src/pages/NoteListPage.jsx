import React, { useState } from 'react';

function NoteListPage() {
  const [values, setValues] = useState({"limit": "", "offset": ""});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const setField = (key, value) => setValues({ ...values, [key]: value });

  const rows = (obj) =>
    Object.entries(obj || {}).map(([k, v]) => (
      <div className="result-row" key={k}>
        <span>{k}</span>
        <span>{typeof v === 'object' && v !== null ? JSON.stringify(v) : String(v)}</span>
      </div>
    ));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      let url = "http://127.0.0.1:9100" + "/notes";
      const params = new URLSearchParams();
      if (values["limit"]) params.append("limit", values["limit"]);
      if (values["offset"]) params.append("offset", values["offset"]);
      if (params.toString()) url += '?' + params.toString();
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) headers['Authorization'] = 'Bearer ' + token;
      const response = await fetch(url, {
        method: 'GET',
        headers,
      });
      const text = await response.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : { status: 'done' };
      } catch (parseError) {
        data = { response: text };
      }
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed');
      }
      if (data && data.access_token) localStorage.setItem('token', data.access_token);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Note List</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>LIMIT</label>
          <input type="text" value={values["limit"]} onChange={(e) => setField("limit", e.target.value)} />
        </div>
        <div className="field">
          <label>OFFSET</label>
          <input type="text" value={values["offset"]} onChange={(e) => setField("offset", e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'WORKING...' : 'LOAD'}
        </button>
      </form>
      {error && <div className="message error">{error}</div>}
      {result && Array.isArray(result) && result.map((item, i) => (
        <div className="message success" key={i}>{rows(item)}</div>
      ))}
      {result && !Array.isArray(result) && (
        <div className="message success">{rows(result)}</div>
      )}
    </div>
  );
}

export default NoteListPage;
