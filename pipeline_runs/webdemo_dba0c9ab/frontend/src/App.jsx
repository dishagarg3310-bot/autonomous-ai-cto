import { useState } from 'react';
import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import TaskListPage from './pages/TaskListPage';
import CreateTaskPage from './pages/CreateTaskPage';
import UpdateTaskPage from './pages/UpdateTaskPage';
import TaskDeletePage from './pages/TaskDeletePage';
import './App.css';

const PAGE_LABELS = {"UserSignupPage": "User Signup", "UserLoginPage": "User Login", "TaskListPage": "Task List", "CreateTaskPage": "Create Task", "UpdateTaskPage": "Update Task", "TaskDeletePage": "Task Delete"};

function App() {
  const [active, setActive] = useState("UserSignupPage");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="dot"></span>
          Todo App
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
          className={"nav-item" + (active === "TaskListPage" ? " active" : "")}
          onClick={() => setActive("TaskListPage")}
        >
          <span className="nav-dot"></span>
          Task List
        </button>
        <button
          className={"nav-item" + (active === "CreateTaskPage" ? " active" : "")}
          onClick={() => setActive("CreateTaskPage")}
        >
          <span className="nav-dot"></span>
          Create Task
        </button>
        <button
          className={"nav-item" + (active === "UpdateTaskPage" ? " active" : "")}
          onClick={() => setActive("UpdateTaskPage")}
        >
          <span className="nav-dot"></span>
          Update Task
        </button>
        <button
          className={"nav-item" + (active === "TaskDeletePage" ? " active" : "")}
          onClick={() => setActive("TaskDeletePage")}
        >
          <span className="nav-dot"></span>
          Task Delete
        </button>
      </aside>

      <main className="content">
        <div className="topbar">
          <h1>{PAGE_LABELS[active]}</h1>
          <span className="crumb">Todo App</span>
        </div>
        <div className="page-body">
        {active === "UserSignupPage" && <UserSignupPage />}
        {active === "UserLoginPage" && <UserLoginPage />}
        {active === "TaskListPage" && <TaskListPage />}
        {active === "CreateTaskPage" && <CreateTaskPage />}
        {active === "UpdateTaskPage" && <UpdateTaskPage />}
        {active === "TaskDeletePage" && <TaskDeletePage />}
        </div>
      </main>
    </div>
  );
}

export default App;
