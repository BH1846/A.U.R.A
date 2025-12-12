// ============================================================================
// AURA TypeScript Type Definitions
// Complete type system for the frontend application
// ============================================================================

export interface Role {
  id: number;
  name: string;
  skills: string[];
  description: string;
}

export interface CandidateSubmit {
  name: string;
  email: string;
  github_url: string;
  role_type: string;
}

export type CandidateStatus =
  | 'pending'
  | 'analyzing'
  | 'questions_ready'
  | 'answering'
  | 'evaluating'
  | 'completed'
  | 'error';

export interface Candidate {
  id: number;
  name: string;
  email: string;
  github_url: string;
  role_type: string;
  status: CandidateStatus;
  created_at: string;
  updated_at: string;
}

export type QuestionType = 'WHY' | 'WHAT' | 'HOW' | 'WHERE';
export type Difficulty = 'easy' | 'medium' | 'hard';

export interface Question {
  question_id: number;
  candidate_id?: number;
  question_type: QuestionType;
  question_text: string;
  context: string;
  difficulty: Difficulty;
  created_at?: string;
}

export interface Answer {
  id: number;
  question_id: number;
  answer_text: string;
  time_taken: number;
  created_at: string;
}

export interface AnswerSubmit {
  question_id: number;
  answer_text: string;
  time_taken: number;
}

export interface QuestionScore {
  id: number;
  question_id: number;
  concept_understanding: number;
  technical_depth: number;
  accuracy: number;
  communication: number;
  relevance: number;
  weighted_score: number;
  feedback: string;
  strengths: string[];
  weaknesses: string[];
  fraud_flag: boolean;
  fraud_reason: string | null;
}

export type Recommendation =
  | 'Highly Recommended'
  | 'Recommended'
  | 'Maybe'
  | 'Not Recommended';

export interface FinalScore {
  overall_score: number;
  understanding_score: number;
  reasoning_score: number;
  communication_score: number;
  logic_score: number;
  hire_recommendation: string;
  confidence: number;
}

export interface Repository {
  name: string;
  languages: string[];
  tech_stack: string[];
  summary: string;
}

export interface EvaluationReport {
  candidate: Candidate;
  repository: Repository;
  questions: Question[];
  answers: Answer[];
  question_scores: QuestionScore[];
  final_score: FinalScore;
  report_pdf_path: string | null;
}

export interface CandidateList {
  total: number;
  items: Candidate[];
  page: number;
  pages: number;
}

export interface StatusResponse {
  status: CandidateStatus;
  progress: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
