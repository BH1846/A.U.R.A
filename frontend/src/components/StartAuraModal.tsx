/**
 * Start AURA Assessment Modal
 * Supports both JD-based and GitHub-based questions
 */
import { useState } from 'react';

interface StartAuraModalProps {
  applicationId: number;
  internshipTitle: string;
  requiresGithub: boolean; // false if JD questions available
  onClose: () => void;
  onSuccess: () => void;
}

export default function StartAuraModal({
  applicationId,
  internshipTitle,
  requiresGithub,
  onClose,
  onSuccess,
}: StartAuraModalProps) {
  const [githubUrl, setGithubUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleStart = async () => {
    if (requiresGithub && !githubUrl.trim()) {
      setError('GitHub URL is required for this assessment');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('aura_token');
      const response = await fetch(`/api/student/aura/${applicationId}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          github_url: githubUrl || undefined,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start assessment');
      }

      const result = await response.json();
      
      // Show success message based on question source
      if (result.question_source === 'job_description') {
        alert('✅ AURA assessment started! Questions are ready. You can start answering now.');
      } else {
        alert('✅ AURA assessment started! Processing your GitHub repository. This may take a few minutes. Please refresh the page in a moment.');
      }

      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Failed to start assessment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Start AURA Assessment
        </h2>
        
        <p className="text-gray-600 mb-4">
          For: <strong>{internshipTitle}</strong>
        </p>

        {!requiresGithub && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">
              ✅ <strong>Job Description Questions Ready!</strong>
            </p>
            <p className="text-green-700 text-sm mt-1">
              You'll answer 10 standardized questions about the job requirements. 
              No GitHub repository needed.
            </p>
          </div>
        )}

        {requiresGithub && (
          <>
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800 text-sm">
                📂 <strong>GitHub-Based Assessment</strong>
              </p>
              <p className="text-blue-700 text-sm mt-1">
                Provide your GitHub repository URL. We'll analyze your code and generate personalized questions.
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Repository URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/username/repo"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={loading}
              />
            </div>
          </>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleStart}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium"
          >
            {loading ? 'Starting...' : 'Start Assessment'}
          </button>
          <button
            onClick={onClose}
            disabled={loading}
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:bg-gray-100"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
