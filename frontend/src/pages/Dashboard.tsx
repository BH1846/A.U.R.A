import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { useDashboardStore } from '../store/dashboardStore';
import { getInitials, formatRelativeTime, formatGithubUrl } from '../utils/formatters';
import { getStatusColor } from '../styles/theme';
import { ROLES, STATUS_LABELS } from '../utils/constants';
import { Search, Eye, Trash2, Users, CheckCircle, Clock, AlertCircle } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { candidates, totalCount, filters, loading, fetchCandidates, setFilter, deleteCandidate } = useDashboardStore();

  useEffect(() => {
    fetchCandidates();
  }, []);

  const stats = {
    total: totalCount,
    completed: candidates.filter((c) => c.status === 'completed').length,
    processing: candidates.filter((c) => ['analyzing', 'evaluating'].includes(c.status)).length,
    pending: candidates.filter((c) => c.status === 'pending').length,
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this candidate?')) {
      await deleteCandidate(id);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-light py-8 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-neutral-dark">Recruiter Dashboard</h1>
          <Button variant="primary" onClick={() => navigate('/submit')}>
            Add Candidate
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Users className="w-6 h-6 text-primary" />
              </div>
              <div>
                <p className="text-sm text-neutral-dark/60">Total</p>
                <p className="text-2xl font-bold text-neutral-dark">{stats.total}</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-dark/60">Completed</p>
                <p className="text-2xl font-bold text-neutral-dark">{stats.completed}</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                <Clock className="w-6 h-6 text-secondary" />
              </div>
              <div>
                <p className="text-sm text-neutral-dark/60">Processing</p>
                <p className="text-2xl font-bold text-neutral-dark">{stats.processing}</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-warm-accent/20 flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-warm-accent" />
              </div>
              <div>
                <p className="text-sm text-neutral-dark/60">Pending</p>
                <p className="text-2xl font-bold text-neutral-dark">{stats.pending}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card className="p-6 mb-6">
          <div className="grid md:grid-cols-3 gap-4">
            <Input
              label="Search"
              placeholder="Search by name, email..."
              icon={<Search className="w-5 h-5" />}
              value={filters.search}
              onChange={(e) => setFilter('search', e.target.value)}
            />
            <Select
              label="Filter by Role"
              options={[
                { value: '', label: 'All Roles' },
                ...ROLES.map((r) => ({ value: r.value, label: r.label })),
              ]}
              value={filters.role || ''}
              onChange={(e) => setFilter('role', e.target.value || null)}
            />
          </div>
        </Card>

        {/* Table */}
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-soft-accent/30">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Candidate
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Role
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Repository
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Submitted
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-neutral-dark">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-dark/10">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-neutral-dark/60">
                      Loading candidates...
                    </td>
                  </tr>
                ) : candidates.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-neutral-dark/60">
                      No candidates found
                    </td>
                  </tr>
                ) : (
                  candidates.map((candidate) => (
                    <tr key={candidate.id} className="hover:bg-soft-accent/20 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-semibold">
                            {getInitials(candidate.name)}
                          </div>
                          <div>
                            <p className="font-medium text-neutral-dark">{candidate.name}</p>
                            <p className="text-sm text-neutral-dark/60">{candidate.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Badge variant="primary" size="sm">
                          {candidate.role_type}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <a
                          href={candidate.github_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-primary hover:underline text-sm"
                        >
                          {formatGithubUrl(candidate.github_url)}
                        </a>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2 h-2 rounded-full"
                            style={{ backgroundColor: getStatusColor(candidate.status) }}
                          />
                          <span className="text-sm text-neutral-dark">
                            {STATUS_LABELS[candidate.status]}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-neutral-dark/70">
                        {formatRelativeTime(candidate.created_at)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          {candidate.status === 'completed' && (
                            <button
                              onClick={() => navigate(`/report/${candidate.id}?view=recruiter`)}
                              className="p-2 text-primary hover:bg-primary/10 rounded-lg transition-colors"
                              title="View Report"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(candidate.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
};
