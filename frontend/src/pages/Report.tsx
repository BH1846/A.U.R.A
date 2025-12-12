import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { LoadingScreen } from '../components/ui/Spinner';
import api from '../services/api';
import type { EvaluationReport } from '../types';
import { getScoreColor } from '../styles/theme';
import { formatScore } from '../utils/formatters';
import { Download, AlertTriangle, TrendingUp, TrendingDown, CheckCircle, Code2 } from 'lucide-react';

export const Report: React.FC = () => {
  const { candidateId } = useParams<{ candidateId: string }>();
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      if (!candidateId) return;
      
      try {
        console.log('Fetching report for candidate:', candidateId);
        const data = await api.getReport(parseInt(candidateId));
        console.log('Report data received:', data);
        setReport(data);
      } catch (error: any) {
        console.error('Failed to fetch report:', error);
        console.error('Error details:', error.response?.data);
        alert(`Failed to load report: ${error.response?.data?.detail || error.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [candidateId]);

  const handleDownload = async () => {
    if (!candidateId) return;
    
    try {
      const blob = await api.downloadReport(parseInt(candidateId));
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AURA_Report_${report?.candidate.name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  if (loading) {
    return <LoadingScreen message="Loading evaluation report..." />;
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-neutral-light flex items-center justify-center">
        <Card className="max-w-md text-center p-8">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Report Not Found</h2>
          <p className="text-neutral-dark/70">
            The evaluation report could not be loaded.
          </p>
        </Card>
      </div>
    );
  }

  const { final_score } = report;
  const scoreColor = getScoreColor(final_score.overall_score);

  return (
    <div className="min-h-screen bg-neutral-light py-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="gradient-primary text-white rounded-2xl p-8 mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">{report.candidate.name}</h1>
              <p className="text-white/80 text-lg mb-4">{report.candidate.email}</p>
              <div className="flex gap-3">
                <Badge variant="warm" className="text-sm">
                  {report.candidate.role_type}
                </Badge>
                <Badge variant="secondary" className="text-sm">
                  {report.repository.name}
                </Badge>
              </div>
            </div>
            <Button
              variant="warm"
              icon={<Download className="w-5 h-5" />}
              onClick={handleDownload}
            >
              Download PDF
            </Button>
          </div>
        </div>

        {/* Overall Score */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card variant="elevated" className="md:col-span-1">
            <div className="text-center">
              <div className="relative inline-block">
                <svg className="w-32 h-32">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="#B3EDEB"
                    strokeWidth="8"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke={scoreColor}
                    strokeWidth="8"
                    strokeDasharray={`${(final_score.overall_score / 100) * 352} 352`}
                    strokeLinecap="round"
                    transform="rotate(-90 64 64)"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-3xl font-bold" style={{ color: scoreColor }}>
                    {formatScore(final_score.overall_score)}
                  </span>
                </div>
              </div>
              <h3 className="text-xl font-semibold mt-4 text-neutral-dark">
                Overall Score
              </h3>
              <Badge
                variant={final_score.overall_score >= 70 ? 'success' : 'neutral'}
                className="mt-2"
              >
                {final_score.hire_recommendation}
              </Badge>
            </div>
          </Card>

          {/* Dimensional Scores */}
          <Card variant="elevated" className="md:col-span-2">
            <h3 className="text-lg font-semibold mb-4 text-neutral-dark">
              Dimensional Breakdown
            </h3>
            <div className="space-y-4">
              {[
                { label: 'Understanding', value: final_score.understanding_score, color: '#1F7368' },
                { label: 'Reasoning', value: final_score.reasoning_score, color: '#63D7C7' },
                { label: 'Communication', value: final_score.communication_score, color: '#004F4D' },
                { label: 'Logic', value: final_score.logic_score, color: '#B3EDEB' },
              ].map((dimension) => (
                <div key={dimension.label}>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-neutral-dark">
                      {dimension.label}
                    </span>
                    <span className="text-sm font-bold" style={{ color: dimension.color }}>
                      {formatScore(dimension.value)}/100
                    </span>
                  </div>
                  <div className="w-full bg-soft-accent rounded-full h-2">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${dimension.value}%`,
                        backgroundColor: dimension.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card variant="elevated">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
              <h3 className="text-xl font-semibold text-neutral-dark">Strengths</h3>
            </div>
            <ul className="space-y-2">
              {report.question_scores
                .flatMap(s => s.strengths || [])
                .filter((s, i, arr) => arr.indexOf(s) === i)
                .slice(0, 5)
                .map((strength, index) => (
                  <li key={index} className="flex gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span className="text-neutral-dark/80">{strength}</span>
                  </li>
                ))}
              {report.question_scores.flatMap(s => s.strengths || []).length === 0 && (
                <li className="text-neutral-dark/60">No specific strengths identified</li>
              )}
            </ul>
          </Card>

          <Card variant="elevated">
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="w-6 h-6 text-orange-600" />
              <h3 className="text-xl font-semibold text-neutral-dark">Areas for Improvement</h3>
            </div>
            <ul className="space-y-2">
              {report.question_scores
                .flatMap(s => s.weaknesses || [])
                .filter((w, i, arr) => arr.indexOf(w) === i)
                .slice(0, 5)
                .map((weakness, index) => (
                  <li key={index} className="flex gap-2">
                    <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                    <span className="text-neutral-dark/80">{weakness}</span>
                  </li>
                ))}
              {report.question_scores.flatMap(s => s.weaknesses || []).length === 0 && (
                <li className="text-neutral-dark/60">No specific weaknesses identified</li>
              )}
            </ul>
          </Card>
        </div>

        {/* Repository Info */}
        <Card variant="elevated" className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Code2 className="w-6 h-6 text-primary" />
            <h3 className="text-xl font-semibold text-neutral-dark">Repository Analysis</h3>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm font-medium text-neutral-dark/70 mb-2">Tech Stack</p>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(report.repository.tech_stack) && report.repository.tech_stack.length > 0 ? (
                  report.repository.tech_stack.map((tech) => (
                    <Badge key={tech} variant="primary" size="sm">
                      {tech}
                    </Badge>
                  ))
                ) : (
                  <span className="text-neutral-dark/60 text-sm">No tech stack data available</span>
                )}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-neutral-dark/70 mb-2">Languages</p>
              <div className="flex flex-wrap gap-2">
                {Array.isArray(report.repository.languages) && report.repository.languages.length > 0 ? (
                  report.repository.languages.map((lang) => (
                    <Badge key={lang} variant="secondary" size="sm">
                      {lang}
                    </Badge>
                  ))
                ) : (
                  <span className="text-neutral-dark/60 text-sm">No language data available</span>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
