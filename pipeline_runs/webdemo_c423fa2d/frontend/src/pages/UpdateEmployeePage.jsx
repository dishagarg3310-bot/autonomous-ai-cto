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

function UpdateEmployeePage() {
  const [values, setValues] = useState({"name": "", "email": "", "department": "", "job_title": "", "user_id": ""});
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
      let url = "http://127.0.0.1:9100" + "/employees/" + encodeURIComponent(values["user_id"]);
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) headers['Authorization'] = 'Bearer ' + token;
      const response = await fetch(url, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ "name": values["name"], "email": values["email"], "department": values["department"], "job_title": values["job_title"], "user_id": values["user_id"] }),
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
      <h2>Update Employee</h2>
      <p className="panel-hint">Edits the details of an existing employee Only changed fields need to be sent - fields left unchanged on the backend are preserved.</p>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>NAME</label>
          <input type="text" placeholder="Enter name" required value={values["name"]} onChange={(e) => setField("name", e.target.value)} />
        </div>
        <div className="field">
          <label>EMAIL</label>
          <input type="text" placeholder="Enter email" required value={values["email"]} onChange={(e) => setField("email", e.target.value)} />
        </div>
        <div className="field">
          <label>DEPARTMENT</label>
          <input type="text" placeholder="Enter department" required value={values["department"]} onChange={(e) => setField("department", e.target.value)} />
        </div>
        <div className="field">
          <label>JOB TITLE</label>
          <input type="text" placeholder="Enter job title" required value={values["job_title"]} onChange={(e) => setField("job_title", e.target.value)} />
        </div>
        <div className="field">
          <label>USER ID</label>
          <input type="text" placeholder="e.g. 1" required value={values["user_id"]} onChange={(e) => setField("user_id", e.target.value)} />
        </div>
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Working...' : 'Save'}
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

export default UpdateEmployeePage;
