import { useState } from 'react';
import '../styles/QuestionnaireForm.css';

const QUESTIONS = [
  { id: 'Q1', text: 'I believe my actions can positively influence my academic outcomes.', dimension: 'Control' },
  { id: 'Q2', text: 'I recover quickly after experiencing disappointment in my studies.', dimension: 'Ownership' },
  { id: 'Q3', text: 'I remain motivated even when results are not immediately visible.', dimension: 'Reach' },
  { id: 'Q4', text: 'Academic failures do not define my overall ability as a student.', dimension: 'Endurance' },
  { id: 'Q5', text: 'I reflect on my mistakes and use them to perform better next time.', dimension: 'Control' },
  { id: 'Q6', text: 'Even under pressure, I feel I have control over how I respond to academic challenges.', dimension: 'Ownership' },
  { id: 'Q7', text: 'I believe most academic problems are temporary and can be resolved with effort.', dimension: 'Reach' },
  { id: 'Q8', text: 'A setback in one subject does not affect my confidence in other subjects.', dimension: 'Endurance' },
  { id: 'Q9', text: 'I take responsibility for improving my situation when things go wrong in my studies.', dimension: 'Control' },
  { id: 'Q10', text: 'When I face academic difficulties, I believe I can find a way to overcome them.', dimension: 'Endurance' },
];

const SCALE_LABELS = {
  1: 'Strongly Disagree',
  2: 'Disagree',
  3: 'Neutral',
  4: 'Agree',
  5: 'Strongly Agree',
};

function QuestionnaireForm({ onSubmit, isLoading }) {
  const [answers, setAnswers] = useState(() => {
    const initial = {};
    QUESTIONS.forEach(q => { initial[q.id] = null; });
    return initial;
  });
  const [showValidation, setShowValidation] = useState(false);

  const answeredCount = Object.values(answers).filter(v => v !== null).length;
  const totalQuestions = QUESTIONS.length;
  const completionPercent = Math.round((answeredCount / totalQuestions) * 100);
  const allAnswered = answeredCount === totalQuestions;

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!allAnswered) {
      setShowValidation(true);
      // Scroll to first unanswered question
      const firstUnanswered = QUESTIONS.find(q => answers[q.id] === null);
      if (firstUnanswered) {
        const el = document.getElementById(`question-${firstUnanswered.id}`);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }
    onSubmit(answers);
  };

  return (
    <div className="questionnaire">
      <div className="questionnaire-header">
        <h2>AQ Assessment Questionnaire</h2>
        <p>Rate each statement based on how much you agree with it in your academic life.</p>
      </div>

      {/* Progress Bar */}
      <div className="progress-section">
        <div className="progress-info">
          <span>{answeredCount}/{totalQuestions} questions answered</span>
          <span className="progress-percentage">{completionPercent}%</span>
        </div>
        <div className="progress-track">
          <div
            className="progress-fill"
            style={{ width: `${completionPercent}%` }}
          ></div>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="questions-list">
          {QUESTIONS.map((question, index) => {
            const isAnswered = answers[question.id] !== null;
            const isUnanswered = showValidation && !isAnswered;

            return (
              <div
                key={question.id}
                id={`question-${question.id}`}
                className={`question-card${isAnswered ? ' answered' : ''}${isUnanswered ? ' unanswered' : ''}`}
              >
                <div className="question-header">
                  <span className="question-number">{index + 1}</span>
                </div>

                <p className="question-text">{question.text}</p>

                <div className="likert-scale" role="radiogroup" aria-label={`Question ${index + 1}`}>
                  {[1, 2, 3, 4, 5].map(value => (
                    <label
                      key={value}
                      className={`likert-option${answers[question.id] === value ? ' selected' : ''}`}
                    >
                      <input
                        type="radio"
                        name={question.id}
                        value={value}
                        checked={answers[question.id] === value}
                        onChange={() => handleAnswer(question.id, value)}
                      />
                      <span className="likert-circle">{value}</span>
                      <span className="likert-label">{SCALE_LABELS[value]}</span>
                    </label>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Submit Section */}
        <div className="submit-section">
          <button
            type="submit"
            className="submit-btn"
            disabled={!allAnswered || isLoading}
          >
            {isLoading ? '⏳ Analyzing...' : '🔍 Get My AQ Analysis'}
          </button>
          {!allAnswered && (
            <p className="submit-hint">
              Please answer all {totalQuestions} questions to continue
            </p>
          )}
        </div>
      </form>
    </div>
  );
}

export default QuestionnaireForm;
