import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Github, Zap, CheckCircle, TrendingUp, ArrowRight, Code2, Brain, FileCheck } from 'lucide-react';

export const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-neutral-light">
      {/* Hero Section */}
      <section className="gradient-primary text-white py-20 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <div className="inline-block mb-6">
            <Code2 className="w-16 h-16 mx-auto text-warm-accent" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            AURA Assessment Platform
          </h1>
          <p className="text-xl md:text-2xl mb-4 text-white/90">
            Advanced Understanding & Responsive Agent
          </p>
          <p className="text-lg mb-8 text-white/80 max-w-3xl mx-auto">
            AI-powered skill verification that evaluates candidates based on their actual GitHub repositories.
            No more generic interviews - assess real code, real projects, real understanding.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Button
              variant="warm"
              size="lg"
              icon={<ArrowRight className="w-5 h-5" />}
              onClick={() => navigate('/submit')}
            >
              Start Assessment
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="bg-white/10 border-white text-white hover:bg-white hover:text-primary"
              onClick={() => navigate('/dashboard')}
            >
              Recruiter Dashboard
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-neutral-dark">
            How AURA Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Card variant="elevated" className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                <Github className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-neutral-dark">
                1. Submit Repository
              </h3>
              <p className="text-neutral-dark/70">
                Candidates submit their GitHub repository. AURA analyzes the code, tech stack, and project structure automatically.
              </p>
            </Card>

            <Card variant="elevated" className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-secondary/10 flex items-center justify-center">
                <Brain className="w-8 h-8 text-secondary" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-neutral-dark">
                2. AI-Generated Questions
              </h3>
              <p className="text-neutral-dark/70">
                Our AI generates personalized interview questions based on the actual codebase, ensuring relevance and depth.
              </p>
            </Card>

            <Card variant="elevated" className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-warm-accent/20 flex items-center justify-center">
                <FileCheck className="w-8 h-8 text-warm-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-neutral-dark">
                3. Automated Evaluation
              </h3>
              <p className="text-neutral-dark/70">
                Answers are evaluated across 5 dimensions: Understanding, Technical Depth, Accuracy, Communication, and Relevance.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-soft-accent/30 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-neutral-dark">
            Why Choose AURA?
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                icon: <Zap className="w-6 h-6" />,
                title: 'Fast & Efficient',
                description: 'Complete assessments in minutes, not hours. Automated analysis saves time for both recruiters and candidates.',
              },
              {
                icon: <CheckCircle className="w-6 h-6" />,
                title: 'Fair & Objective',
                description: 'AI-driven evaluation eliminates bias and ensures consistent, objective assessment across all candidates.',
              },
              {
                icon: <TrendingUp className="w-6 h-6" />,
                title: 'Deep Technical Insights',
                description: 'Go beyond resumes with detailed analysis of coding patterns, architecture decisions, and technical depth.',
              },
              {
                icon: <Code2 className="w-6 h-6" />,
                title: 'Real Code Assessment',
                description: 'Evaluate actual projects, not theoretical knowledge. See how candidates solve real problems.',
              },
            ].map((benefit, index) => (
              <Card key={index} className="flex gap-4">
                <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                  {benefit.icon}
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2 text-neutral-dark">
                    {benefit.title}
                  </h3>
                  <p className="text-neutral-dark/70 text-sm">{benefit.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <Card variant="elevated" padding="lg" className="gradient-secondary">
            <h2 className="text-3xl font-bold mb-4 text-neutral-dark">
              Ready to Get Started?
            </h2>
            <p className="text-lg mb-8 text-neutral-dark/80">
              Submit your GitHub repository and let AURA assess your skills in minutes.
            </p>
            <Button
              variant="primary"
              size="lg"
              icon={<ArrowRight className="w-5 h-5" />}
              onClick={() => navigate('/submit')}
            >
              Start Your Assessment Now
            </Button>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-tertiary text-white py-12 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <div className="mb-4">
            <Code2 className="w-10 h-10 mx-auto mb-2 text-warm-accent" />
            <h3 className="text-xl font-bold">AURA</h3>
            <p className="text-white/60">Automated Understanding & Role Assessment</p>
          </div>
          <p className="text-white/40 text-sm">
            © 2025 AURA. AI-powered skill verification for modern recruiting.
          </p>
        </div>
      </footer>
    </div>
  );
};
