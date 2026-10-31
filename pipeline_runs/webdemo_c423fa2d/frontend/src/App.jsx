import { useEffect, useState } from 'react';
import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import UserProfilePage from './pages/UserProfilePage';
import EmployeeListPage from './pages/EmployeeListPage';
import CreateEmployeePage from './pages/CreateEmployeePage';
import EmployeeDetailPage from './pages/EmployeeDetailPage';
import UpdateEmployeePage from './pages/UpdateEmployeePage';
import EmployeeDeletePage from './pages/EmployeeDeletePage';
import './App.css';

const DATA = {"project": "Employee Management", "multi": true, "dashboards": [{"id": "admin", "role": "admin", "title": "Admin Dashboard", "icon": "🛡️", "blurb": "Manage everything: add, edit and remove records.", "pages": ["EmployeeListPage", "CreateEmployeePage", "EmployeeDetailPage", "UpdateEmployeePage", "EmployeeDeletePage"], "account": ["UserSignupPage", "UserLoginPage", "UserProfilePage"], "tint": null}, {"id": "employee", "role": "employee", "title": "Employee Dashboard", "icon": "🧑‍🔧", "blurb": "View records and manage your own profile.", "pages": ["EmployeeListPage", "EmployeeDetailPage"], "account": ["UserSignupPage", "UserLoginPage", "UserProfilePage"], "tint": {"--accent": "#14b8a6", "--accent-2": "#22d3ee", "--accent-grad": "linear-gradient(135deg, #14b8a6 0%, #22d3ee 100%)", "--accent-rgb": "20,184,166", "--accent2-rgb": "34,211,238", "--bg-glow": "#0a2a2c"}}], "me": "http://127.0.0.1:9100/users/me", "labels": {"UserSignupPage": "User Signup", "UserLoginPage": "User Login", "UserProfilePage": "User Profile", "EmployeeListPage": "Employee List", "CreateEmployeePage": "Create Employee", "EmployeeDetailPage": "Employee Detail", "UpdateEmployeePage": "Update Employee", "EmployeeDeletePage": "Employee Delete"}, "descriptions": {"UserSignupPage": "Creates a new user account with a hashed password and role", "UserLoginPage": "Logs in a user and returns a JWT access token", "UserProfilePage": "Returns the currently logged-in user's information", "EmployeeListPage": "Lists all employees with pagination", "CreateEmployeePage": "Adds a new employee", "EmployeeDetailPage": "Views the details of an existing employee", "UpdateEmployeePage": "Edits the details of an existing employee Only changed fields need to be sent - fields lef", "EmployeeDeletePage": "Deletes an existing employee"}};
const PAGES = { UserSignupPage, UserLoginPage, UserProfilePage, EmployeeListPage, CreateEmployeePage, EmployeeDetailPage, UpdateEmployeePage, EmployeeDeletePage };
const store = {
  get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { v === null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) { /* storage unavailable */ } },
};

function Overview({ dash, go }) {
  const tools = [...dash.pages, ...dash.account];
  return (
    <div className="overview">
      <div className="panel welcome">
        <h2>{DATA.multi ? 'Welcome to the ' + dash.title : 'Welcome to ' + DATA.project}</h2>
        <p className="panel-hint">{dash.blurb}</p>
        <div className="stat-row">
          <div><b>{dash.pages.length}</b><span>Tools</span></div>
          <div><b>{DATA.multi ? dash.role : 'Everyone'}</b><span>Access level</span></div>
        </div>
      </div>
      <div className="quick-grid">
        {tools.map((n) => (
          <button key={n} className="quick-card" onClick={() => go(n)}>
            <b>{DATA.labels[n]}</b>
            <span>{DATA.descriptions[n] || 'Open this page'}</span>
            <i>Open &rarr;</i>
          </button>
        ))}
      </div>
    </div>
  );
}

function Gate({ onPick }) {
  return (
    <div className="gate">
      <h1>{DATA.project}</h1>
      <p className="muted">Choose your dashboard</p>
      <div className="gate-grid">
        {DATA.dashboards.map((d) => (
          <button key={d.id} className="gate-card" style={d.tint || undefined} onClick={() => onPick(d.id)}>
            <span className="gate-ico">{d.icon}</span>
            <b>{d.title}</b>
            <span>{d.blurb}</span>
            <i>Enter &rarr;</i>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const first = DATA.multi ? null : DATA.dashboards[0].id;
  const saved = store.get('dash');
  const [dashId, setDashId] = useState(DATA.dashboards.some((d) => d.id === saved) ? saved : first);
  const [page, setPage] = useState('overview');
  const [locked, setLocked] = useState(null);
  const [token, setToken] = useState(store.get('token'));

  const choose = (id) => { setDashId(id); setPage('overview'); store.set('dash', id); };

  // Logged in? Ask the backend who we are and open the dashboard that matches the role.
  useEffect(() => {
    const t = store.get('token');
    setToken(t);
    if (!DATA.me || !t) return;
    fetch(DATA.me, { headers: { Authorization: 'Bearer ' + t } })
      .then((r) => (r.ok ? r.json() : null))
      .then((u) => {
        const role = u && typeof u.role === 'string' ? u.role.toLowerCase() : '';
        const hit = role && DATA.dashboards.find((d) => role.includes(d.id) || d.id.includes(role));
        if (hit) { setLocked(hit.id); setDashId(hit.id); }
      })
      .catch(() => {});
  }, [page]);

  const dash = DATA.dashboards.find((d) => d.id === dashId);
  if (!dash) return <Gate onPick={choose} />;
  const navBtn = (n) => (
    <button key={n} className={'nav-item' + (page === n ? ' active' : '')} onClick={() => setPage(n)}>
      <span className="nav-dot"></span>{DATA.labels[n]}
    </button>
  );
  const Current = PAGES[page];
  return (
    <div className="app-shell" style={dash.tint || undefined}>
      <aside className="sidebar">
        <div className="sidebar-brand"><span className="dot"></span>{DATA.project}</div>
        {DATA.multi && <div className="role-badge">{dash.title}</div>}
        <button className={'nav-item' + (page === 'overview' ? ' active' : '')} onClick={() => setPage('overview')}>
          <span className="nav-dot"></span>Overview
        </button>
        <div className="sidebar-section-label">{DATA.multi ? 'Tools' : 'Pages'}</div>
        {dash.pages.map(navBtn)}
        {dash.account.length > 0 && <div className="sidebar-section-label">Account</div>}
        {dash.account.map(navBtn)}
        {DATA.multi && !locked && (
          <button className="nav-item switch" onClick={() => { setDashId(null); store.set('dash', null); }}>Switch dashboard</button>
        )}
        {token && (
          <button className="nav-item signout" onClick={() => { store.set('token', null); setToken(null); setLocked(null); }}>Sign out</button>
        )}
      </aside>
      <main className="content">
        <div className="topbar">
          <h1>{page === 'overview' ? 'Overview' : DATA.labels[page]}</h1>
          <span className="crumb">{DATA.multi ? dash.title : DATA.project}</span>
        </div>
        <div className="page-body">
          {page === 'overview' ? <Overview dash={dash} go={setPage} /> : Current ? <Current /> : null}
        </div>
      </main>
    </div>
  );
}
