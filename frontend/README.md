# AURA Frontend

Modern, professional TypeScript React frontend for the AURA (Automated Understanding & Role Assessment) platform.

## 🎨 Color Palette

- **Primary**: `#1F7368` - Main brand color
- **Secondary**: `#63D7C7` - Accents and highlights
- **Tertiary**: `#004F4D` - Dark sections
- **Soft Accent**: `#B3EDEB` - Light backgrounds
- **Warm Accent**: `#FFD187` - Success states
- **Neutral Dark**: `#181C19` - Text and borders
- **Neutral Light**: `#FFFAF3` - Page backgrounds

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   └── domain/       # Domain-specific components
│   ├── pages/            # Page components
│   ├── services/         # API and validation
│   ├── store/            # Zustand state management
│   ├── styles/           # Global styles and theme
│   ├── types/            # TypeScript definitions
│   └── utils/            # Helper functions
├── public/
└── index.html
```

## 🎯 Features

- ✅ TypeScript for type safety
- ✅ React 18 with hooks
- ✅ React Router v6 for navigation
- ✅ Zustand for state management
- ✅ React Hook Form + Zod validation
- ✅ TailwindCSS for styling
- ✅ Framer Motion animations
- ✅ Responsive design
- ✅ Accessibility compliant

## 📄 Pages

### 1. Landing Page (`/`)
- Hero section with gradient background
- Feature cards
- CTA sections

### 2. Submit Candidate (`/submit`)
- Form with validation
- GitHub URL verification
- Role selection

### 3. Interview Questions (`/questions/:id`)
- Progress tracking
- Auto-save functionality
- Question navigation

### 4. Evaluation Report (`/report/:id`)
- Score visualization
- Dimensional breakdown
- PDF download

### 5. Recruiter Dashboard (`/dashboard`)
- Candidate list
- Filters and search
- Status tracking

## 🔧 Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npm run lint
```

## 🎨 Component Library

### UI Components
- `Button` - Configurable button with variants
- `Card` - Container component with elevation
- `Input` - Form input with validation
- `Select` - Dropdown select
- `Badge` - Status and label badges
- `ProgressBar` - Progress indicator
- `Spinner` - Loading states

## 🔌 API Integration

All API calls are centralized in `src/services/api.ts`:

```typescript
import { api } from '@/services/api';

// Submit candidate
const { id } = await api.submitCandidate(data);

// Get questions
const questions = await api.getQuestions(candidateId);

// Submit answers
await api.submitAnswers(candidateId, answers);

// Get report
const report = await api.getReport(candidateId);
```

## 🎭 State Management

Using Zustand for global state:

```typescript
import { useCandidateStore } from '@/store/candidateStore';

const { submitCandidate, fetchQuestions } = useCandidateStore();
```

## 📱 Responsive Design

- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px, 1536px
- Optimized for all screen sizes

## ♿ Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation
- Proper ARIA labels
- Focus indicators
- Color contrast ≥ 4.5:1

## 🚀 Deployment

```bash
# Build for production
npm run build

# Output in dist/ directory
```

Deploy the `dist/` folder to any static hosting service (Vercel, Netlify, etc.)

## 📝 License

© 2025 AURA. All rights reserved.
