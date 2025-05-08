import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { UserPlanProvider } from './context/UserPlanContext';
import { AdminDesignUploader } from './components/admin/AdminDesignUploader';
import { FintechRoutes } from './fintech/FintechRoutes';
import './App.css';

function App() {
  return (
    <UserPlanProvider>
      <Router>
        <div className="app">
          <header className="app-header">
            <h1>SoulCoreHub</h1>
            <nav>
              <ul>
                <li><Link to="/">Dashboard</Link></li>
                <li><Link to="/designs">Designs</Link></li>
                <li><Link to="/fintech">Market Whisperer</Link></li>
                <li><Link to="/settings">Settings</Link></li>
              </ul>
            </nav>
          </header>
          
          <main className="app-main">
            <Routes>
              <Route path="/" element={
                <section className="admin-section">
                  <h2>Welcome to SoulCoreHub</h2>
                  <p>Select a module from the navigation menu to get started.</p>
                </section>
              } />
              <Route path="/designs" element={
                <section className="admin-section">
                  <h2>Design Management</h2>
                  <AdminDesignUploader />
                </section>
              } />
              <Route path="/fintech/*" element={<FintechRoutes />} />
              <Route path="/settings" element={
                <section className="admin-section">
                  <h2>Settings</h2>
                  <p>Account settings and preferences.</p>
                </section>
              } />
            </Routes>
          </main>
          
          <footer className="app-footer">
            <p>© 2025 SoulCoreHub, All Rights Reserved.</p>
            <p>Created by Helo Im AI Inc. Est. 2024</p>
          </footer>
        </div>
      </Router>
    </UserPlanProvider>
  );
}

export default App;
