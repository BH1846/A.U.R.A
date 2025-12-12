import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Submit } from './pages/Submit';
import { Questions } from './pages/Questions';
import { Report } from './pages/Report';
import { Dashboard } from './pages/Dashboard';
import './styles/globals.css';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit" element={<Submit />} />
          <Route path="/questions/:candidateId" element={<Questions />} />
          <Route path="/report/:candidateId" element={<Report />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
