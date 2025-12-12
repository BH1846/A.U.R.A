import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ProgressBar } from '../components/ui/ProgressBar';
import { Badge } from '../components/ui/Badge';
import { LoadingScreen } from '../components/ui/Spinner';
import { useCandidateStore } from '../store/candidateStore';
import { questionTypeColors } from '../styles/theme';
import { ChevronLeft, ChevronRight, CheckCircle, Save } from 'lucide-react';

const MIN_ANSWER_LENGTH = 20;
const AUTO_SAVE_DELAY = 3000;

export const Questions: React.FC = () => {
  const { candidateId } = useParams<{ candidateId: string }>();
  const navigate = useNavigate();
  const {
    questions,
    answers,
    loading,
    fetchQuestions,
    saveAnswer,
    submitAllAnswers,
  } = useCandidateStore();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [localAnswer, setLocalAnswer] = useState('');
  const [isSaved, setIsSaved] = useState(true);

  useEffect(() => {
    if (candidateId) {
      fetchQuestions(parseInt(candidateId));
    }
  }, [candidateId, fetchQuestions]);

  useEffect(() => {
    if (questions.length > 0) {
      const questionId = questions[currentIndex].question_id;
      setLocalAnswer(answers.get(questionId) || '');
    }
  }, [currentIndex, questions, answers]);

  // Auto-save with debounce
  useEffect(() => {
    if (!questions.length) return;
    
    const timer = setTimeout(() => {
      if (localAnswer) {
        saveAnswer(questions[currentIndex].question_id, localAnswer);
        setIsSaved(true);
      }
    }, AUTO_SAVE_DELAY);

    setIsSaved(false);
    return () => clearTimeout(timer);
  }, [localAnswer, currentIndex, questions, saveAnswer]);

  if (loading || questions.length === 0) {
    return <LoadingScreen message="Loading questions..." />;
  }

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + 1) / questions.length) * 100;
  const allAnswered = questions.every((q) => answers.get(q.question_id)?.trim());
  const currentAnswerLength = localAnswer.length;

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = async () => {
    if (!candidateId) return;
    
    try {
      await submitAllAnswers(parseInt(candidateId));
      navigate(`/report/${candidateId}`);
    } catch (error: any) {
      console.error('Failed to submit answers:', error);
      console.error('Error response:', error.response?.data);
      const errorDetail = error.response?.data?.detail;
      const errorMsg = Array.isArray(errorDetail) 
        ? JSON.stringify(errorDetail, null, 2)
        : errorDetail || error.message;
      alert(`Failed to submit:\n${errorMsg}`);
    }
  };

  return (
    <div className="bg-neutral-light py-8 px-6 pb-32">
      <div className="max-w-4xl mx-auto">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-3">
            <h1 className="text-2xl font-bold text-neutral-dark">
              Interview Questions
            </h1>
            <div className="flex items-center gap-2">
              {isSaved ? (
                <div className="flex items-center gap-1 text-secondary text-sm">
                  <CheckCircle className="w-4 h-4" />
                  Saved
                </div>
              ) : (
                <div className="flex items-center gap-1 text-neutral-dark/40 text-sm">
                  <Save className="w-4 h-4 animate-pulse" />
                  Saving...
                </div>
              )}
            </div>
          </div>
          <ProgressBar
            value={currentIndex + 1}
            max={questions.length}
            showLabel
          />
          <p className="text-sm text-neutral-dark/60 mt-2">
            Question {currentIndex + 1} of {questions.length}
          </p>
        </div>

        {/* Question Card */}
        <Card variant="elevated" padding="lg" className={`mb-6 ${questionTypeColors[currentQuestion.question_type]}`}>
          <div className="flex items-start justify-between mb-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-lg">
                {currentIndex + 1}
              </div>
              <div>
                <div className="flex gap-2 mb-2">
                  <Badge variant="primary" size="sm">
                    {currentQuestion.question_type}
                  </Badge>
                  <Badge variant="neutral" size="sm">
                    {currentQuestion.difficulty}
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-semibold text-neutral-dark mb-4">
            {currentQuestion.question_text}
          </h2>

          {currentQuestion.context && (
            <div className="bg-tertiary/5 rounded-xl p-4 mb-6">
              <p className="text-sm font-medium text-neutral-dark/70 mb-2">
                Context:
              </p>
              <code className="text-sm text-neutral-dark/90 whitespace-pre-wrap">
                {currentQuestion.context}
              </code>
            </div>
          )}

          {/* Answer Textarea */}
          <div>
            <label className="block text-sm font-medium text-neutral-dark mb-2">
              Your Answer
            </label>
            <textarea
              value={localAnswer}
              onChange={(e) => setLocalAnswer(e.target.value)}
              placeholder="Type your answer here... (minimum 20 characters)"
              className="w-full px-4 py-3 rounded-xl border border-neutral-dark/20 bg-white text-neutral-dark 
                       placeholder-neutral-dark/40 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                       transition-all duration-200 min-h-[200px] resize-y"
              rows={8}
            />
            <div className="flex justify-between items-center mt-2">
              <p className="text-sm text-neutral-dark/60">
                {currentAnswerLength < MIN_ANSWER_LENGTH ? (
                  <span className="text-red-500">
                    Need {MIN_ANSWER_LENGTH - currentAnswerLength} more characters
                  </span>
                ) : (
                  <span className="text-secondary">
                    {currentAnswerLength} characters
                  </span>
                )}
              </p>
            </div>
          </div>
        </Card>

        {/* Navigation - SHOULD BE VISIBLE */}
        <div className="flex justify-between items-center mb-6 p-4 bg-primary rounded-lg">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            icon={<ChevronLeft className="w-5 h-5" />}
            className="bg-white"
          >
            Previous
          </Button>

          {currentIndex === questions.length - 1 ? (
            <Button
              variant="warm"
              onClick={handleSubmit}
              disabled={!allAnswered}
              icon={<CheckCircle className="w-5 h-5" />}
              size="lg"
            >
              Submit All Answers
            </Button>
          ) : (
            <Button
              variant="primary"
              onClick={handleNext}
              icon={<ChevronRight className="w-5 h-5" />}
              className="bg-white text-primary"
            >
              Next Question
            </Button>
          )}
        </div>

        {/* Progress Summary */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">
              {questions.filter((q) => answers.get(q.question_id)?.trim()).length}
            </div>
            <div className="text-sm text-neutral-dark/70">Answered</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-neutral-dark/40 mb-1">
              {questions.length - questions.filter((q) => answers.get(q.question_id)?.trim()).length}
            </div>
            <div className="text-sm text-neutral-dark/70">Remaining</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-secondary mb-1">
              {questions.length}
            </div>
            <div className="text-sm text-neutral-dark/70">Total</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-warm-accent mb-1">
              {Math.round(progress)}%
            </div>
            <div className="text-sm text-neutral-dark/70">Complete</div>
          </Card>
        </div>
      </div>
    </div>
  );
};
