import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import CreateNotePage from './pages/CreateNotePage';
import NoteListPage from './pages/NoteListPage';
import NoteDetailPage from './pages/NoteDetailPage';
import UpdateNotePage from './pages/UpdateNotePage';
import NoteDeletePage from './pages/NoteDeletePage';
import './App.css';

function App() {
  return (
    <div className="sheet">
      <div className="sheet-header">
        <h1>notes_app</h1>
      </div>
      <UserSignupPage />
      <UserLoginPage />
      <CreateNotePage />
      <NoteListPage />
      <NoteDetailPage />
      <UpdateNotePage />
      <NoteDeletePage />
    </div>
  );
}

export default App;
