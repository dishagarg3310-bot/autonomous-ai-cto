import React, { useState } from 'react';

function UpdateNotePage() {
  const [values, setValues] = useState({"id": "", "owner_id": "", "title": "", "content": ""});
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
      let url = "http://127.0.0.1:9100" + "/notes/" + encodeURIComponent(values["id"]);
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) headers['Authorization'] = 'Bearer ' + token;
      const response = await fetch(url, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ "owner_id": values["owner_id"], "title": values["title"], "content": values["content"] }),
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
      <h2>Update Note</h2>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input type="text" value={values["id"]} onChange={(e) => setField("id", e.target.value)} />
        </div>
        <div className="field">
          <label>OWNER ID</label>
          <input type="text" value={values["owner_id"]} onChange={(e) => setField("owner_id", e.target.value)} />
        </div>
        <div className="field">
          <label>TITLE</label>
          <input type="text" value={values["title"]} onChange={(e) => setField("title", e.target.value)} />
        </div>
        <div className="field">
          <label>CONTENT</label>
          <input type="text" value={values["content"]} onChange={(e) => setField("content", e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'WORKING...' : 'SAVE'}
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

export default UpdateNotePage;
