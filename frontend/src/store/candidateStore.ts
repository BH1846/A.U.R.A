// ============================================================================
// Candidate Store
// Zustand store for candidate-related state
// ============================================================================

import { create } from 'zustand';
import type { Candidate, Question, AnswerSubmit, CandidateSubmit } from '../types';
import api from '../services/api';

interface CandidateStore {
  currentCandidate: Candidate | null;
  questions: Question[];
  answers: Map<number, string>;
  loading: boolean;
  error: string | null;
  
  submitCandidate: (data: CandidateSubmit) => Promise<number>;
  fetchCandidate: (id: number) => Promise<void>;
  fetchQuestions: (id: number) => Promise<void>;
  saveAnswer: (questionId: number, answer: string) => void;
  submitAllAnswers: (candidateId: number) => Promise<void>;
  reset: () => void;
}

export const useCandidateStore = create<CandidateStore>((set, get) => ({
  currentCandidate: null,
  questions: [],
  answers: new Map(),
  loading: false,
  error: null,

  submitCandidate: async (data: CandidateSubmit) => {
    set({ loading: true, error: null });
    try {
      const response = await api.submitCandidate(data);
      return response.id;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to submit candidate';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  fetchCandidate: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const candidate = await api.getCandidate(id);
      set({ currentCandidate: candidate });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch candidate';
      set({ error: errorMessage });
    } finally {
      set({ loading: false });
    }
  },

  fetchQuestions: async (id: number) => {
    set({ loading: true, error: null });
    try {
      const questions = await api.getQuestions(id);
      set({ questions });
      
      // Load saved answers from localStorage
      const savedAnswers = new Map<number, string>();
      questions.forEach((q) => {
        const saved = localStorage.getItem(`answer_${q.question_id}`);
        if (saved) {
          savedAnswers.set(q.question_id, saved);
        }
      });
      set({ answers: savedAnswers });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch questions';
      set({ error: errorMessage });
    } finally {
      set({ loading: false });
    }
  },

  saveAnswer: (questionId: number, answer: string) => {
    const { answers } = get();
    const newAnswers = new Map(answers);
    newAnswers.set(questionId, answer);
    set({ answers: newAnswers });
    
    // Save to localStorage
    localStorage.setItem(`answer_${questionId}`, answer);
  },

  submitAllAnswers: async (candidateId: number) => {
    const { answers, questions } = get();
    set({ loading: true, error: null });
    
    try {
      const answerSubmits: AnswerSubmit[] = questions
        .filter((q) => answers.get(q.question_id)) // Only submit answered questions
        .map((q) => {
          const answerObj = {
            question_id: q.question_id,
            answer_text: answers.get(q.question_id) || '',
            time_taken: 0,
          };
          console.log('Mapping question', q.question_id, 'to answer:', answerObj);
          return answerObj;
        });

      if (answerSubmits.length === 0) {
        throw new Error('Please answer at least one question before submitting');
      }

      console.log('Submitting answers:', JSON.stringify(answerSubmits, null, 2));
      console.log('Raw array:', answerSubmits);
      await api.submitAnswers(candidateId, answerSubmits);
      
      // Clear localStorage
      questions.forEach((q) => {
        localStorage.removeItem(`answer_${q.question_id}`);
      });
      
      set({ answers: new Map() });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to submit answers';
      set({ error: errorMessage });
      throw error;
    } finally {
      set({ loading: false });
    }
  },

  reset: () => {
    set({
      currentCandidate: null,
      questions: [],
      answers: new Map(),
      loading: false,
      error: null,
    });
  },
}));
