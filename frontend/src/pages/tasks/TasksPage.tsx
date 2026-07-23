import { useEffect, useState, useCallback } from 'react';
import { Button } from '../../components/Button/Button';
import { listTasks, cancelTask, retryTask } from '../../services/api';
import type { QueueTask } from '../../types';
import './tasks.css';

const STATUS_LABELS: Record<string, string> = {
  pending: 'В очереди',
  processing: 'Обработка',
  classifying: 'Классификация',
  saving: 'Сохранение',
  completed: 'Завершена',
  failed: 'Ошибка',
  cancelled: 'Отменена',
};

const STATUS_ICONS: Record<string, string> = {
  pending: '⏳',
  processing: '🔄',
  classifying: '🤖',
  saving: '💾',
  completed: '✅',
  failed: '❌',
  cancelled: '🚫',
};

export function TasksPage() {
  const [tasks, setTasks] = useState<QueueTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listTasks();
      setTasks(data.tasks);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 2000);
    return () => clearInterval(interval);
  }, [refresh]);

  const handleCancel = async (id: string) => {
    try {
      await cancelTask(id);
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка');
    }
  };

  const handleRetry = async (id: string) => {
    try {
      await retryTask(id);
      refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка');
    }
  };

  return (
    <div className="page">
      <div className="tasks-header">
        <h2>Очередь задач</h2>
        <Button onClick={refresh} disabled={loading}>
          Обновить
        </Button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading && tasks.length === 0 ? (
        <div className="empty">Загрузка...</div>
      ) : tasks.length === 0 ? (
        <div className="empty">Очередь пуста</div>
      ) : (
        <table className="tasks-table">
          <thead>
            <tr>
              <th>Статус</th>
              <th>Этап</th>
              <th>Текст</th>
              <th>Время</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} className={`task-row status-${task.status}`}>
                <td className="status-cell">
                  <span className="status-icon">{STATUS_ICONS[task.status] || '?'}</span>
                  <span>{STATUS_LABELS[task.status] || task.status}</span>
                  {task.error && <span className="error-hint">{task.error.slice(0, 60)}...</span>}
                </td>
                <td className="step-cell">{task.step || '—'}</td>
                <td className="text-cell" title={task.input_text}>
                  {task.input_text}
                </td>
                <td className="time-cell">
                  {new Date(task.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </td>
                <td className="actions-cell">
                  {(task.status === 'pending' || task.status === 'processing' || task.status === 'classifying' || task.status === 'saving') && (
                    <Button size="sm" onClick={() => handleCancel(task.id)}>
                      Отменить
                    </Button>
                  )}
                  {(task.status === 'failed' || task.status === 'cancelled') && (
                    <Button size="sm" variant="secondary" onClick={() => handleRetry(task.id)}>
                      Повторить
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}