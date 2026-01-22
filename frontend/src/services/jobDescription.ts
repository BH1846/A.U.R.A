/**
 * Job Description API Service
 * Handles all JD-related API calls
 */

export interface JobDescriptionCreate {
  internship_id: number;
  description_text: string;
  required_skills: string[];
  preferred_skills?: string[];
}

export interface JobDescriptionQuestion {
  question_text: string;
  question_type: string;
  difficulty: string;
  context: string;
  expected_keywords: string[];
  evaluation_criteria: string[];
}

export interface JobDescription {
  id: number;
  internship_id: number;
  description_text: string;
  role_type: string;
  required_skills: string[];
  preferred_skills: string[];
  questions_count: number;
  questions: JobDescriptionQuestion[];
  created_at: string;
  updated_at?: string;
  is_active: boolean;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.MODE === 'production' ? '' : 'http://localhost:8000');

export class JobDescriptionService {
  private getAuthHeader(): HeadersInit {
    const token = localStorage.getItem('aura_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  /**
   * Create a new job description and generate questions
   */
  async createJobDescription(data: JobDescriptionCreate): Promise<JobDescription> {
    const response = await fetch(`${API_BASE_URL}/api/company/job-descriptions`, {
      method: 'POST',
      headers: this.getAuthHeader(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create job description');
    }

    return response.json();
  }

  /**
   * Get job description for an internship
   */
  async getJobDescription(internshipId: number): Promise<JobDescription> {
    const response = await fetch(
      `${API_BASE_URL}/api/company/job-descriptions/${internshipId}`,
      {
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to fetch job description');
    }

    return response.json();
  }

  /**
   * Update job description and regenerate questions
   */
  async updateJobDescription(
    internshipId: number,
    data: JobDescriptionCreate
  ): Promise<JobDescription> {
    const response = await fetch(
      `${API_BASE_URL}/api/company/job-descriptions/${internshipId}`,
      {
        method: 'PUT',
        headers: this.getAuthHeader(),
        body: JSON.stringify(data),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update job description');
    }

    return response.json();
  }

  /**
   * Delete/deactivate job description
   */
  async deleteJobDescription(internshipId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/company/job-descriptions/${internshipId}`,
      {
        method: 'DELETE',
        headers: this.getAuthHeader(),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete job description');
    }
  }
}

export const jobDescriptionService = new JobDescriptionService();
