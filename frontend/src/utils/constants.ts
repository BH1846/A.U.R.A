// ============================================================================
// Constants
// Application-wide constants
// ============================================================================

export const APP_NAME = 'AURA';
export const APP_FULL_NAME = 'Automated Understanding & Role Assessment';

export const ROLES = [
  {
    value: 'Frontend',
    label: 'Frontend Developer',
    description: 'React, Vue, Angular, UI/UX',
  },
  {
    value: 'Backend',
    label: 'Backend Developer',
    description: 'Node.js, Python, Java, APIs',
  },
  {
    value: 'FullStack',
    label: 'Full Stack Developer',
    description: 'Frontend + Backend',
  },
  {
    value: 'ML',
    label: 'Machine Learning Engineer',
    description: 'AI, Data Science, ML Models',
  },
  {
    value: 'DevOps',
    label: 'DevOps Engineer',
    description: 'CI/CD, Cloud, Infrastructure',
  },
];

export const STATUS_LABELS = {
  pending: 'Pending',
  analyzing: 'Analyzing Repository',
  questions_ready: 'Questions Ready',
  answering: 'Answering Questions',
  evaluating: 'Evaluating Answers',
  completed: 'Completed',
  error: 'Error',
} as const;

export const DIFFICULTY_LABELS = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
} as const;

export const QUESTION_TYPE_LABELS = {
  WHY: 'Why',
  WHAT: 'What',
  HOW: 'How',
  WHERE: 'Where',
} as const;

export const RECOMMENDATION_LABELS = {
  'Highly Recommended': 'Highly Recommended',
  'Recommended': 'Recommended',
  'Maybe': 'Maybe',
  'Not Recommended': 'Not Recommended',
} as const;

export const AUTO_SAVE_DELAY = 3000; // 3 seconds
export const STATUS_POLL_INTERVAL = 2000; // 2 seconds
export const TOAST_DURATION = 5000; // 5 seconds

export const MIN_ANSWER_LENGTH = 20;
export const MAX_ANSWER_LENGTH = 5000;
