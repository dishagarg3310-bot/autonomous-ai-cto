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

function CreateContactMessagePage() {
  const [values, setValues] = useState({"service_id": "", "message": ""});
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
      let url = "http://127.0.0.1:9100" + "/services/" + encodeURIComponent(values["service_id"]) + "/contact";
      const headers = { 'Content-Type': 'application/json' };
      const token = localStorage.getItem('token');
      if (token) headers['Authorization'] = 'Bearer ' + token;
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ "service_id": values["service_id"], "message": values["message"] }),
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
      <h2>Create Contact Message</h2>
      <p className="panel-hint">Submits a contact message for a service</p>
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>SERVICE ID</label>
          <input type="text" placeholder="e.g. 1" required value={values["service_id"]} onChange={(e) => setField("service_id", e.target.value)} />
        </div>
        <div className="field">
          <label>MESSAGE</label>
          <textarea rows={4} placeholder="Type here..." required value={values["message"]} onChange={(e) => setField("message", e.target.value)} />
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

export default CreateContactMessagePage;
