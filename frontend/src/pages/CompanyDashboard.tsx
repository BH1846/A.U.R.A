/**
 * Company Dashboard - Overview and analytics for recruiters
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth, useAuthHeader } from '../contexts/AuthContext';

interface Analytics {
  total_applications: number;
  status_breakdown: Record<string, number>;
  aura_completed: number;
  aura_average_score: number;
}

export default function CompanyDashboard() {
  const { user } = useAuth();
  const authHeader = useAuthHeader();
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/company/analytics/overview', {
        headers: authHeader
      });
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user?.name}
          </h1>
          <p className="mt-2 text-gray-600">
            Company Dashboard - {user?.companyName}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Total Applications</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {analytics?.total_applications || 0}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">AURA Completed</p>
            <p className="mt-2 text-3xl font-bold text-blue-600">
              {analytics?.aura_completed || 0}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Average AURA Score</p>
            <p className="mt-2 text-3xl font-bold text-green-600">
              {analytics?.aura_average_score?.toFixed(1) || '0.0'}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Shortlisted</p>
            <p className="mt-2 text-3xl font-bold text-purple-600">
              {analytics?.status_breakdown?.shortlisted || 0}
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Link
            to="/company/internships"
            className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Manage Internships
            </h3>
            <p className="text-gray-600">View and manage your internship postings</p>
          </Link>

          <Link
            to="/company/applications"
            className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              View Applications
            </h3>
            <p className="text-gray-600">Review candidate applications and AURA assessments</p>
          </Link>

          <Link
            to="/company/rankings"
            className="block bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Candidate Rankings
            </h3>
            <p className="text-gray-600">See top candidates ranked by AURA score</p>
          </Link>
        </div>

        {/* Status Breakdown */}
        {analytics?.status_breakdown && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Application Status Breakdown
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(analytics.status_breakdown).map(([status, count]) => (
                <div key={status} className="border rounded-lg p-4">
                  <p className="text-sm text-gray-600 capitalize">
                    {status.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{count}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
