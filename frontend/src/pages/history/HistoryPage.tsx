import { useEffect, useState } from 'react';
import { getEvents } from '../../services/api';
import { DatabaseEvent } from '../../types';
import { Button } from '../../components/Button/Button';
import './history.css';

const TABLE_LABELS: Record<string, string> = {
  train_arrivals: 'Прибытие',
  train_departures: 'Отправление',
  evacuations: 'Эвакуация',
  waiting_room: 'Зал ожидания',
};

const FIELD_LABELS: Record<string, string> = {
  date: 'Дата',
  time: 'Время',
  train_number: 'Номер поезда',
  platform: 'Путь',
  delay_minutes: 'Задержка (мин)',
  notes: 'Примечания',
  start_time: 'Начало',
  end_time: 'Конец',
  reason: 'Причина',
  visitors: 'Посетителей',
  tea_cups: 'Чашек чая',
  water_glasses: 'Стаканов воды',
  temperature: 'Температура (°C)',
};

export function HistoryPage() {
  const [events, setEvents] = useState<DatabaseEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEvents();
      setEvents(data.events);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const formatDate = (value: unknown): string => {
    if (value === null || value === undefined || value === '') return '';
    if (typeof value === 'string') {
      // Date-only format: "2026-07-18" → "18.07.2026"
      if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        const parts = value.split('-');
        return `${parts[2]}.${parts[1]}.${parts[0]}`;
      }
      // DateTime with timezone → format nicely if valid date
      if (value.length > 10) {
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
          return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          });
        }
      }
      // Short strings (time like "12:30") — return as-is
      return value;
    }
    if (typeof value === 'number') return String(value);
    return String(value);
  };

  const formatValue = (value: unknown): string => {
    if (value === null || value === undefined || value === '') return '';
    return formatDate(value);
  };

  const ignoreKeys = new Set(['id', '__table__', 'created_at']);

  return (
    <div className="page">
      <div className="history-header">
        <h2>История событий</h2>
        <Button onClick={refresh} disabled={loading}>
          {loading ? 'Загрузка...' : 'Обновить'}
        </Button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading && events.length === 0 && <div className="loading">Загрузка...</div>}

      {!loading && events.length === 0 && (
        <div className="empty">Событий пока нет</div>
      )}

      <div className="event-history">
        <table className="history-table">
          <thead>
            <tr>
              <th>Время</th>
              <th>Тип</th>
              <th>Данные</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <tr key={`${event.__table__}-${event.id}`}>
                <td>{formatDate(event.created_at)}</td>
                <td>
                  <span className={`badge badge-${event.__table__}`}>
                    {TABLE_LABELS[event.__table__] || event.__table__}
                  </span>
                </td>
                <td>
                  {Object.entries(event)
                    .filter(([key]) => !ignoreKeys.has(key))
                    .filter(([, value]) => value !== null && value !== undefined && value !== '')
                    .map(([key, value]) => {
                      const formatted = formatValue(value);
                      if (!formatted) return null;
                      const label = FIELD_LABELS[key] || key;
                      return (
                        <span key={key} className="field">
                          <strong>{label}</strong>: {formatted}{' '}
                        </span>
                      );
                    })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}