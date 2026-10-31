import { useState } from 'react';
import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import UserProfilePage from './pages/UserProfilePage';
import CreateBookPage from './pages/CreateBookPage';
import BookListPage from './pages/BookListPage';
import './App.css';

const PAGE_LABELS = {"UserSignupPage": "User Signup", "UserLoginPage": "User Login", "UserProfilePage": "User Profile", "CreateBookPage": "Create Book", "BookListPage": "Book List"};

function App() {
  const [active, setActive] = useState("UserSignupPage");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="dot"></span>
          Book Tracker
        </div>
        <div className="sidebar-section-label">Pages</div>
        <button
          className={"nav-item" + (active === "UserSignupPage" ? " active" : "")}
          onClick={() => setActive("UserSignupPage")}
        >
          <span className="nav-dot"></span>
          User Signup
        </button>
        <button
          className={"nav-item" + (active === "UserLoginPage" ? " active" : "")}
          onClick={() => setActive("UserLoginPage")}
        >
          <span className="nav-dot"></span>
          User Login
        </button>
        <button
          className={"nav-item" + (active === "UserProfilePage" ? " active" : "")}
          onClick={() => setActive("UserProfilePage")}
        >
          <span className="nav-dot"></span>
          User Profile
        </button>
        <button
          className={"nav-item" + (active === "CreateBookPage" ? " active" : "")}
          onClick={() => setActive("CreateBookPage")}
        >
          <span className="nav-dot"></span>
          Create Book
        </button>
        <button
          className={"nav-item" + (active === "BookListPage" ? " active" : "")}
          onClick={() => setActive("BookListPage")}
        >
          <span className="nav-dot"></span>
          Book List
        </button>
      </aside>

      <main className="content">
        <div className="topbar">
          <h1>{PAGE_LABELS[active]}</h1>
          <span className="crumb">Book Tracker</span>
        </div>
        <div className="page-body">
        {active === "UserSignupPage" && <UserSignupPage />}
        {active === "UserLoginPage" && <UserLoginPage />}
        {active === "UserProfilePage" && <UserProfilePage />}
        {active === "CreateBookPage" && <CreateBookPage />}
        {active === "BookListPage" && <BookListPage />}
        </div>
      </main>
    </div>
  );
}

export default App;
