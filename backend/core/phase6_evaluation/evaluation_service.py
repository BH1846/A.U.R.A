"""
Phase 6: Automated Evaluation System
Score candidate answers across multiple dimensions
"""
from typing import List, Dict
from pydantic import BaseModel
from groq import Groq
from loguru import logger
from config import settings
import json


class DimensionalScore(BaseModel):
    """Score for each evaluation dimension"""
    concept_understanding: float  # 0-10
    technical_depth: float  # 0-10
    accuracy: float  # 0-10
    communication: float  # 0-10
    relevance: float  # 0-10


class QuestionEvaluation(BaseModel):
    """Evaluation result for a single question"""
    question_id: int
    scores: DimensionalScore
    weighted_score: float  # 0-100
    feedback: str
    strengths: List[str]
    weaknesses: List[str]
    fraud_flag: bool = False
    fraud_reason: str = ""


class EvaluationService:
    """Service for evaluating candidate answers"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.MODEL_NAME
    
    def evaluate_answer(
        self,
        question: str,
        question_type: str,
        expected_keywords: List[str],
        candidate_answer: str,
        code_context: str,
        project_summary: str
    ) -> DimensionalScore:
        """Evaluate a single answer using LLM"""
        
        prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

## Question:
**Type**: {question_type}
**Question**: {question}

## Expected Keywords/Concepts:
{', '.join(expected_keywords)}

## Candidate's Answer:
{candidate_answer}

## Project Context:
{code_context[:1000]}

{project_summary[:500]}

## Evaluation Task:
Score the answer on these dimensions (0-10 scale):

1. **Concept Understanding** (0-10): Does the candidate understand the core concepts?
2. **Technical Depth** (0-10): Is the technical explanation detailed and accurate?
3. **Accuracy** (0-10): Is the answer factually correct based on the code?
4. **Communication** (0-10): Is the explanation clear and well-articulated?
5. **Relevance** (0-10): Does the answer address the question directly?

## Scoring Guidelines:
- 0-3: Poor/Incorrect
- 4-6: Adequate/Partial
- 7-8: Good/Complete
- 9-10: Excellent/Exceptional

Return JSON with:
- concept_understanding
- technical_depth
- accuracy
- communication
- relevance
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical evaluator. Return ONLY valid JSON with no markdown or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            if content.startswith("```"):
                # Remove markdown code blocks
                content = content.split("```json")[-1] if "```json" in content else content.split("```")[-1]
                content = content.split("```")[0].strip()
            
            result = json.loads(content)
            return DimensionalScore(**result)
            
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")
            logger.debug(f"Response content: {response.choices[0].message.content if 'response' in locals() else 'N/A'}")
            # Return neutral scores
            return DimensionalScore(
                concept_understanding=5.0,
                technical_depth=5.0,
                accuracy=5.0,
                communication=5.0,
                relevance=5.0
            )
    
    def generate_feedback(
        self,
        question: str,
        answer: str,
        scores: DimensionalScore
    ) -> tuple[str, List[str], List[str]]:
        """Generate detailed feedback, strengths, and weaknesses"""
        
        prompt = f"""Based on this Q&A and scores, provide constructive feedback.

Question: {question}
Answer: {answer}

Scores:
- Concept Understanding: {scores.concept_understanding}/10
- Technical Depth: {scores.technical_depth}/10
- Accuracy: {scores.accuracy}/10
- Communication: {scores.communication}/10
- Relevance: {scores.relevance}/10

Provide:
1. Brief feedback (2-3 sentences)
2. Strengths (2-3 points)
3. Weaknesses (2-3 points)

Return JSON with:
- feedback (string)
- strengths (array)
- weaknesses (array)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a constructive technical mentor. Return ONLY valid JSON with no markdown or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            if "```" in content:
                # Remove markdown code block markers
                content = content.replace("```json", "").replace("```", "").strip()
            
            result = json.loads(content)
            return (
                result.get('feedback', 'Good effort'),
                result.get('strengths', ['Shows understanding']),
                result.get('weaknesses', ['Could provide more detail'])
            )
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            logger.debug(f"Response content: {response.choices[0].message.content if 'response' in locals() else 'N/A'}")
            return ("Good effort on this question.", ["Shows understanding"], ["Could elaborate more"])
    
    def calculate_weighted_score(self, scores: DimensionalScore) -> float:
        """Calculate weighted score based on configured weights"""
        weighted = (
            scores.concept_understanding * settings.WEIGHT_UNDERSTANDING +
            scores.technical_depth * settings.WEIGHT_REASONING +
            scores.communication * settings.WEIGHT_COMMUNICATION +
            scores.accuracy * settings.WEIGHT_LOGIC +
            scores.relevance * 0.1  # Small weight for relevance
        )
        
        # Normalize to 0-100
        return (weighted / 10) * 100
    
    def detect_fraud(
        self,
        answer: str,
        code_context: str,
        question: str
    ) -> tuple[bool, str]:
        """Detect potential fraud signals"""
        
        # Check for generic/copy-paste answers
        generic_phrases = [
            "i don't know",
            "not sure",
            "can't remember",
            "didn't implement",
            "copied from",
            "found online"
        ]
        
        answer_lower = answer.lower()
        for phrase in generic_phrases:
            if phrase in answer_lower:
                return True, f"Generic response detected: '{phrase}'"
        
        # Check answer length
        if len(answer.strip()) < 20:
            return True, "Answer too short (< 20 characters)"
        
        # Use LLM for sophisticated fraud detection
        prompt = f"""Detect if this answer seems fraudulent or inconsistent.

Question: {question}
Answer: {answer}
Code Context: {code_context[:500]}

Check for:
1. Answer completely unrelated to project
2. Generic/template responses
3. Contradictions with code
4. Copied text patterns

Return JSON:
- is_fraud (boolean)
- reason (string, empty if not fraud)
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fraud detection system. Return ONLY valid JSON with no markdown or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON if wrapped in markdown code blocks
            if content.startswith("```"):
                content = content.split("```json")[-1] if "```json" in content else content.split("```")[-1]
                content = content.split("```")[0].strip()
            
            result = json.loads(content)
            return result.get('is_fraud', False), result.get('reason', '')
            
        except:
            return False, ""


class OverallEvaluator:
    """Calculate overall evaluation metrics"""
    
    @staticmethod
    def calculate_overall_score(question_evaluations: List[QuestionEvaluation]) -> Dict:
        """Calculate overall score and breakdown"""
        
        if not question_evaluations:
            return {
                'overall_score': 0,
                'understanding_score': 0,
                'reasoning_score': 0,
                'communication_score': 0,
                'logic_score': 0
            }
        
        # Average dimensional scores
        total_understanding = sum(e.scores.concept_understanding for e in question_evaluations)
        total_reasoning = sum(e.scores.technical_depth for e in question_evaluations)
        total_communication = sum(e.scores.communication for e in question_evaluations)
        total_logic = sum(e.scores.accuracy for e in question_evaluations)
        
        n = len(question_evaluations)
        
        understanding_score = (total_understanding / n) * 10
        reasoning_score = (total_reasoning / n) * 10
        communication_score = (total_communication / n) * 10
        logic_score = (total_logic / n) * 10
        
        # Calculate weighted overall score
        overall_score = (
            understanding_score * settings.WEIGHT_UNDERSTANDING +
            reasoning_score * settings.WEIGHT_REASONING +
            communication_score * settings.WEIGHT_COMMUNICATION +
            logic_score * settings.WEIGHT_LOGIC
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'understanding_score': round(understanding_score, 2),
            'reasoning_score': round(reasoning_score, 2),
            'communication_score': round(communication_score, 2),
            'logic_score': round(logic_score, 2)
        }
    
    @staticmethod
    def generate_recommendation(overall_score: float) -> tuple[str, float]:
        """Generate hiring recommendation"""
        
        if overall_score >= 85:
            return "strong_yes", 0.95
        elif overall_score >= 75:
            return "yes", 0.80
        elif overall_score >= 60:
            return "maybe", 0.60
        elif overall_score >= 40:
            return "no", 0.30
        else:
            return "strong_no", 0.10


# Service instance
evaluation_service = EvaluationService()
