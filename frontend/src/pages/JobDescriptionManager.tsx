/**
 * Job Description Manager Page
 * Company recruiters and admins can create/manage JD and generate questions
 */
import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { jobDescriptionService, JobDescription, JobDescriptionCreate } from '../services/jobDescription';

export default function JobDescriptionManager() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const internshipId = searchParams.get('internship_id');

  const [loading, setLoading] = useState(false);
  const [existingJD, setExistingJD] = useState<JobDescription | null>(null);
  const [formData, setFormData] = useState<JobDescriptionCreate>({
    internship_id: internshipId ? parseInt(internshipId) : 0,
    description_text: '',
    required_skills: [],
    preferred_skills: [],
  });
  const [requiredSkillInput, setRequiredSkillInput] = useState('');
  const [preferredSkillInput, setPreferredSkillInput] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [generatedQuestions, setGeneratedQuestions] = useState<any[]>([]);

  useEffect(() => {
    if (internshipId) {
      loadExistingJD(parseInt(internshipId));
    }
  }, [internshipId]);

  const loadExistingJD = async (id: number) => {
    try {
      const jd = await jobDescriptionService.getJobDescription(id);
      setExistingJD(jd);
      setFormData({
        internship_id: id,
        description_text: jd.description_text,
        required_skills: jd.required_skills,
        preferred_skills: jd.preferred_skills,
      });
      setGeneratedQuestions(jd.questions);
    } catch (err: any) {
      // JD doesn't exist yet, that's okay
      console.log('No existing JD found');
    }
  };

  const handleAddRequiredSkill = () => {
    if (requiredSkillInput.trim()) {
      setFormData({
        ...formData,
        required_skills: [...formData.required_skills, requiredSkillInput.trim()],
      });
      setRequiredSkillInput('');
    }
  };

  const handleAddPreferredSkill = () => {
    if (preferredSkillInput.trim()) {
      setFormData({
        ...formData,
        preferred_skills: [...(formData.preferred_skills || []), preferredSkillInput.trim()],
      });
      setPreferredSkillInput('');
    }
  };

  const handleRemoveRequiredSkill = (index: number) => {
    setFormData({
      ...formData,
      required_skills: formData.required_skills.filter((_, i) => i !== index),
    });
  };

  const handleRemovePreferredSkill = (index: number) => {
    setFormData({
      ...formData,
      preferred_skills: formData.preferred_skills?.filter((_, i) => i !== index) || [],
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (!formData.internship_id) {
        throw new Error('Internship ID is required');
      }

      if (!formData.description_text.trim()) {
        throw new Error('Job description text is required');
      }

      if (formData.required_skills.length === 0) {
        throw new Error('At least one required skill is needed');
      }

      let result: JobDescription;
      if (existingJD) {
        // Update existing JD
        result = await jobDescriptionService.updateJobDescription(
          formData.internship_id,
          formData
        );
        setSuccess('Job description updated and questions regenerated successfully!');
      } else {
        // Create new JD
        result = await jobDescriptionService.createJobDescription(formData);
        setSuccess('Job description created and 10 questions generated successfully!');
      }

      setExistingJD(result);
      setGeneratedQuestions(result.questions);
    } catch (err: any) {
      setError(err.message || 'Failed to save job description');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!formData.internship_id || !existingJD) return;

    if (!confirm('Are you sure you want to delete this job description? This will switch the internship back to GitHub-based questions.')) {
      return;
    }

    setLoading(true);
    try {
      await jobDescriptionService.deleteJobDescription(formData.internship_id);
      setSuccess('Job description deleted successfully');
      setExistingJD(null);
      setGeneratedQuestions([]);
      setFormData({
        ...formData,
        description_text: '',
        required_skills: [],
        preferred_skills: [],
      });
    } catch (err: any) {
      setError(err.message || 'Failed to delete job description');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/company/dashboard')}
            className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {existingJD ? 'Edit Job Description' : 'Create Job Description'}
          </h1>
          <p className="mt-2 text-gray-600">
            Generate 10 standardized questions that all candidates will answer
          </p>
        </div>

        {/* Alert Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border-l-4 border-green-500 p-4">
            <p className="text-green-700">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Form */}
          <div>
            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 space-y-6">
              {/* Internship ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Internship ID <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  value={formData.internship_id}
                  onChange={(e) => setFormData({ ...formData, internship_id: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  disabled={!!existingJD}
                />
                <p className="mt-1 text-sm text-gray-500">
                  One job description per internship
                </p>
              </div>

              {/* Job Description Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.description_text}
                  onChange={(e) => setFormData({ ...formData, description_text: e.target.value })}
                  rows={8}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="We are seeking a Backend Developer with expertise in..."
                  required
                />
              </div>

              {/* Required Skills */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Required Skills <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={requiredSkillInput}
                    onChange={(e) => setRequiredSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddRequiredSkill())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Python, FastAPI, PostgreSQL"
                  />
                  <button
                    type="button"
                    onClick={handleAddRequiredSkill}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.required_skills.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemoveRequiredSkill(index)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Preferred Skills */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Skills (Optional)
                </label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={preferredSkillInput}
                    onChange={(e) => setPreferredSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddPreferredSkill())}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Docker, AWS, Redis"
                  />
                  <button
                    type="button"
                    onClick={handleAddPreferredSkill}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.preferred_skills?.map((skill, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => handleRemovePreferredSkill(index)}
                        className="text-gray-600 hover:text-gray-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium"
                >
                  {loading ? 'Generating Questions...' : existingJD ? 'Update & Regenerate Questions' : 'Create & Generate Questions'}
                </button>
                {existingJD && (
                  <button
                    type="button"
                    onClick={handleDelete}
                    disabled={loading}
                    className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 font-medium"
                  >
                    Delete
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Right Column: Generated Questions */}
          <div>
            <div className="bg-white shadow-md rounded-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Generated Questions {generatedQuestions.length > 0 && `(${generatedQuestions.length})`}
              </h2>

              {generatedQuestions.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p>No questions generated yet.</p>
                  <p className="text-sm mt-2">Submit the form to generate 10 questions.</p>
                </div>
              ) : (
                <div className="space-y-4 max-h-[800px] overflow-y-auto">
                  {generatedQuestions.map((q, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-sm font-semibold text-blue-600">
                          Question {index + 1}
                        </span>
                        <div className="flex gap-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            q.question_type === 'why' ? 'bg-purple-100 text-purple-700' :
                            q.question_type === 'what' ? 'bg-blue-100 text-blue-700' :
                            q.question_type === 'how' ? 'bg-green-100 text-green-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>
                            {q.question_type.toUpperCase()}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            q.difficulty === 'easy' ? 'bg-green-100 text-green-700' :
                            q.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            {q.difficulty}
                          </span>
                        </div>
                      </div>
                      <p className="text-gray-900 mb-2">{q.question_text}</p>
                      <p className="text-xs text-gray-500 mb-2">
                        <strong>Context:</strong> {q.context}
                      </p>
                      <div className="text-xs text-gray-600">
                        <strong>Expected Keywords:</strong> {q.expected_keywords.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {generatedQuestions.length > 0 && (
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    ✅ <strong>All candidates</strong> applying to this internship will answer these exact 10 questions.
                  </p>
                  <p className="text-sm text-blue-700 mt-2">
                    This ensures fair comparison and consistent evaluation across all applicants.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
