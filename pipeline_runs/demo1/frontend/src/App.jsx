import UserSignupPage from './pages/UserSignupPage';
import UserLoginPage from './pages/UserLoginPage';
import CreatePhotoPage from './pages/CreatePhotoPage';
import PhotoListPage from './pages/PhotoListPage';
import PhotoDetailPage from './pages/PhotoDetailPage';
import CreateCommentPage from './pages/CreateCommentPage';
import CommentListPage from './pages/CommentListPage';
import './App.css';

function App() {
  return (
    <div className="sheet">
      <div className="sheet-header">
        <h1>photo_sharing</h1>
      </div>
      <UserSignupPage />
      <UserLoginPage />
      <CreatePhotoPage />
      <PhotoListPage />
      <PhotoDetailPage />
      <CreateCommentPage />
      <CommentListPage />
    </div>
  );
}

export default App;
