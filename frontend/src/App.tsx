import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute, StudentRoute, RecruiterRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Submit } from './pages/Submit';
import { Questions } from './pages/Questions';
import { Report } from './pages/Report';
import { Dashboard } from './pages/Dashboard';
import StudentDashboard from './pages/StudentDashboard';
import CompanyDashboard from './pages/CompanyDashboard';
import CompanyApplications from './pages/CompanyApplications';
import JobDescriptionManager from './pages/JobDescriptionManager';
import './styles/globals.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            {/* Public/Standalone AURA Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/submit" element={<Submit />} />
            <Route path="/questions/:candidateId" element={<Questions />} />
            <Route path="/report/:candidateId" element={<Report />} />
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Student Portal Routes (Protected) */}
            <Route element={<StudentRoute />}>
              <Route path="/student/dashboard" element={<StudentDashboard />} />
              <Route path="/student/application/:id" element={<Report />} />
              <Route path="/student/aura/:applicationId/report" element={<Report />} />
            </Route>
            
            {/* Company/Recruiter Portal Routes (Protected) */}
            <Route element={<RecruiterRoute />}>
              <Route path="/company/dashboard" element={<CompanyDashboard />} />
              <Route path="/company/job-descriptions" element={<JobDescriptionManager />} />
              <Route path="/company/applications" element={<CompanyApplications />} />
              <Route path="/company/application/:id" element={<Report />} />
              <Route path="/company/rankings" element={<CompanyApplications />} />
              <Route path="/company/internships" element={<CompanyApplications />} />
            </Route>
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
