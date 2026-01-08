/**
 * Student Dashboard - View applications and AURA assessments
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth, useAuthHeader } from '../contexts/AuthContext';

interface Application {
  id: number;
  internship: {
    id: number;
    title: string;
    company_name: string;
    role_type: string;
    location: string;
    aura_enabled: boolean;
    aura_required: boolean;
  };
  status: string;
  applied_at: string;
  aura?: {
    completed: boolean;
    in_progress?: boolean;
    score?: number;
    completed_at?: string;
  };
}

export default function StudentDashboard() {
  const { user } = useAuth();
  const authHeader = useAuthHeader();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      console.log('Auth header:', authHeader);
      console.log('Making request to /api/student/applications');
      
      const response = await fetch('/api/student/applications', {
        headers: {
          'Content-Type': 'application/json',
          ...authHeader
        },
        credentials: 'include'
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        setApplications(data.items);
      } else {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
      }
    } catch (error) {
      console.error('Failed to fetch applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-gray-100 text-gray-800',
      aura_invited: 'bg-blue-100 text-blue-800',
      aura_in_progress: 'bg-yellow-100 text-yellow-800',
      aura_completed: 'bg-green-100 text-green-800',
      shortlisted: 'bg-purple-100 text-purple-800',
      rejected: 'bg-red-100 text-red-800',
      accepted: 'bg-green-100 text-green-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
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
            Track your internship applications and AURA assessments
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Total Applications</p>
            <p className="mt-2 text-3xl font-bold text-gray-900">
              {applications.length}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">AURA Completed</p>
            <p className="mt-2 text-3xl font-bold text-green-600">
              {applications.filter(app => app.aura?.completed).length}
            </p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Pending Assessments</p>
            <p className="mt-2 text-3xl font-bold text-blue-600">
              {applications.filter(app => app.status === 'aura_invited' && !app.aura?.completed).length}
            </p>
          </div>
        </div>

        {/* Applications List */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">My Applications</h2>
          </div>

          <div className="divide-y divide-gray-200">
            {applications.map((app) => (
              <div key={app.id} className="p-6 hover:bg-gray-50 transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {app.internship.title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-600">
                      {app.internship.company_name} • {app.internship.role_type} • {app.internship.location}
                    </p>
                    <div className="mt-3 flex items-center gap-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(app.status)}`}>
                        {app.status.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-gray-500">
                        Applied {new Date(app.applied_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="ml-6 flex flex-col items-end gap-2">
                    {/* AURA Status */}
                    {app.internship.aura_enabled && (
                      <div className="text-right">
                        {app.aura?.completed ? (
                          <>
                            <div className="text-sm text-gray-600">AURA Score</div>
                            <div className="text-2xl font-bold text-green-600">
                              {app.aura.score?.toFixed(1)}
                            </div>
                            <Link
                              to={`/student/aura/${app.id}/report`}
                              className="mt-2 text-sm text-blue-600 hover:text-blue-700"
                            >
                              View Report →
                            </Link>
                          </>
                        ) : app.status === 'aura_invited' ? (
                          <Link
                            to={`/?application=${app.id}`} // Redirect to AURA assessment flow
                            className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                          >
                            Start AURA Assessment
                          </Link>
                        ) : app.aura?.in_progress ? (
                          <span className="text-sm text-yellow-600">Assessment in progress...</span>
                        ) : null}
                      </div>
                    )}

                    {/* View Details */}
                    <Link
                      to={`/student/application/${app.id}`}
                      className="text-sm text-gray-600 hover:text-gray-700"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              </div>
            ))}

            {applications.length === 0 && (
              <div className="text-center py-12 text-gray-500">
                <p className="mb-4">No applications yet</p>
                <p className="text-sm">
                  Apply to internships on I-Intern to see them here
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
