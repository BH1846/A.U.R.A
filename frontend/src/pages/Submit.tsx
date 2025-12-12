import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { candidateSchema, type CandidateFormData } from '../services/validation';
import { useCandidateStore } from '../store/candidateStore';
import { User, Mail, Github, Briefcase, ArrowRight, CheckCircle } from 'lucide-react';

export const Submit: React.FC = () => {
  const navigate = useNavigate();
  const submitCandidate = useCandidateStore((state) => state.submitCandidate);
  const [isSuccess, setIsSuccess] = useState(false);
  const [candidateId, setCandidateId] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CandidateFormData>({
    resolver: zodResolver(candidateSchema),
  });

  const onSubmit = async (data: CandidateFormData) => {
    try {
      const id = await submitCandidate(data);
      setCandidateId(id);
      setIsSuccess(true);
      
      // Redirect after 2 seconds
      setTimeout(() => {
        navigate(`/questions/${id}`);
      }, 2000);
    } catch (error) {
      console.error('Submission failed:', error);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen bg-neutral-light flex items-center justify-center px-6">
        <Card variant="elevated" className="max-w-md w-full text-center animation-scale-in">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-warm-accent/20 flex items-center justify-center">
            <CheckCircle className="w-12 h-12 text-warm-accent" />
          </div>
          <h2 className="text-3xl font-bold mb-4 text-neutral-dark">Success!</h2>
          <p className="text-neutral-dark/70 mb-6">
            Your repository is being analyzed. Redirecting to questions...
          </p>
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto" />
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-light py-12 px-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 text-neutral-dark">
            Submit Your Repository
          </h1>
          <p className="text-lg text-neutral-dark/70">
            Start your skill assessment by providing your GitHub repository and basic information.
          </p>
        </div>

        {/* Form Card */}
        <Card variant="elevated" padding="lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Name Input */}
            <Input
              label="Full Name"
              placeholder="John Doe"
              icon={<User className="w-5 h-5" />}
              error={errors.name?.message}
              {...register('name')}
            />

            {/* Email Input */}
            <Input
              label="Email Address"
              type="email"
              placeholder="john@example.com"
              icon={<Mail className="w-5 h-5" />}
              error={errors.email?.message}
              {...register('email')}
            />

            {/* GitHub URL Input */}
            <Input
              label="GitHub Repository URL"
              placeholder="https://github.com/username/repository"
              icon={<Github className="w-5 h-5" />}
              error={errors.github_url?.message}
              {...register('github_url')}
            />

            {/* Role Selection */}
            <Select
              label="Role Type"
              options={[
                { value: '', label: 'Select a role...' },
                { value: 'Frontend', label: 'Frontend Developer' },
                { value: 'Backend', label: 'Backend Developer' },
                { value: 'FullStack', label: 'Full Stack Developer' },
                { value: 'ML', label: 'Machine Learning Engineer' },
                { value: 'DevOps', label: 'DevOps Engineer' },
              ]}
              error={errors.role_type?.message}
              {...register('role_type')}
            />

            {/* Help Text */}
            <div className="bg-soft-accent/50 rounded-xl p-4">
              <p className="text-sm text-neutral-dark/70">
                <strong>Note:</strong> Your repository will be analyzed for code quality, architecture, and technical decisions. 
                Make sure the repository is public and contains meaningful code.
              </p>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isSubmitting}
              icon={<ArrowRight className="w-5 h-5" />}
              className="w-full"
            >
              {isSubmitting ? 'Submitting...' : 'Submit & Start Assessment'}
            </Button>
          </form>
        </Card>

        {/* Info Cards */}
        <div className="grid md:grid-cols-3 gap-4 mt-8">
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-primary mb-1">~5 min</div>
            <div className="text-sm text-neutral-dark/70">Analysis Time</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-secondary mb-1">6-10</div>
            <div className="text-sm text-neutral-dark/70">Questions</div>
          </Card>
          <Card className="text-center p-4">
            <div className="text-2xl font-bold text-warm-accent mb-1">100%</div>
            <div className="text-sm text-neutral-dark/70">Automated</div>
          </Card>
        </div>
      </div>
    </div>
  );
};
