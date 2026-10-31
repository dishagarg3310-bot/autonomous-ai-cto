import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import CreateNotePage from './pages/CreateNotePage';
import NoteListPage from './pages/NoteListPage';
import NoteDeletePage from './pages/NoteDeletePage';
import UpdateNotePage from './pages/UpdateNotePage';
import UpdateNotePage2 from './pages/UpdateNotePage2';
import './App.css';

function App() {
  return (
    <div className="sheet">
      <div className="sheet-header">
        <h1>notes_manager</h1>
      </div>
      <UserSignupPage />
      <UserLoginPage />
      <CreateNotePage />
      <NoteListPage />
      <NoteDeletePage />
      <UpdateNotePage />
      <UpdateNotePage2 />
    </div>
  );
}

export default App;
