import { useState, FormEvent, useEffect, useRef } from 'react';
import { submitEvent, getTaskStatus } from '../../services/api';
import { TaskState } from '../../types';
import { StatusMessage } from '../../components/StatusMessage/StatusMessage';
import { Button } from '../../components/Button/Button';
import { TextArea } from '../../components/TextArea/TextArea';
import './input.css';

type StatusType = 'idle' | 'loading' | 'success' | 'error';

const PROCESS_STEPS = [
  { key: 'pending', label: 'Задача создана', icon: '○' },
  { key: 'processing', label: 'Подготовка данных', icon: '⏳' },
  { key: 'classifying', label: 'Анализ через AI (Ollama)', icon: '🤖' },
  { key: 'saving', label: 'Сохранение в базу', icon: '💾' },
];

function getStepIndex(state: TaskState | undefined): number {
  const order: Record<string, number> = {
    pending: 0,
    processing: 1,
    classifying: 2,
    saving: 3,
    completed: 4,
    failed: -1,
  };
  return state ? (order[state] ?? -1) : -1;
}

export function InputPage() {
  const [text, setText] = useState('');
  const [status, setStatus] = useState<StatusType>('idle');
  const [message, setMessage] = useState('');
  const [taskState, setTaskState] = useState<TaskState | null>(null);
  const [currentStep, setCurrentStep] = useState('');
  const pollRef = useRef<number | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  const startPolling = async (taskId: string) => {
    pollRef.current = window.setInterval(async () => {
      try {
        const task = await getTaskStatus(taskId);

        setTaskState(task.status);
        setCurrentStep(task.step || '');

        if (task.status === 'completed') {
          stopPolling();
          setStatus('success');
          setMessage(
            task.result
              ? `${task.result.message} (${task.result.count} событий)`
              : 'Готово',
          );
          setText('');
          setTaskState(null);
        } else if (task.status === 'failed') {
          stopPolling();
          setStatus('error');
          setMessage(task.error || 'Ошибка обработки');
          setTaskState(null);
        }
      } catch {
        // Ignore polling errors, keep trying
      }
    }, 500);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setStatus('loading');
    setMessage('');
    setTaskState('pending');
    setCurrentStep('Отправка запроса...');

    try {
      const { task_id } = await submitEvent(text.trim());
      startPolling(task_id);
    } catch (err) {
      stopPolling();
      setStatus('error');
      setMessage(err instanceof Error ? err.message : 'Произошла ошибка');
      setTaskState(null);
    }
  };

  const currentStepIndex = getStepIndex(taskState || undefined);

  return (
    <div className="page">
      <h2>Добавить событие</h2>
      <form className="event-input" onSubmit={handleSubmit}>
        <TextArea
          value={text}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setText(e.target.value)}
          placeholder="Опишите событие, например: Поезд №742 прибыл на 3 путь в 12:43 с задержкой 15 минут."
          disabled={status === 'loading'}
          rows={4}
        />
        <Button type="submit" disabled={status === 'loading' || !text.trim()}>
          {status === 'loading' ? 'Отправлено — обработка...' : 'Добавить'}
        </Button>

        {/* Processing steps */}
        {status === 'loading' && (
          <div className="process-steps">
            {PROCESS_STEPS.map((step, idx) => {
              const isActive = idx === currentStepIndex;
              const isDone = idx < currentStepIndex;
              return (
                <div
                  key={step.key}
                  className={`process-step ${isActive ? 'active' : ''} ${isDone ? 'done' : ''}`}
                >
                  <span className="step-icon">{isDone ? '✅' : isActive ? step.icon : '○'}</span>
                  <span className="step-label">
                    {step.label}
                    {isActive && currentStep ? ` — ${currentStep}` : ''}
                  </span>
                </div>
              );
            })}
          </div>
        )}

        <StatusMessage status={status} message={message} />
      </form>
    </div>
  );
}