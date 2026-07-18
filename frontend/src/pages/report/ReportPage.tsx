import { useState, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { Button } from '../../components/Button/Button';
import { generateReportStream } from '../../services/api';
import './report.css';

const STEPS = [
  { key: 'collecting_data', label: 'Сбор данных из базы' },
  { key: 'building_prompt', label: 'Формирование промпта' },
  { key: 'calling_ollama', label: 'Отправка запроса в Ollama' },
  { key: 'receiving_response', label: 'Получение Markdown от модели' },
  { key: 'saving_file', label: 'Сохранение файла' },
  { key: 'done', label: 'Готово!' },
];

type StepStatus = 'pending' | 'active' | 'done';

interface StepState {
  key: string;
  label: string;
  status: StepStatus;
}

export function ReportPage() {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<StepState[]>(
    STEPS.map((s) => ({ ...s, status: 'pending' })),
  );
  const [partialMarkdown, setPartialMarkdown] = useState<string>('');

  const updateStep = useCallback((stepKey: string) => {
    setSteps((prev) =>
      prev.map((s) => ({
        ...s,
        status: s.key === stepKey ? 'active' : s.status === 'active' ? 'done' : s.status,
      })),
    );
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setContent('');
    setPartialMarkdown('');
    setSteps(STEPS.map((s) => ({ ...s, status: 'pending' as StepStatus })));

    try {
      await generateReportStream((event) => {
        if (event.step === 'error') {
          setError(event.message);
          setLoading(false);
          return;
        }

        updateStep(event.step);

        // Accumulate partial markdown during receiving_response step
        if (event.step === 'receiving_response' && event.content) {
          setPartialMarkdown(event.content);
        }

        if (event.step === 'done' && event.content) {
          setContent(event.content);
          setPartialMarkdown('');
          // Mark all remaining as done
          setSteps((prev) => prev.map((s) => ({ ...s, status: 'done' as StepStatus })));
          setLoading(false);
        }
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка генерации отчёта');
      setLoading(false);
    }
  };

  const getStepIcon = (status: StepStatus) => {
    switch (status) {
      case 'active': return '⏳';
      case 'done': return '✅';
      default: return '○';
    }
  };

  return (
    <div className="page">
      <div className="report-header">
        <h2>Отчёт</h2>
        <Button onClick={handleGenerate} disabled={loading}>
          {loading ? 'Генерация...' : 'Сформировать отчёт'}
        </Button>
      </div>

      {error && <div className="error">{error}</div>}

      {/* Progress Steps — only visible while actively generating */}
      {loading && !content && (
        <div className="progress-panel">
          <h3>Прогресс</h3>
          <ul className="progress-list">
            {steps.map((step) => (
              <li key={step.key} className={`progress-step ${step.status}`}>
                <span className="step-icon">{getStepIcon(step.status)}</span>
                <span className="step-label">{step.label}</span>
                {step.status === 'active' && <span className="step-spinner" />}
              </li>
            ))}
          </ul>

          {/* Live Markdown Preview */}
          {partialMarkdown && (
            <div className="markdown-live-preview">
              <ReactMarkdown children={partialMarkdown} />
            </div>
          )}
        </div>
      )}

      {!loading && !error && !content && (
        <div className="empty">Нажмите кнопку для генерации отчёта</div>
      )}

      {content && (
        <div className="report-content">
          <ReactMarkdown children={content} />
        </div>
      )}
    </div>
  );
}