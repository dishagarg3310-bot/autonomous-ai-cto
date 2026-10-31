import React, { useState } from 'react';

const IMAGE_RE = /^(https?:|data:image|[/]).*(png|jpe?g|gif|webp|svg)([?].*)?$/i;

function Value({ v }) {
  if (v === null || v === undefined || v === '') return <span className="muted">-</span>;
  if (Array.isArray(v)) {
    return (
      <div className="chip-list">
        {v.map((x, i) => (typeof x === 'object' && x !== null
          ? <pre className="json" key={i}>{JSON.stringify(x, null, 2)}</pre>
          : <Value v={x} key={i} />))}
      </div>
    );
  }
  if (typeof v === 'object') return <pre className="json">{JSON.stringify(v, null, 2)}</pre>;
  if (typeof v === 'string' && IMAGE_RE.test(v)) return <img className="thumb" src={v} alt="" />;
  return <span className="value-chip">{String(v)}</span>;
}

function Record({ data }) {
  if (data === null || typeof data !== 'object') return <div className="record"><Value v={data} /></div>;
  return (
    <div className="record">
      {Object.entries(data).map(([k, v]) => (
        <div className="result-row" key={k}>
          <span>{k.replace(/_/g, ' ')}</span>
          <Value v={v} />
        </div>
      ))}
    </div>
  );
}

function CreateTaskPage() {
  const [values, setValues] = useState({"user_id": "", "title": "", "completed": "", "created_at": "", "updated_at": ""});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const setField = (key, value) => setValues({ ...values, [key]: value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);
    try {
      let url = "http://127.0.0.1:9100" + "/tasks";
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) headers['Authorization'] = 'Bearer ' + token;
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ "user_id": values["user_id"], "title": values["title"], "completed": values["completed"] === 'true', "created_at": values["created_at"], "updated_at": values["updated_at"] }),
      });
      const text = await response.text();
      let data = {};
      try {
        data = text ? JSON.parse(text) : { status: 'done' };
      } catch (parseError) {
        data = { response: text };
      }
      if (!response.ok) {
        const detail = data && data.detail;
        throw new Error(typeof detail === 'string' ? detail : (response.status === 404 ? 'Not found - check the ID and try again.' : 'Request failed (' + response.status + ')'));
      }
      if (data && data.access_token) localStorage.setItem('token', data.access_token);
      setResult(data);
    } catch (err) {
      setError(err.message === 'Failed to fetch' ? 'Cannot reach the backend. Is it running?' : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h2>Create Task</h2>
      <p className="panel-hint">Adds a new task to the to-do list</p>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>USER ID</label>
          <input type="text" placeholder="e.g. 1" required value={values["user_id"]} onChange={(e) => setField("user_id", e.target.value)} />
        </div>
        <div className="field">
          <label>TITLE</label>
          <input type="text" placeholder="Enter title" required value={values["title"]} onChange={(e) => setField("title", e.target.value)} />
        </div>
        <div className="field">
          <label>COMPLETED</label>
          <input type="text" placeholder="Enter completed" required value={values["completed"]} onChange={(e) => setField("completed", e.target.value)} />
        </div>
        <div className="field">
          <label>CREATED AT</label>
          <input type="text" placeholder="Enter created at" required value={values["created_at"]} onChange={(e) => setField("created_at", e.target.value)} />
        </div>
        <div className="field">
          <label>UPDATED AT</label>
          <input type="text" placeholder="Enter updated at" required value={values["updated_at"]} onChange={(e) => setField("updated_at", e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Working...' : 'Submit'}
        </button>
      </form>
      {error && <div className="message error">{error}</div>}
      {result && Array.isArray(result) && result.length === 0 && (
        <div className="message">Nothing found yet.</div>
      )}
      {result && Array.isArray(result) && result.map((item, i) => (
        <div className="message success" key={i}><Record data={item} /></div>
      ))}
      {result && !Array.isArray(result) && (
        <div className="message success"><Record data={result} /></div>
      )}
    </div>
  );
}

export default CreateTaskPage;
