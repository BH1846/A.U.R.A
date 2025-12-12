// ============================================================================
// AURA API Service
// Centralized API client with all backend endpoints
// ============================================================================

import axios, { AxiosInstance } from 'axios';
import type {
  Role,
  Candidate,
  CandidateSubmit,
  CandidateList,
  Question,
  AnswerSubmit,
  EvaluationReport,
  StatusResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds - increased for database queries
    });

    // Request interceptor for debugging
    this.client.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url, config.data);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          console.error('API Error:', error.response.status, error.response.data);
          console.error('Request that failed:', error.config?.data);
        } else if (error.request) {
          console.error('Network Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // ============================================================================
  // Role Management
  // ============================================================================

  async getRoles(): Promise<Role[]> {
    const response = await this.client.get<Role[]>('/roles');
    return response.data;
  }

  // ============================================================================
  // Candidate Management
  // ============================================================================

  async submitCandidate(data: CandidateSubmit): Promise<{ id: number; status: string }> {
    const response = await this.client.post<{ candidate_id: number; status: string; message: string }>(
      '/candidate/submit',
      data
    );
    // Map backend response (candidate_id) to frontend expectation (id)
    return { id: response.data.candidate_id, status: response.data.status };
  }

  async getCandidate(id: number): Promise<Candidate> {
    const response = await this.client.get<Candidate>(`/candidate/${id}`);
    return response.data;
  }

  async getCandidates(params?: {
    skip?: number;
    limit?: number;
    role?: string;
  }): Promise<CandidateList> {
    const response = await this.client.get<CandidateList>('/candidates', { params });
    return response.data;
  }

  async deleteCandidate(id: number): Promise<void> {
    await this.client.delete(`/candidate/${id}`);
  }

  // ============================================================================
  // Question & Answer Flow
  // ============================================================================

  async getQuestions(candidateId: number): Promise<Question[]> {
    const response = await this.client.get<Question[]>(`/candidate/${candidateId}/questions`);
    return response.data;
  }

  async submitAnswers(
    candidateId: number,
    answers: AnswerSubmit[]
  ): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>(
      `/candidate/${candidateId}/answers`,
      { answers }
    );
    return response.data;
  }

  // ============================================================================
  // Evaluation & Report
  // ============================================================================

  async getCandidateStatus(candidateId: number): Promise<StatusResponse> {
    const response = await this.client.get<StatusResponse>(`/candidate/${candidateId}/status`);
    return response.data;
  }

  async getReport(candidateId: number): Promise<EvaluationReport> {
    const response = await this.client.get<EvaluationReport>(`/candidate/${candidateId}/report`);
    return response.data;
  }

  async downloadReport(candidateId: number): Promise<Blob> {
    const response = await this.client.get(`/candidate/${candidateId}/report/download`, {
      responseType: 'blob',
    });
    return response.data;
  }
}

export const api = new ApiService();
export default api;
