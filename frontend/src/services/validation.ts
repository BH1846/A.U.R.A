// ============================================================================
// AURA Validation Schemas
// Zod schemas for form validation
// ============================================================================

import { z } from 'zod';

export const candidateSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),
  
  email: z
    .string()
    .email('Invalid email address')
    .toLowerCase(),
  
  github_url: z
    .string()
    .url('Invalid URL format')
    .refine(
      (url) => url.includes('github.com'),
      'Must be a GitHub repository URL'
    ),
  
  role_type: z.enum(['Frontend', 'Backend', 'ML', 'DevOps', 'FullStack'], {
    errorMap: () => ({ message: 'Please select a valid role' }),
  }),
});

export type CandidateFormData = z.infer<typeof candidateSchema>;

export const answerSchema = z.object({
  question_id: z.number(),
  answer_text: z
    .string()
    .min(20, 'Answer must be at least 20 characters')
    .max(5000, 'Answer must be less than 5000 characters'),
  time_taken: z.number().min(0),
});

export type AnswerFormData = z.infer<typeof answerSchema>;
