// ============================================================================
// AURA Theme Configuration
// Color palette, gradients, and design tokens
// ============================================================================

export const colors = {
  primary: '#1F7368',
  secondary: '#63D7C7',
  tertiary: '#004F4D',
  softAccent: '#B3EDEB',
  warmAccent: '#FFD187',
  neutralDark: '#181C19',
  neutralLight: '#FFFAF3',
} as const;

export const gradients = {
  primary: 'linear-gradient(135deg, #1F7368 0%, #004F4D 100%)',
  secondary: 'linear-gradient(135deg, #63D7C7 0%, #B3EDEB 100%)',
  warm: 'linear-gradient(135deg, #FFD187 0%, #63D7C7 100%)',
  hero: 'linear-gradient(135deg, #1F7368 0%, #004F4D 100%)',
} as const;

export const spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem',   // 64px
} as const;

export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

export const shadows = {
  soft: '0 4px 20px rgba(31, 115, 104, 0.08)',
  medium: '0 8px 30px rgba(31, 115, 104, 0.12)',
  large: '0 12px 40px rgba(31, 115, 104, 0.16)',
} as const;

// Color utilities
export const getScoreColor = (score: number): string => {
  if (score >= 85) return colors.warmAccent;    // Excellent
  if (score >= 70) return colors.secondary;     // Good
  if (score >= 50) return colors.primary;       // Average
  return '#EF4444';                              // Needs Improvement
};

export const getStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    pending: colors.neutralDark,
    analyzing: colors.secondary,
    questions_ready: colors.primary,
    answering: colors.warmAccent,
    evaluating: colors.secondary,
    completed: colors.primary,
    error: '#EF4444',
  };
  return statusColors[status] || colors.neutralDark;
};

export const questionTypeColors = {
  WHY: 'border-l-4 border-primary',
  WHAT: 'border-l-4 border-secondary',
  HOW: 'border-l-4 border-tertiary',
  WHERE: 'border-l-4 border-warm-accent',
} as const;
