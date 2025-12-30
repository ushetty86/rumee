import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/App.css';

// Pages (to be created)
// import Dashboard from './pages/Dashboard';
// import NotesPage from './pages/NotesPage';
// import PeoplePage from './pages/PeoplePage';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<div>Welcome to Rumee</div>} />
          {/* Add routes here */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
